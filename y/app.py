import gradio as gr
from gradio.interface import Interface
from gradio.components import Number, Dropdown, Textbox, Slider, Checkbox, File
from health_cost_agent import HealthCostPredictorAgent
from load_data import load_costs, load_weights
from pdf_generator import generate_health_cost_report
import os
from google import genai
from typing import List, Dict, Any
import time
from google.api_core import retry

# Initialize Gemini
client = genai.Client(api_key="AIzaSyBUuxzgwZyi2Dab3dihgbLA3kXzASuw_yw")

# Initialize the predictor agent
agent = HealthCostPredictorAgent(load_costs(), load_weights())

def calculate_lifestyle_score(exercise_days, fruit_veg, sleep_hours):
    score = 0
    # Egzersiz
    if exercise_days >= 5:
        score += 3
    elif exercise_days >= 3:
        score += 2
    elif exercise_days >= 1:
        score += 1
    # Sebze/meyve
    if fruit_veg >= 5:
        score += 3
    elif fruit_veg >= 3:
        score += 2
    elif fruit_veg >= 1:
        score += 1
    # Uyku
    if 7 <= sleep_hours <= 9:
        score += 4
    elif 6 <= sleep_hours < 7 or 9 < sleep_hours <= 10:
        score += 2
    else:
        score += 0
    return min(score, 10)

def generate_recommendations(
    age: int,
    region: str,
    chronic_conditions: List[str],
    family_history: List[str],
    lifestyle_score: int,
    insurance_status: bool,
    calculation_details: List[Dict[str, Any]]
) -> List[str]:
    """
    Generate personalized health recommendations using Gemini.
    """
    try:
        # Prepare the prompt for the LLM
        prompt = f"""As a healthcare professional, provide detailed and personalized health recommendations based on the following patient information:

Patient Profile:
- Age: {age} years
- Geographic Region: {region}
- Current Health Status:
  * Chronic Conditions: {', '.join(chronic_conditions) if chronic_conditions else 'None reported'}
  * Family Medical History: {', '.join(family_history) if family_history else 'None reported'}
  * Lifestyle Assessment Score: {lifestyle_score}/10
  * Insurance Coverage: {'Present' if insurance_status else 'Not present'}

Cost Analysis Details:
{chr(10).join([f"- {detail['step']}: {detail['desc']}" for detail in calculation_details])}

Please provide comprehensive health recommendations that include:

1. Preventive Care Measures:
   - Specific screening tests and check-ups recommended for the patient's age and risk factors
   - Vaccination recommendations based on age and region
    
2. Lifestyle Modifications:
   - Diet and nutrition advice
   - Physical activity recommendations
   - Stress management techniques
   - Sleep hygiene practices

3. Risk Management:
   - Specific actions to manage existing chronic conditions
   - Preventive measures for conditions in family history
   - Risk reduction strategies based on lifestyle score

4. Healthcare Access:
   - Insurance optimization recommendations
   - Healthcare provider selection guidance
   - Cost-effective healthcare utilization strategies
Do not repeat any recommendation or heading. Only provide each unique recommendation once.
For each recommendation, if it is based on a specific scientific source or guideline, cite the source in parentheses at the end of the recommendation. If the calculation is based on a risk factor or cost data, mention that it is grounded in scientific/official data as shown in the calculation details.
Please format each recommendation as a clear, actionable bullet point with specific, measurable goals where applicable.
Focus on evidence-based practices and practical, implementable suggestions."""

        # Call Gemini API using new SDK
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40
            }
        )
        
        if response and response.text:
            recommendations = response.text.strip().split('\n')
            # Tekrarları kaldır ve boşları filtrele
            seen = set()
            unique_recommendations = []
            for rec in recommendations:
                clean_rec = rec.strip('- ').strip()
                if clean_rec and clean_rec not in seen:
                    unique_recommendations.append(clean_rec)
                    seen.add(clean_rec)
            return unique_recommendations
        else:
            return ["Unable to generate recommendations at this time. Please consult with your healthcare provider."]
            
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return ["Unable to generate recommendations at this time. Please consult with your healthcare provider."]

