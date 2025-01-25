import streamlit as st
from model_loader import ConstructionModel
from utils import parse_llm_response, create_visualizations
from constants import INPUT_PARAMETERS, COLOR_SCHEME
import pandas as pd

# Initialize Gemini API
API_KEY = "AIzaSyBY9gpL3qQYsUoXNt76nJOUa04NBvdKX_M"  # Replace with your Gemini API key
model = ConstructionModel(API_KEY)

# UI Configuration
st.set_page_config(
    page_title="Construction AI Analyst",
    page_icon="🏗️",
    layout="wide"
)

def parse_custom_parameters(input_text):
    """Parse custom parameters from free-form text input"""
    custom_params = {}
    for line in input_text.split("\n"):
        if ":" in line:
            param, value = line.split(":", 1)
            custom_params[param.strip()] = value.strip()
    return custom_params

def format_metric_value(value):
    """Format metric value with correct sign"""
    if isinstance(value, (int, float)):
        return f"{value:+.1f}%"  # Uses inherent numeric sign
    return str(value)

def generate_insights(location, inputs, custom_params):
    prompt = f"""
            As a construction expert, analyze this scenario:
            - Location: {location}
            - Capital Budget: {inputs['capital_cost']}% change
            - Labor Availability: {inputs['labor_availability']}% change
            - Material Costs: {inputs['material_cost']}% change
            - Project Duration: {inputs['project_duration']}% change
            - Weather Risk: {inputs['weather_impact']}% days affected
            """
            
    # Add custom parameters to the prompt
    if custom_params:
        for param, value in custom_params.items():
            prompt += f"\n- {param}: {value}"
            
    prompt += """
            Provide:
            1. Numerical predictions for key metrics
            2. Causal relationships between parameters (as [INSIGHT])
            3. Detailed methodology analysis (as [DEEP_INSIGHT])
            4. Actionable recommendations
            
            Use this format: The output reponse must be exactly like this ( if the metric is increasing, use Positive number, else use negative)
            Always give only numbers for all the Metrics
            [METRIC] Total Cost: X%
            [METRIC] Delay Risk: Y%
            [METRIC] Budget Variance: Z%
            [METRIC] ROI: A%
            
            [INSIGHT] The change in parameter {x} causes a change in parameter {y} due to {reason}.
            [DEEP_INSIGHT] Detailed analysis of the corresponding insight of at least 5 to 6 line explaining the complete methodology of the relationships including location-specific factors, historical data, and industry benchmarks...
            [INSIGHT] Another insight...
            [DEEP_INSIGHT] Its corresponding detailed analysis...
            Mention the location in the Insights as well
            """
    print(prompt)
    # Get Gemini Response
    try:
        response = model.generate_insights(prompt)
        print(response)
        if not response:  # Handle empty responses
            st.error("Failed to get valid response from AI model")
            return {}, [], []
        
        metrics, insights, deep_insights = parse_llm_response(response)
        return metrics, insights, deep_insights
    except Exception as e:
        st.error(f"Failed to generate insights. Please try again!")
        return {}, [], []

def main():
    # Sidebar Controls
    with st.sidebar:
        st.image("assets/logo.png", width=200)
        st.header("Project Setup ⚙️")
        
        location = st.text_input(
            "Enter Project Location",
            placeholder="e.g., New York, USA",
            help="Specify the location for context (e.g., city, country)."
        )
        
        st.header("Adjust Parameters")
        inputs = {}
        for param, config in INPUT_PARAMETERS.items():
            inputs[param] = st.slider(
                label=f"{config['description']} ({config['unit']})",
                min_value=config["min"],
                max_value=config["max"],
                value=config["default"],
                key=param
            )
            
        st.header("Additional Parameters")
        custom_input = st.text_area(
            "Enter additional parameters (one per line, format: parameter: value)",
            placeholder="e.g., Soil Quality: Poor\nRegulatory Hurdles: High",
            height=100
        )
        custom_params = parse_custom_parameters(custom_input)
    
    # Main Display Area
    st.title("Construction Project Analyzer")
    st.markdown(f"""
    <style>
    /* Full Blue Expander Styling */
    div[data-testid="stExpander"] > div {{
        background-color: {COLOR_SCHEME["primary"]} !important;
        border-radius: 8px !important;
        margin: 8px 0 !important;
        border: none !important;
        padding: 12px !important;
    }}

    /* Expander Header Text */
    div[data-testid="stExpander"] div[role="button"] p {{
        color: white !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }}

    /* Content Area Styling */
    div[data-testid="stExpander"] > div > div {{
    background-color: {COLOR_SCHEME["primary"]} !important;
    padding: 25px !important;  /* Increased from 15px */
    border-radius: 0 0 12px 12px !important;  /* Larger radius */
    margin: 15px 0 !important;  /* Added margin */
    width: 100% !important;  /* Full width */
    min-height: 150px !important;  /* Minimum height */
    font-size: 16px !important;  /* Larger text */
    line-height: 1.6 !important;  /* Better spacing */
    box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;  /* Added depth */
    }}

    /* Deep Insights Text */
    .deep-insight {{
        color: white !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
        padding: 10px !important;
        background-color: #2B7FA5 !important;
        border-radius: 4px !important;
        margin: 8px 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    if location:
        metrics, insights, deep_insights = generate_insights(location, inputs, custom_params)
        
        # Metrics Display
        st.subheader("Key Metrics")
        if metrics:
            cols = st.columns(len(metrics))
            for idx, (metric, value) in enumerate(metrics.items()):
                with cols[idx % len(metrics)]:
                    formatted_value = format_metric_value(value)
                    st.metric(label=metric, value=formatted_value)
        else:
            st.warning("No valid metrics found in the response.")
        
        # Insights Section with Full Blue Boxes
        st.subheader("Key Insights")
        if insights:
            for idx, (insight, deep_insight) in enumerate(zip(insights, deep_insights)):
                with st.expander(f"🔍 {insight}", expanded=False):
                    st.markdown(f"""
                    <div class="deep-insight">
                        📚 <strong>Detailed Analysis:</strong><br><br>
                        {deep_insight}
                    </div>
                    """, unsafe_allow_html=True)
            
            if len(deep_insights) > len(insights):
                st.warning(f"Found {len(deep_insights)-len(insights)} additional analyses without matching insights")
        else:
            st.warning("No insights generated for this scenario")
        
        # Visualizations
        st.subheader("Impact Analysis")
        fig_bar, fig_gauge = create_visualizations(metrics)
        if fig_bar and fig_gauge:
            st.plotly_chart(fig_bar, use_container_width=True)
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.warning("Could not generate visualizations from metrics data")
            
        # Detailed Metrics Table
        with st.expander("📊 Detailed Metrics Table"):
            if metrics:
                df = pd.DataFrame(metrics.items(), columns=["Metric", "Value"])
                df = df.dropna(subset=["Value"])
                if not df.empty:
                    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
                    df = df.dropna(subset=["Value"])
                    df["Value"] = df["Value"].apply(format_metric_value)
                    
                    st.dataframe(
                        df,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "Metric": st.column_config.TextColumn(width="medium"),
                            "Value": st.column_config.NumberColumn(
                                format="%+.1f %%",
                                help="Percentage change from baseline"
                            )
                        }
                    )
                else:
                    st.warning("No valid metrics to display")
    else:
        st.warning("Please enter a project location to begin analysis")

if __name__ == "__main__":
    main()