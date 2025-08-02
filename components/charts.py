import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

def plot_financial_chart(years, eps_values, fcf_values, revenue_values=None, net_income_values=None):
    """
    Create an interactive financial performance chart with professional styling
    
    Parameters:
    years (list): List of years
    eps_values (list): EPS values
    fcf_values (list): Free Cash Flow values
    revenue_values (list): Optional revenue values
    net_income_values (list): Optional net income values
    """
    # Create DataFrame with proper data handling
    df = pd.DataFrame({
        "Year": years,
        "EPS": eps_values,
        "FCF": fcf_values
    })
    
    # Add optional metrics if provided
    if revenue_values is not None:
        df["Revenue"] = revenue_values
    if net_income_values is not None:
        df["Net Income"] = net_income_values

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add EPS bar chart
    fig.add_trace(
        go.Bar(
            x=df["Year"],
            y=df["EPS"],
            name="EPS",
            marker_color="#1f77b4",
            opacity=0.8,
            hovertemplate="<b>%{x}</b><br>EPS: %{y:,.2f}<extra></extra>"
        ),
        secondary_y=False
    )
    
    # Add FCF line chart
    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df["FCF"],
            name="FCF",
            mode="lines+markers",
            line=dict(width=3, color="#ff7f0e"),
            marker=dict(size=10, symbol="diamond"),
            hovertemplate="<b>%{x}</b><br>FCF: %{y:,.0f}<extra></extra>"
        ),
        secondary_y=True
    )
    
    # Add Revenue if available
    if "Revenue" in df:
        fig.add_trace(
            go.Scatter(
                x=df["Year"],
                y=df["Revenue"],
                name="Revenue",
                mode="lines",
                line=dict(width=2, color="#2ca02c", dash="dot"),
                hovertemplate="<b>%{x}</b><br>Revenue: %{y:,.0f}<extra></extra>"
            ),
            secondary_y=True
        )
    
    # Add Net Income if available
    if "Net Income" in df:
        fig.add_trace(
            go.Bar(
                x=df["Year"],
                y=df["Net Income"],
                name="Net Income",
                marker_color="#d62728",
                opacity=0.4,
                hovertemplate="<b>%{x}</b><br>Net Income: %{y:,.0f}<extra></extra>"
            ),
            secondary_y=True
        )
    
    # Calculate growth rates
    eps_growth = calculate_growth_rate(df["EPS"])
    fcf_growth = calculate_growth_rate(df["FCF"])
    
    # Add annotations for growth rates
    annotations = []
    for i, year in enumerate(df["Year"]):
        if eps_growth[i] is not None:
            annotations.append(dict(
                x=year,
                y=df["EPS"].iloc[i],
                text=f"<b>{eps_growth[i]:+.0f}%</b>",
                showarrow=False,
                yshift=20,
                font=dict(size=10, color="#1f77b4")
            ))
        
        if fcf_growth[i] is not None:
            annotations.append(dict(
                x=year,
                y=df["FCF"].iloc[i],
                text=f"<b>{fcf_growth[i]:+.0f}%</b>",
                showarrow=False,
                yshift=20,
                font=dict(size=10, color="#ff7f0e")
            ))
    
    # Format axes and layout
    fig.update_layout(
        title="<b>Financial Performance Analysis</b>",
        title_x=0.03,
        title_font_size=20,
        xaxis_title="Tahun",
        yaxis_title="EPS",
        yaxis2_title="FCF (Juta Rupiah)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=60, b=80, l=60, r=60),
        annotations=annotations,
        height=500
    )
    
    # Add custom grid and axis formatting
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#f0f0f0")
    fig.update_yaxes(
        secondary_y=False, 
        showgrid=True, 
        gridwidth=1, 
        gridcolor="#f0f0f0",
        tickformat=".2f"
    )
    fig.update_yaxes(
        secondary_y=True, 
        showgrid=False,
        tickformat=",.0f"
    )
    
    # Add watermark
    fig.add_annotation(
        text="Sumber: Data Fundamental Perusahaan",
        xref="paper", yref="paper",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=10, color="gray")
    )
    
    # Display in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    # Add metrics summary
    if len(df) > 1:
        with st.expander("📈 Ringkasan Pertumbuhan", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("EPS CAGR", 
                          f"{calculate_cagr(df['EPS']):+.1f}%",
                          f"{eps_growth[-1] if eps_growth[-1] else 0:+.1f}% YoY")
            with col2:
                st.metric("FCF CAGR", 
                          f"{calculate_cagr(df['FCF']):+.1f}%",
                          f"{fcf_growth[-1] if fcf_growth[-1] else 0:+.1f}% YoY")

def calculate_growth_rate(series):
    """Calculate year-over-year growth rates"""
    growth_rates = [None]
    for i in range(1, len(series)):
        if series.iloc[i-1] != 0:
            growth = ((series.iloc[i] / series.iloc[i-1]) - 1) * 100
            growth_rates.append(round(growth, 1))
        else:
            growth_rates.append(None)
    return growth_rates

def calculate_cagr(series):
    """Calculate compound annual growth rate"""
    if len(series) < 2 or series.iloc[0] == 0:
        return 0.0
    start = series.iloc[0]
    end = series.iloc[-1]
    years = len(series) - 1
    return ((end / start) ** (1/years) - 1) * 100

# Example usage in Streamlit app
if __name__ == "__main__":
    st.title("Analisis Kinerja Perusahaan")
    
    # Sample data
    years = [2019, 2020, 2021, 2022, 2023]
    eps_values = [150, 165, 142, 210, 255]
    fcf_values = [1200, 1500, 1100, 1800, 2200]
    revenue = [4500, 5200, 4800, 6100, 7200]
    net_income = [900, 1050, 950, 1300, 1600]
    
    plot_financial_chart(
        years=years,
        eps_values=eps_values,
        fcf_values=fcf_values,
        revenue_values=revenue,
        net_income_values=net_income
    )