def predict_health_cost(age: int, 
                       gender: str,
                       height: float,
                       weight: float,
                       region: str, 
                       chronic_conditions: str, 
                       family_history: str, 
                       smoke: bool,
                       alcohol: bool,
                       exercise_days: int,
                       fruit_veg: int,
                       sleep_hours: int,
                       insurance_status: bool) -> tuple[str, str | None]:
    """
    Predict health costs based on user inputs and generate PDF report.
    """
    try:
        # Process inputs
        conditions = [c.strip() for c in chronic_conditions.split(',') if c.strip()]
        family = [f.strip() for f in family_history.split(',') if f.strip()]
        lifestyle_score = calculate_lifestyle_score(exercise_days, fruit_veg, sleep_hours)
        # Get prediction with details
        result = agent.predict(age, region, conditions, family, lifestyle_score, insurance_status)
        final_cost = result['final_cost']
        details = result['details']
        # Generate recommendations
        recommendations = generate_recommendations(
            age=age,
            region=region,
            chronic_conditions=conditions,
            family_history=family,
            lifestyle_score=lifestyle_score,
            insurance_status=insurance_status,
            calculation_details=details
        )
        # Generate PDF report with details and recommendations
        pdf_path = generate_health_cost_report(
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            region=region,
            chronic_conditions=conditions,
            family_history=family,
            lifestyle_score=lifestyle_score,
            insurance_status=insurance_status,
            smoke=smoke,
            alcohol=alcohol,
            predicted_cost=final_cost,
            calculation_details=details,
            recommendations=recommendations
        )
        # Format output with details and recommendations
        detail_lines = [f"{d['step']}: {d['desc']} (Değer: {d['value']:.2f})" for d in details]
        rec_lines = [f"- {rec}" for rec in recommendations]
        prediction_text = (
            f"Predicted Annual Health Cost: ${final_cost:,.2f}\n\n"
            f"Calculation Steps:\n" + "\n".join(detail_lines) +
            ("\n\nÖneriler:\n" + "\n".join(rec_lines) if rec_lines else "")
        )
        return prediction_text, pdf_path
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return error_message, None

# Create Gradio interface
demo = Interface(
    fn=predict_health_cost,
    inputs=[
        Number(label="Age", minimum=30, maximum=100),
        Dropdown(choices=["Male", "Female", "Other"], label="Gender"),
        Number(label="Height (cm)", minimum=100, maximum=250),
        Number(label="Weight (kg)", minimum=30, maximum=250),
        Dropdown(
            choices=["USA", "Europe", "Asia", "Turkey"],
            label="Region",
            value="Turkey"
        ),
        Textbox(
            label="Chronic Conditions (comma-separated)",
            placeholder="e.g., diabetes, hypertension, asthma"
        ),
        Textbox(
            label="Family History (comma-separated)",
            placeholder="e.g., cancer, heart_disease, diabetes"
        ),
        Checkbox(label="Do you smoke?"),
        Checkbox(label="Do you consume alcohol?"),
        Slider(minimum=0, maximum=7, step=1, label="How many days a week do you exercise at least 30 minutes?", value=3),
        Slider(minimum=0, maximum=10, step=1, label="How many portions of fruit/vegetables do you eat per day?", value=3),
        Slider(minimum=0, maximum=24, step=1, label="How many hours do you sleep per day?", value=7),
        Checkbox(label="Have Health Insurance?", value=True)
    ],
    outputs=[
        Textbox(label="Prediction"),
        File(label="Download PDF Report")
    ],
    title="Health Cost Predictor",
    description="Predict annual health costs based on personal health factors and demographics. Lifestyle score is automatically calculated based on your exercise, nutrition, and sleep habits."
)

if __name__ == "__main__":
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    demo.launch(share=True) 