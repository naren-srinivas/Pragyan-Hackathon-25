import re
import plotly.express as px
import pandas as pd
from constants import COLOR_SCHEME

def parse_llm_response(response):
    """Extract structured data from natural language response with citation handling"""
    metrics = {
        "Total Cost": None,
        "Delay Risk": None,
        "Budget Variance": None,
        "ROI": None
    }
    
    insights = []
    deep_insights = []

    # Clean response from citations and special markers
    clean_response = re.sub(r'\[\d+\]|\(Source:.*?\)', '', response)  # Remove citations
    
    # Extract numerical values with enhanced pattern matching
    metric_pattern = r'\[METRIC\]\s*(Total Cost|Delay Risk|Budget Variance|ROI):?\s*([+-]?\d+\.?\d*)%?'
    for match in re.finditer(metric_pattern, clean_response, re.IGNORECASE):
        metric, value = match.groups()
        metric = metric.strip()
        try:
            metrics[metric] = float(value)
        except (ValueError, KeyError):
            metrics[metric] = None

    # Extract insights with multiline support
    insight_pattern = r'\[INSIGHT\](.*?)(?=\n\[DEEP_INSIGHT\]|\n\[METRIC\]|\n\Z)'
    deep_insight_pattern = r'\[DEEP_INSIGHT\](.*?)(?=\n\[INSIGHT\]|\n\[METRIC\]|\n\Z)'
    
    insights = [m.group(1).strip() 
               for m in re.finditer(insight_pattern, clean_response, re.DOTALL)]
    
    deep_insights = [m.group(1).strip()
                    for m in re.finditer(deep_insight_pattern, clean_response, re.DOTALL)]

    return metrics, insights, deep_insights

def create_visualizations(metrics):
    """Generate interactive charts with improved error handling"""
    # Filter and validate metrics
    filtered_metrics = {k: v for k, v in metrics.items() if v is not None and isinstance(v, (int, float))}
    
    if not filtered_metrics:
        return None, None

    df = pd.DataFrame({
        "Metric": list(filtered_metrics.keys()),
        "Value": list(filtered_metrics.values())
    })

    try:
        # Enhanced bar chart
        fig_bar = px.bar(
            df,
            x="Metric",
            y="Value",
            color="Metric",
            title="<b>Project Impact Analysis</b>",
            color_discrete_sequence=[COLOR_SCHEME["primary"], COLOR_SCHEME["secondary"]],
            labels={"Value": "Percentage Change (%)"},
            hover_data={"Value": ":.1f%"}
        )
        fig_bar.update_layout(
            uniformtext_minsize=14,
            uniformtext_mode='hide',
            hoverlabel=dict(
                bgcolor=COLOR_SCHEME["background"],
                font_size=14
            )
        )
    except Exception as bar_error:
        print(f"Bar chart error: {bar_error}")
        fig_bar = None

    try:
        # Enhanced gauge chart
        fig_gauge = px.pie(
            df,
            names="Metric",
            values="Value",
            hole=0.6,
            title="<b>Risk Distribution</b>",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"Value": "Impact %"}
        )
        fig_gauge.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>Impact: %{percent}</br>"
        )
        fig_gauge.update_layout(
            showlegend=False,
            margin=dict(t=50, b=20)
        )
    except Exception as pie_error:
        print(f"Pie chart error: {pie_error}")
        fig_gauge = None

    return fig_bar, fig_gauge