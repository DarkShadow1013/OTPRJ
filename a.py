import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gdown

# Set wide layout
st.set_page_config(layout="wide")

# Custom CSS for intro styling
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

# Sidebar with navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")
section = st.sidebar.radio(
    "Go to Section:",
    options=["Intro", "Line Chart", "Price Calculator", "Price Forecaster"],
    index=0,
)

# Intro Section
if section == "Intro":
    st.markdown('<div class="intro-section">', unsafe_allow_html=True)
    st.markdown('<div class="intro-title">HDB Analytics Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="intro-subtitle">Explore trends in Singapore\'s real estate market.</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <img src="https://via.placeholder.com/800x400?text=Real+Estate+Dashboard" 
             alt="Dashboard Overview" 
             style="display: block; margin: 20px auto; width: 50%; border-radius: 10px;">
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
    **How to use this dashboard:**
    - Scroll down to see the interactive chart.
    - Use dropdowns and buttons to filter by towns or flat types.
    - Click on legend items to toggle visibility of traces.
    """)

# Load the CSV file from Google Drive
@st.cache_data
def load_data():
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

# Line Chart Section
if section == "Line Chart":
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

    # Add range selector buttons (e.g., 6m, 1y, etc.)
    fig.update_layout(
        title_text='<b>Average Resale Price Over the Years</b>',
        xaxis_title='Month',
        yaxis_title='Average Resale Price',
        xaxis=dict(
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=[
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=2, label="2y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ]
            ),
            type="date"
        ),
        height=600,
        updatemenus=[
            # Dropdown for towns
            {
                'buttons': [
                    {
                        'label': 'All Towns',
                        'method': 'update',
                        'args': [{'visible': [True] * len(df_avg_price['town'].unique()) + [True] + [False] * len(df_flat_type_avg['flat_type'].unique())},
                                 {'title': '<b>Average Resale Price Over the Years by Town</b>'}]
                    },
                    *[
                        {
                            'label': town,
                            'method': 'update',
                            'args': [{'visible': [town == t for t in df_avg_price['town'].unique()] + [False] + [False] * len(df_flat_type_avg['flat_type'].unique())},
                                     {'title': f'<b>Average Resale Price in {town}</b>'}]
                        }
                        for town in df_avg_price['town'].unique()
                    ]
                ],
                'direction': 'down',
                'showactive': True,
                'x': 0.22,
                'xanchor': 'left',
                'y': 1.11,
                'yanchor': 'top'
            },
            # Button for overall average
            {
                'buttons': [
                    {
                        'label': 'Show Overall Average',
                        'method': 'update',
                        'args': [{'visible': [False] * len(df_avg_price['town'].unique()) + [True] + [False] * len(df_flat_type_avg['flat_type'].unique())},
                                 {'title': '<b>Overall Average Resale Price Over the Years</b>'}]
                    }
                ],
                'type': 'buttons',
                'x': 0.9,
                'xanchor': 'center',
                'y': 1.11,
                'yanchor': 'top'
            },
            # Button for flat types
            {
                'buttons': [
                    {
                        'label': 'Flat Types',
                        'method': 'update',
                        'args': [{'visible': [False] * len(df_avg_price['town'].unique()) + [False] + [True] * len(df_flat_type_avg['flat_type'].unique())},
                                 {'title': '<b>Average Resale Price by Flat Type</b>'}]
                    }
                ],
                'type': 'buttons',
                'x': 0.43,
                'xanchor': 'center',
                'y': 1.11,
                'yanchor': 'top'
            }
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

# Price Calculator Section
if section == "Price Calculator":
    st.write("### Price Calculator (Coming Soon)")
    st.write("This section will allow you to estimate flat resale prices based on input parameters.")

# Price Forecaster Section
if section == "Price Forecaster":
    st.write("### Price Forecaster (Coming Soon)")
    st.write("This section will forecast future resale prices using historical trends.")
