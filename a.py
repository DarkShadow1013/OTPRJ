import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gdown
st.set_page_config(layout="wide")
# Title for the Streamlit app
st.title("Average Resale Price Analysis")


# Instructions
st.write("""
This app visualizes the average resale price over the years. 
You can filter by towns, view the overall average, or examine trends by flat types.
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
    title_text='Average Resale Price Over the Years', title_x=0.4, title_y=0.99,
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
            # Move the range selector buttons higher by adjusting the 'y' value
            y=1.05  # Adjusted to move the buttons higher
        ),
        rangeslider=dict(visible=True, bgcolor='rgba(211, 211, 211, 0.2)'),  # Set slider background to light grey
        type="date"
    ),
    plot_bgcolor='rgba(211, 211, 211, 0.2)',  # Set chart background to light grey
    paper_bgcolor='white',  # Keep the area surrounding the chart white
    legend=dict(
        bgcolor='rgba(0,0,0,0)',  # Transparent legend background
        borderwidth=0  # Remove legend border if desired
    ),
    updatemenus=[
        {
            'buttons': [
                {
                    'label': 'All Towns',
                    'method': 'update',
                    'args': [{'visible': [True] * len(df_avg_price['town'].unique()) + [True] + [False] * len(df_flat_type_avg['flat_type'].unique())},
                             {'title': 'Average Resale Price Over the Years by Town'}]
                },
                *[
                    {
                        'label': town,
                        'method': 'update',
                        'args': [{'visible': [town == t for t in df_avg_price['town'].unique()] + [False] + [False] * len(df_flat_type_avg['flat_type'].unique())},
                                 {'title': f'Average Resale Price in {town}'}]
                    }
                    for town in df_avg_price['town'].unique()
                ]
            ],
            'direction': 'down',
            'showactive': True,
            'x': 0.15,
            'xanchor': 'left',
            'y': 1.15,  # Keep dropdown above the plot
            'yanchor': 'top'
        },
        {
            'buttons': [
                {
                    'label': 'Show Overall Average',
                    'method': 'update',
                    'args': [{'visible': [False] * len(df_avg_price['town'].unique()) + [True] + [False] * len(df_flat_type_avg['flat_type'].unique())},
                             {'title': 'Overall Average Resale Price Over the Years'}]
                }
            ],
            'type': 'buttons',
            'x': 0.883,
            'xanchor': 'center',
            'y': 1.15,  # Keep button above the plot
            'yanchor': 'top'
        },
        {
            'buttons': [
                {
                    'label': 'Flat Types',
                    'method': 'update',
                    'args': [{'visible': [False] * len(df_avg_price['town'].unique()) + [False] + [True] * len(df_flat_type_avg['flat_type'].unique())},
                             {'title': 'Average Resale Price by Flat Type'}]
                }
            ],
            'type': 'buttons',
            'x': 0.35,
            'xanchor': 'center',
            'y': 1.15,  # Keep button above the plot
            'yanchor': 'top'
        }
    ],
    showlegend=True,
    shapes=[
        # Adding the large rectangle to cover the entire area (not just corners)
        {
            'type': 'rect',
            'x0': -0.55,  # Extend the left boundary
            'y0': -0.95,  # Extend the bottom boundary
            'x1': 1.55,   # Extend the right boundary
            'y1': 1.55,   # Extend the top boundary
            'xref': 'paper',
            'yref': 'paper',
            'fillcolor': 'rgba(211, 211, 211, 0.14)',  # Very light grey
            'line': {
                'width': 0  # Border width
            },
            'opacity': 1
        }
    ],
    height=600  # Increase the height of the plot area (height of the plot itself)
)

# Display the figure in Streamlit
st.plotly_chart(fig)
