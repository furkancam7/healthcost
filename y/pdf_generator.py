from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
from typing import Optional, List, Dict, Any
from google import genai

client = genai.Client(api_key="AIzaSyBUuxzgwZyi2Dab3dihgbLA3kXzASuw_yw")

def generate_health_cost_report(age: int,
                              gender: str,
                              height: float,
                              weight: float,
                              region: str,
                              chronic_conditions: list,
                              family_history: list,
                              lifestyle_score: int,
                              insurance_status: bool,
                              smoke: bool,
                              alcohol: bool,
                              predicted_cost: float,
                              calculation_details: Optional[list] = None,
                              recommendations: Optional[list] = None,
                              output_dir: str = "reports") -> str:
    """
    Generate a PDF report for health cost prediction.
    
    Args:
        age (int): Age of the person
        gender (str): Gender of the person
        height (float): Height of the person in centimeters
        weight (float): Weight of the person in kilograms
        region (str): Region/country of residence
        chronic_conditions (list): List of chronic conditions
        family_history (list): List of family medical history
        lifestyle_score (int): Lifestyle score (0-10)
        insurance_status (bool): Whether the person has health insurance
        smoke (bool): Whether the person smokes
        alcohol (bool): Whether the person consumes alcohol
        predicted_cost (float): Predicted annual health cost
        calculation_details (list): Detailed calculation steps (optional)
        recommendations (list): User-specific health suggestions (optional)
        output_dir (str): Directory to save the PDF report
        
    Returns:
        str: Path to the generated PDF file
    """
    if calculation_details is None:
        calculation_details = []
    if recommendations is None:
        recommendations = []
    
    # Create reports directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"health_cost_prediction_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )
    
    source_style = ParagraphStyle(
        'SourceStyle',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        spaceBefore=2,
        spaceAfter=6
    )
    
    # Build the content
    content = []
    
    # Title
    content.append(Paragraph("Health Cost Prediction Report", title_style))
    content.append(Spacer(1, 20))
    
    # Personal Information
    content.append(Paragraph("Personal Information", heading_style))
    personal_data = [
        ["Age:", str(age)],
        ["Gender:", gender],
        ["Height (cm):", str(height)],
        ["Weight (kg):", str(weight)],
        ["Region:", region],
        ["Lifestyle Score:", f"{lifestyle_score}/10"],
        ["Insurance Status:", "Yes" if insurance_status else "No"],
        ["Smoking:", "Yes" if smoke else "No"],
        ["Alcohol Consumption:", "Yes" if alcohol else "No"]
    ]
    personal_table = Table(personal_data, colWidths=[2*inch, 4*inch])
    personal_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(personal_table)
    content.append(Spacer(1, 20))
    
    # Health Information
    content.append(Paragraph("Health Information", heading_style))
    health_data = [
        ["Chronic Conditions:", ", ".join(chronic_conditions) if chronic_conditions else "None"],
        ["Family History:", ", ".join(family_history) if family_history else "None"]
    ]
    health_table = Table(health_data, colWidths=[2*inch, 4*inch])
    health_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    content.append(health_table)
    content.append(Spacer(1, 20))
    
    # Prediction Results
    content.append(Paragraph("Prediction Results", heading_style))
    prediction_data = [
        ["Predicted Annual Health Cost:", f"${predicted_cost:,.2f}"]
    ]
    prediction_table = Table(prediction_data, colWidths=[2*inch, 4*inch])
    prediction_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.red),
        ('FONTSIZE', (1, 0), (1, 0), 14),
    ]))
    content.append(prediction_table)
    content.append(Spacer(1, 20))
    
    # Calculation Details Table
    if calculation_details:
        content.append(Paragraph("Calculation Steps", heading_style))
        # Header'ı da Paragraph ile oluştur
        calc_data = [
            [
                Paragraph("Step", styles["Normal"]),
                Paragraph("Description", styles["Normal"]),
                Paragraph("Value", styles["Normal"]),
                Paragraph("Source", source_style)
            ]
        ]
        for d in calculation_details:
            step_para = Paragraph(str(d.get('step', '')), styles["Normal"])
            desc_para = Paragraph(str(d.get('desc', '')), styles["Normal"])
            value_para = Paragraph(f"{d.get('value', 0):,.2f}", styles["Normal"])
            source_para = Paragraph(d.get('source', ''), source_style)
            calc_data.append([
                step_para,
                desc_para,
                value_para,
                source_para
            ])
        calc_table = Table(calc_data, colWidths=[0.9*inch, 2.0*inch, 0.9*inch, 4.0*inch], repeatRows=1)
        calc_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, 0), colors.lightblue),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),  # header
            ('FONTSIZE', (0, 1), (-1, -1), 8),  # body
            ('TEXTCOLOR', (3, 1), (3, -1), colors.gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        content.append(calc_table)
        content.append(Spacer(1, 20))

    # Recommendations Section
    if recommendations:
        content.append(Paragraph("Recommendations", heading_style))
        for rec in recommendations:
            content.append(Paragraph(f"• {rec}", styles["Normal"]))
            # Split recommendation and source
            if "Source:" in rec:
                rec_text, source = rec.split("Source:")
                content.append(Paragraph(rec_text, styles["Normal"]))
                content.append(Paragraph(f"Source: {source}", source_style))
            else:
                content.append(Paragraph(rec, styles["Normal"]))
        content.append(Spacer(1, 16))

    # Disclaimer
    content.append(Paragraph("Disclaimer", heading_style))
    disclaimer = Paragraph(
        "This prediction is based on statistical models and should be used as a general guideline only. "
        "Actual health costs may vary based on individual circumstances and healthcare system changes. "
        "Please consult with healthcare professionals for accurate medical advice.",
        styles["Normal"]
    )
    content.append(disclaimer)
    
    # Add data sources section
    content.append(Spacer(1, 20))
    content.append(Paragraph("Data Sources", heading_style))
    sources = [
        "• World Health Organization (WHO) - Healthcare cost statistics and lifestyle impact data",
        "• Centers for Disease Control and Prevention (CDC) - Chronic condition costs and risk factors",
        "• Organization for Economic Co-operation and Development (OECD) - Regional healthcare costs and insurance data",
        "• American Heart Association - Cardiovascular disease costs and risk factors",
        "• American Cancer Society - Cancer screening and treatment costs",
        "• American Lung Association - Respiratory condition costs",
        "• National Institute of Mental Health - Mental health condition costs",
        "• Arthritis Foundation - Arthritis treatment costs",
        "• National Kidney Foundation - Kidney disease costs",
        "• American Diabetes Association - Diabetes management costs"
    ]
    for source in sources:
        content.append(Paragraph(source, source_style))
    
    # Build the PDF
    doc.build(content)
    
    return filepath 

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
    Generate personalized health recommendations using Gemini with grounding.
    """
    
    try:
        # Prepare the prompt for the LLM
        prompt = f"""Based on the following health information and context, provide personalized health recommendations:

Age: {age}
Region: {region}
Chronic Conditions: {', '.join(chronic_conditions) if chronic_conditions else 'None'}
Family History: {', '.join(family_history) if family_history else 'None'}
Lifestyle Score: {lifestyle_score}/10
Insurance Status: {'Has insurance' if insurance_status else 'No insurance'}

Calculation Details:
{chr(10).join([f"- {detail['step']}: {detail['desc']}" for detail in calculation_details])}



Please provide 3-5 specific, actionable health recommendations based on this information. 
Focus on preventive measures, lifestyle changes, and medical check-ups that would be most beneficial.
Format each recommendation as a separate bullet point."""

        # Call Gemini API using new SDK
        response = client.models.generate_content(
            model='gemini-1.5-pro',
            contents=prompt,
            config={
                'temperature': 0.7,
                'top_p': 0.8,
                'top_k': 40
            }
        )
        
        if response and response.text:
            recommendations = response.text.strip().split('\n')
            return [rec.strip('- ') for rec in recommendations if rec.strip()]
        else:
            return ["Unable to generate recommendations at this time. Please consult with your healthcare provider."]
            
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return ["Unable to generate recommendations at this time. Please consult with your healthcare provider."]
    
    