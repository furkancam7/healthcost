import pandas as pd
import json
from typing import List, Dict, Union, Optional

class HealthCostPredictorAgent:
    def __init__(self, 
                 cost_data: pd.DataFrame, 
                 weights: Dict[str, float],
                 chronic_condition_sources: Optional[Dict[str, str]] = None,
                 family_history_risk: Optional[Dict[str, float]] = None,
                 lifestyle_source: Optional[str] = None,
                 insurance_source: Optional[str] = None,
                 insurance_discount_rate: float = 0.3):
        """
        Initialize the HealthCostPredictorAgent.
        
        Args:
            cost_data (pd.DataFrame): DataFrame containing base costs by region and age group
            weights (Dict[str, float]): Dictionary of chronic condition risk weights
            chronic_condition_sources (Dict[str, str], optional): Dictionary mapping conditions to their data sources
            family_history_risk (Dict[str, float], optional): Dictionary of family history risk factors
            lifestyle_source (str, optional): Source URL for lifestyle data
            insurance_source (str, optional): Source URL for insurance data
            insurance_discount_rate (float, optional): Insurance discount rate (default: 0.3 for 30%)
        """
        self.cost_data = cost_data
        
        # Define default data sources if not provided
        self.chronic_condition_sources = chronic_condition_sources or {
            "diabetes": "https://www.cdc.gov/diabetes/data/statistics-report/index.html",
            "hypertension": "https://www.heart.org/en/health-topics/high-blood-pressure",
            "heart_disease": "https://www.heart.org/en/health-topics/consumer-healthcare/what-is-cardiovascular-disease",
            "asthma": "https://www.lung.org/lung-health-diseases/lung-disease-lookup/asthma",
            "cancer": "https://www.cancer.org/cancer/cancer-basics/cancer-facts-and-figures.html",
            "copd": "https://www.lung.org/lung-health-diseases/lung-disease-lookup/copd",
            "depression": "https://www.nimh.nih.gov/health/statistics/major-depression",
            "obesity": "https://www.cdc.gov/obesity/data/index.html"
        }
        
        self.family_history_risk = family_history_risk or {
            "cancer": 0.15,
            "heart_disease": 0.20,
            "diabetes": 0.15
        }
        
        self.lifestyle_source = lifestyle_source or "https://www.who.int/data/gho/data/themes/topics/health-behaviours"
        self.insurance_source = insurance_source or "https://www.oecd.org/health/health-data.htm"
        self.insurance_discount_rate = insurance_discount_rate
        
        # Initialize weights with source information
        self.weights = {}
        for condition, weight in weights.items():
            if condition in self.chronic_condition_sources:
                self.weights[condition] = {
                    'value': float(weight),
                    'source': self.chronic_condition_sources[condition]
                }
            else:
                self.weights[condition] = {
                    'value': float(weight),
                    'source': 'General medical research data'
                }

    def _get_age_group(self, age: int) -> str:
        """Convert age to age group category."""
        if age < 40:
            return "30-39"
        elif age < 50:
            return "40-49"
        elif age < 60:
            return "50-59"
        else:
            return "60+"

    def predict(self, 
                age: int, 
                region: str, 
                chronic_conditions: List[str], 
                family_history: List[str], 
                lifestyle_score: int, 
                insurance_status: bool) -> dict:
        """
        Predict health costs based on input parameters and return detailed calculation steps.
        Returns a dict with 'final_cost' and 'details'.
        """
        # Get base cost for region and age group
        age_group = self._get_age_group(age)
        try:
            base_cost = self.cost_data.loc[(self.cost_data['region'] == region) & 
                                         (self.cost_data['age_group'] == age_group), 
                                         'base_cost'].iloc[0]
        except IndexError:
            base_cost = self.cost_data['base_cost'].mean()

        details = []
        details.append({
            'step': 'Base Cost',
            'desc': f'Region: {region}, Age Group: {age_group}',
            'value': base_cost,
            'source': self.insurance_source
        })

        # Calculate risk factors
        risk = 0.0
        chronic_risk = 0.0
        chronic_breakdown = []
        for condition in chronic_conditions:
            cond_info = self.weights.get(condition.lower(), {'value': 0.0, 'source': 'Data not available'})
            cond_risk = cond_info['value']
            chronic_risk += cond_risk
            chronic_breakdown.append((condition, cond_risk, cond_info['source']))
        if chronic_breakdown:
            details.append({
                'step': 'Chronic Conditions',
                'desc': ', '.join([f"{c}: +{r:.2f} (Source: {s})" for c, r, s in chronic_breakdown]),
                'value': chronic_risk,
                'source': '; '.join([s for _, _, s in chronic_breakdown])
            })
        risk += chronic_risk

        family_risk = 0.0
        family_breakdown = []
        for condition in family_history:
            if condition.lower() in self.family_history_risk:
                fam_risk = self.family_history_risk[condition.lower()]
                family_risk += fam_risk
                family_breakdown.append((condition, fam_risk, self.chronic_condition_sources.get(condition.lower(), 'General medical research data')))
        if family_breakdown:
            details.append({
                'step': 'Family History',
                'desc': ', '.join([f"{c}: +{r:.2f} (Source: {s})" for c, r, s in family_breakdown]),
                'value': family_risk,
                'source': '; '.join([s for _, _, s in family_breakdown])
            })
        risk += family_risk

        lifestyle_risk = (10 - lifestyle_score) * 0.03
        details.append({
            'step': 'Lifestyle Score',
            'desc': f'Score: {lifestyle_score}/10 -> Risk: +{lifestyle_risk:.2f}',
            'value': lifestyle_risk,
            'source': self.lifestyle_source
        })
        risk += lifestyle_risk

        details.append({
            'step': 'Total Risk Factor',
            'desc': 'Sum of all risk factors (Chronic Conditions + Family History + Lifestyle)',
            'value': risk,
            'source': 'Internal Model Calculation'
        })

        predicted_cost = base_cost * (1 + risk)
        details.append({
            'step': 'Cost Before Insurance',
            'desc': f'Base Cost (${base_cost:,.2f}) x (1 + Total Risk {risk:.2f})',
            'value': predicted_cost,
            'source': 'Internal Model Calculation'
        })

        if insurance_status:
            final_cost = predicted_cost * (1 - self.insurance_discount_rate)
            details.append({
                'step': 'Insurance Discount',
                'desc': f'Applied {self.insurance_discount_rate*100:.0f}% discount for insurance',
                'value': final_cost,
                'source': self.insurance_source
            })
        else:
            final_cost = predicted_cost
            details.append({
                'step': 'Insurance Discount',
                'desc': 'No insurance discount applied',
                'value': final_cost,
                'source': self.insurance_source
            })

        return {
            'final_cost': round(final_cost, 2),
            'details': details
        } 