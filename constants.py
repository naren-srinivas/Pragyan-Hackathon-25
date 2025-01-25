# Configuration parameters
INPUT_PARAMETERS = {
    "capital_cost": {
        "min": -30,
        "max": 30,
        "default": 0,
        "unit": "% change",
        "description": "Budget adjustment"
    },
    "labor_availability": {
        "min": -20,
        "max": 20,
        "default": 0,
        "unit": "% change",
        "description": "Workforce adjustment"
    },
    "material_cost": {
        "min": -25,
        "max": 25,
        "default": 0,
        "unit": "% change",
        "description": "Material cost adjustment"
    },
    "project_duration": {
        "min": -15,
        "max": 15,
        "default": 0,
        "unit": "% change",
        "description": "Timeline adjustment"
    },
    "weather_impact": {
        "min": 0,
        "max": 40,
        "default": 0,
        "unit": "% days affected",
        "description": "Adverse weather likelihood"
    }
}

COLOR_SCHEME = {
    "primary": "#2E86AB",    # Primary blue tone
    "secondary": "#A23B72",  # Secondary magenta tone
    "background": "#F5F5F5", # Light gray background
    "text": "#333333",       # Dark text color
    "accent": "#2E86AB"      # Matching primary as accent
}