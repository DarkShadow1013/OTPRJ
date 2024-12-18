import openai
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gdown


# Set your OpenAI API key from .env file or directly set it here
openai.api_key = st.secrets["openai"]["api_key"]

# Set wide layout
st.set_page_config(layout="wide")

st.sidebar.markdown(
    """
    <a href="https://www.orangetee.com" target="_blank">
        <img src="logo.png" alt="Your Logo" style="width: 100%; height: auto;"/>
    </a>
    """, 
    unsafe_allow_html=True
)

# Sidebar with navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")
section = st.sidebar.radio(
    "Go to Section:",
    options=["Intro", "Line Chart", "Chatbot"],
    index=0,
)

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

# Intro Section
if section == "Intro":
    st.markdown('<div class="intro-section">', unsafe_allow_html=True)
    st.markdown('<h1 style="font-weight: bold; font-size: 36px;">HDB Analytics Portal</h1>', unsafe_allow_html=True)
    st.markdown('<div class="intro-subtitle">Explore trends in Singapore\'s real estate market.</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <img src="https://www.scnsoft.com/data-analytics/real-estate-data-analytics/real-estate-analytics_cover-01.svg" 
             alt="Dashboard Overview" 
             style="display: block; margin: 20px auto; width: 50%; border-radius: 10px;">
        """,
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("""
    **HDB Analytics Portal:**
    
    - **Overview:** This portal provides an interactive platform for exploring and analyzing HDB property data, offering valuable insights for real estate agents, investors, and individuals interested in the property market.
    
    - **Data Visualization:** View property data in an intuitive and visually appealing manner through dynamic charts, tables, and maps. Analyze trends, prices, and sales volume over time.
    
    - **Customizable Filters:** Customize your search based on room types, price range, and amenities, with real-time updates as you adjust the filters.
    
    - **Insights & Reports:** Access detailed insights and reports to support your decision-making process. The portal provides up-to-date property market trends and analytics for a comprehensive view.
    
    - **Real-Time Updates:** Stay informed with the latest data, refreshed regularly to ensure accurate and current property information.
    """)

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
                'x': 0.19,
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
                        'args': [{'visible': [False] * len(df_avg_price['town'].unique()) + [True] + [True] * len(df_flat_type_avg['flat_type'].unique())},
                                 {'title': '<b>Average Resale Price by Flat Type</b>'}]
                    }
                ],
                'type': 'buttons',
                'x': 0.5,
                'xanchor': 'center',
                'y': 1.11,
                'yanchor': 'top'
            }
        ]
    )

    # Display the plot
    st.plotly_chart(fig)

if section == "Chatbot":
    st.title("AI Assistant")

    # Initialize session state for storing chat history
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    # Function to generate a response from the chatbot
    def chatbot(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant in the real estate industry of Singapore, you work for orangetee as well."}
            ] + [{"role": log["role"], "content": log["content"]} for log in st.session_state.chat_log] +
            [{"role": "user", "content": prompt}],
            max_tokens=150  # Adjust token limit as needed
        )
        return response['choices'][0]['message']['content'].strip()

    # Display chat log
    st.markdown("### Chat Log")
    chat_container = st.container()
    with chat_container:
        for log in st.session_state.chat_log:
            if log["role"] == "user":
                st.markdown(f"**You:** {log['content']}")
            elif log["role"] == "assistant":
                st.markdown(f"**Chatbot:** {log['content']}")

    # Input field below chat log
    st.markdown("---")
    user_input = st.text_input("Your message", placeholder="Ask me anything about real estate...")

    # Process input when "Send" is pressed
    if st.button("Send"):
        if user_input.strip():
            # Append user message to chat log
            st.session_state.chat_log.append({"role": "user", "content": user_input.strip()})

            # Generate AI response and append it to chat log
            ai_response = chatbot(user_input.strip())
            st.session_state.chat_log.append({"role": "assistant", "content": ai_response})

            # Clear the input field for the next message
            st.rerun()  # Immediately rerun the app to show updates
