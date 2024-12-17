import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gdown

# Set wide layout
st.set_page_config(layout="wide")

# Custom CSS for intro background and styling
st.markdown(
    """
    <style>
    .intro-section {
        background-color: #f5f5f5; /* Light gray background */
        padding: 50px;
        text-align: center;
        margin-bottom: 50px;
        border-radius: 10px;
    }
    .intro-title {
        font-size: 3em;
        font-weight: bold;
        color: #333; /* Dark text color */
    }
    .intro-subtitle {
        font-size: 1.5em;
        margin-top: 10px;
        color: #666; /* Medium gray color */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Intro section with fixed image handling
st.markdown('<div class="intro-section">', unsafe_allow_html=True)
st.markdown('<div class="intro-title">Welcome to the Average Resale Price Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="intro-subtitle">Explore trends in Singapore\'s real estate market by towns and flat types.</div>', unsafe_allow_html=True)
st.markdown(
    """
    <img src="https://via.placeholder.com/800x400?text=Real+Estate+Dashboard" 
         alt="Dashboard Overview" 
         style="display: block; margin: 20px auto; width: 50%; border-radius: 10px;">
    """,
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

# Instructions section
st.write("""
**How to use this dashboard:**
- Scroll down to see the interactive chart.
- Use dropdowns and buttons to filter by towns or flat types.
- Click on legend items to toggle visibility of traces.
""")

# Load the CSV file from Google Drive
@st.cache_data
def load_data():
    # Replace <FILE_ID> with your Google Drive file ID
    file_id = "1pNq5BS4p17kYWPfFyKcnYGhrVwW5o_LG"
    url = f"https://drive.google.com/uc?id={file_id}"
    output = "merged_property_data.csv"
    gdown.download(url, output, quiet=False)
    df = pd.read_csv(output)
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')  # Ensure 'month' is datetime
    return df

df_all = load_data()

# Data preparation
df_avg_price = df_all.groupby(['month', 'town'], as_index=False)['resale_price'].mean()
df_monthly_avg = df_all.groupby('month', as_index=False)['resale_price'].mean()
df_flat_type_avg = df_all.groupby(['month', 'flat_type'], as_index=False)['resale_price'].mean()

# Create the Plotly figure
fig = go.Figure()

# Add traces for towns
for town in df_avg_price['town'].unique():
    town_data = df_avg_price[df_avg_price['town'] == town]
    fig.add_trace(go.Scatter(
        x=town_data['month'],
        y=town_data['resale_price'],
        mode='lines',
        name=town,
        visible=True  # Default visible for towns
    ))

# Add a trace for overall average
fig.add_trace(go.Scatter(
    x=df_monthly_avg['month'],
    y=df_monthly_avg['resale_price'],
    mode='lines',
    name='Overall Average',
    visible=True
))

# Add traces for flat types (initially hidden)
for flat_type in df_flat_type_avg['flat_type'].unique():
    flat_type_data = df_flat_type_avg[df_flat_type_avg['flat_type'] == flat_type]
    fig.add_trace(go.Scatter(
        x=flat_type_data['month'],
        y=flat_type_data['resale_price'],
        mode='lines',
        name=flat_type,
        visible=False
    ))

# Update the layout with dropdowns and buttons
fig.update_layout(
    title_text='<b>Average Resale Price Over the Years</b>',
    title_x=0.4,
    title_y=0.97,
    xaxis_title='Month',
    yaxis_title='Average Resale Price',
    xaxis=dict(
        rangeselector=dict(
            buttons=[
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(count=3, label="3y", step="year", stepmode="backward"),
                dict(step="all")
            ],
            y=1.05
        ),
        rangeslider=dict(visible=True, bgcolor='rgba(211, 211, 211, 0.2)'),
        type="date"
    ),
    plot_bgcolor='rgba(211, 211, 211, 0.2)',
    paper_bgcolor='white',
    legend=dict(
        bgcolor='rgba(0,0,0,0)',
        borderwidth=0
    ),
    height=600
)

# Add the figure to the Streamlit app
st.plotly_chart(fig, use_container_width=True)
