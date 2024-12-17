import openai
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gdown


# Set your OpenAI API key from .env file or directly set it here
openai.api_key = "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"

# Set wide layout
st.set_page_config(layout="wide")

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
                {"role": "system", "content": "You are a helpful assistant in the real estate industry."}
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
        if user_input:
            # Append user message to chat log
            st.session_state.chat_log.append({"role": "user", "content": user_input})

            # Generate AI response
            ai_response = chatbot(user_input)

            # Append AI response to chat log
            st.session_state.chat_log.append({"role": "assistant", "content": ai_response})

            # Clear the input field after processing
            st.experimental_set_query_params()  # Update URL state if needed

