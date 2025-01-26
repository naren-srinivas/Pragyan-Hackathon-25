import re
import plotly.express as px
import pandas as pd
from constants import COLOR_SCHEME
import plotly.graph_objects as go
import streamlit as st

def parse_llm_response(response):
    """Robust parsing that handles various response formats"""
    metrics = {
        "Total Cost": None,
        "Delay Risk": None,
        "Budget Variance": None,
        "ROI": None
    }
    
    insights = []
    deep_insights = []

    # Clean response
    clean_response = re.sub(r'\*\*|\n{2,}', '\n', response).strip()
    
    # Split into sections
    sections = re.split(r'(\[METRIC\]|\[INSIGHT\]|\[DEEP_INSIGHT\])', clean_response)
    sections = [s.strip() for s in sections if s.strip()]

    current_section = None
    
    for section in sections:
        if section == '[METRIC]':
            current_section = 'METRIC'
        elif section == '[INSIGHT]':
            current_section = 'INSIGHT'
        elif section == '[DEEP_INSIGHT]':
            current_section = 'DEEP_INSIGHT'
        else:
            if current_section == 'METRIC':
                # Handle metrics
                metric_match = re.match(r'(.*?):\s*([+-]?\d+\.?\d*)%?', section)
                if metric_match:
                    metric, value = metric_match.groups()
                    try:
                        metrics[metric.strip()] = float(value)
                    except (ValueError, KeyError):
                        pass
            elif current_section == 'INSIGHT':
                insights.append(section.strip())
            elif current_section == 'DEEP_INSIGHT':
                deep_insights.append(section.strip())

    return metrics, insights, deep_insights

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from model_loader import ConstructionModel  # Your existing imports
from utils import parse_llm_response
from constants import COLOR_SCHEME

def create_visualizations(metrics):
    """Generate visualizations with robust error handling"""
    try:
        # Validate and clean metrics data
        clean_metrics = {}
        for key, value in metrics.items():
            try:
                # Handle percentage values and various numeric types
                num_value = float(str(value).replace('%', '').strip())
                clean_metrics[key] = num_value
            except (ValueError, TypeError, AttributeError):
                continue

        if not clean_metrics:
            return None, None

        # Create visualization data
        viz_df = pd.DataFrame({
            'Metric': clean_metrics.keys(),
            'Value': clean_metrics.values(),
            'AbsoluteValue': [abs(v) for v in clean_metrics.values()]
        })

        # Generate charts
        bar_chart = create_bar_chart(viz_df)
        gauge_chart = create_gauge_chart(viz_df)
        
        return bar_chart, gauge_chart

    except Exception as e:
        st.error(f"Visualization error: {str(e)}")
        return None, None

def create_bar_chart(df):
    """Create impact analysis bar chart"""
    try:
        fig = px.bar(
            df,
            x='Metric',
            y='Value',
            color='Metric',
            title='<b>Project Impact Analysis</b>',
            labels={'Value': 'Impact (%)'},
            text_auto='+.1f%',
            color_discrete_sequence=[COLOR_SCHEME['primary'], COLOR_SCHEME['secondary']]
        )
        fig.update_layout(
            yaxis_title="Impact Percentage",
            xaxis_title="Metrics",
            uniformtext_minsize=12,
            hovermode='x unified'
        )
        return fig
    except Exception as e:
        print(f"Bar chart error: {str(e)}")
        return None

def create_gauge_chart(df):
    """Create circular risk distribution gauge"""
    try:
        total_impact = df['AbsoluteValue'].sum()
        
        # Handle zero-risk scenario
        if total_impact <= 0:
            fig = go.Figure()
            fig.add_trace(go.Pie(
                values=[1],
                labels=['No Risks'],
                hole=0.75,
                marker_colors=[COLOR_SCHEME['success']],
                hoverinfo='none'
            ))
            fig.update_layout(
                title='<b>Risk Distribution</b>',
                annotations=[dict(
                    text='NO RISKS<br>DETECTED',
                    x=0.5, y=0.5,
                    font=dict(size=18, color=COLOR_SCHEME['success']),
                    showarrow=False
                )],
                showlegend=False,
                height=400,
                width=400,
                margin=dict(t=80, b=20)
            )
            return fig

        # Create proportional risk chart
        fig = go.Figure()
        fig.add_trace(go.Pie(
            values=df['AbsoluteValue'],
            labels=df['Metric'],
            hole=0.4,
            textinfo='percent+label',
            textposition='inside',
            insidetextorientation='horizontal',
            hovertemplate=(
                '<b>%{label}</b><br>' +
                'Actual Impact: %{customdata:.1f}%<br>' +
                'Proportion: %{percent:.1%}' +
                '<extra></extra>'
            ),
            customdata=df['Value'],
            marker_colors=px.colors.qualitative.Pastel
        ))
        
        fig.update_layout(
            title='<b>Risk Distribution</b>',
            uniformtext_minsize=12,
            height=400,
            width=400,
            margin=dict(t=80, b=20, l=20, r=20),
            showlegend=False
        )
        return fig

    except Exception as e:
        print(f"Gauge chart error: {str(e)}")
        return None