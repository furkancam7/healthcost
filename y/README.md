# Health Cost Predictor

This application predicts annual health costs based on various factors including age, region, chronic conditions, family history, lifestyle score, and insurance status.

## Features

- Predicts annual health costs based on multiple factors
- Supports different regions (USA, Europe, Asia, Turkey)
- Considers chronic conditions and family history
- Takes into account lifestyle factors
- Applies insurance discounts
- User-friendly web interface
- Generates detailed PDF reports of predictions

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:7860)

## Input Parameters

- **Age**: Your current age (30-100)
- **Region**: Your country/region of residence
- **Chronic Conditions**: Comma-separated list of chronic conditions (e.g., "diabetes, hypertension, asthma")
- **Family History**: Comma-separated list of family medical history (e.g., "cancer, heart_disease")
- **Lifestyle Score**: A score from 0-10 indicating your lifestyle habits (higher is better)
- **Insurance Status**: Whether you have health insurance

## Supported Conditions

The system recognizes the following chronic conditions:
- diabetes
- hypertension
- heart_disease
- asthma
- arthritis
- cancer
- chronic_kidney_disease
- copd
- depression
- obesity

## Data Sources

The prediction model uses two main data sources:
1. `data/health_costs_by_region.csv`: Base health costs by region and age group
2. `data/chronic_condition_weights.json`: Risk weights for different chronic conditions

## PDF Reports

The application generates detailed PDF reports that include:
- Personal information (age, region, lifestyle score, insurance status)
- Health information (chronic conditions and family history)
- Prediction results with the estimated annual health cost
- A disclaimer about the prediction's limitations

Reports are automatically generated and can be downloaded directly from the web interface. They are also saved in the `reports` directory with timestamps for future reference.

## Example Usage

1. Enter your age (e.g., 45)
2. Select your region (e.g., Turkey)
3. Enter any chronic conditions (e.g., "diabetes, hypertension")
4. Enter family history (e.g., "heart_disease")
5. Set your lifestyle score (0-10)
6. Check if you have insurance
7. Click "Submit" to get your predicted annual health cost
8. Download the detailed PDF report 