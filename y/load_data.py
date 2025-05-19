import pandas as pd
import json
import os

def load_costs():
    """Load health costs by region and age group"""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Default costs if file doesn't exist
    default_costs = [
        {'region': 'USA', 'age_group': '30-39', 'base_cost': 2000},
        {'region': 'USA', 'age_group': '40-49', 'base_cost': 3000},
        {'region': 'USA', 'age_group': '50-59', 'base_cost': 4000},
        {'region': 'USA', 'age_group': '60+', 'base_cost': 6000},
        {'region': 'Europe', 'age_group': '30-39', 'base_cost': 1500},
        {'region': 'Europe', 'age_group': '40-49', 'base_cost': 2250},
        {'region': 'Europe', 'age_group': '50-59', 'base_cost': 3000},
        {'region': 'Europe', 'age_group': '60+', 'base_cost': 4500},
        {'region': 'Asia', 'age_group': '30-39', 'base_cost': 1000},
        {'region': 'Asia', 'age_group': '40-49', 'base_cost': 1500},
        {'region': 'Asia', 'age_group': '50-59', 'base_cost': 2000},
        {'region': 'Asia', 'age_group': '60+', 'base_cost': 3000},
        {'region': 'Turkey', 'age_group': '30-39', 'base_cost': 800},
        {'region': 'Turkey', 'age_group': '40-49', 'base_cost': 1200},
        {'region': 'Turkey', 'age_group': '50-59', 'base_cost': 1600},
        {'region': 'Turkey', 'age_group': '60+', 'base_cost': 2400}
    ]
    
    # Try to load existing file, if not exists create with default data
    try:
        costs_df = pd.read_csv('data/health_costs_by_region.csv')
        if costs_df.empty:
            costs_df = pd.DataFrame(default_costs)
            costs_df.to_csv('data/health_costs_by_region.csv', index=False)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        costs_df = pd.DataFrame(default_costs)
        costs_df.to_csv('data/health_costs_by_region.csv', index=False)
    
    return costs_df

def load_weights():
    """Load chronic condition risk weights"""
    # Default weights if file doesn't exist
    default_weights = {
        "diabetes": 0.96,
        "hypertension": 0.72,
        "heart_disease": 1.20,
        "asthma": 0.33,
        "cancer": 1.44,
        "copd": 0.96,
        "depression": 0.48,
        "obesity": 0.72
    }
    
    # Try to load existing file, if not exists create with default data
    try:
        with open('data/chronic_condition_weights.json', 'r') as f:
            weights = json.load(f)
            if not weights:
                weights = default_weights
                with open('data/chronic_condition_weights.json', 'w') as f:
                    json.dump(weights, f, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        weights = default_weights
        with open('data/chronic_condition_weights.json', 'w') as f:
            json.dump(weights, f, indent=4)
    
    return weights 