import openai
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import xgboost as xgb
import gdown
from pathlib import Path
import pickle
import shap
from lime.lime_tabular import LimeTabularExplainer
# Set your OpenAI API key from .env file or directly set it here
openai.api_key = st.secrets["openai"]["api_key"]

# Set wide layout
st.set_page_config(layout="wide")

# Get the path to the logo.png file
logo_path = Path("logo.png")

# Add custom CSS for styling
st.markdown(
    """
    <style>
        /* Fix the sidebar width and prevent resizing */
        .css-1d391kg { 
            width: 250px !important; /* Set the sidebar width to 250px */
            height: 100vh !important; /* Ensure the sidebar takes full height */
            overflow: hidden !important; /* Prevent content from overflowing */
        }

        /* Ensure the sidebar cannot be hidden */
        .css-1d391kg > div { 
            visibility: visible !important; 
        }

        /* Move the logo higher in the sidebar */
        .sidebar-logo {
            margin-top: -700px; /* Adjust the top margin to move the logo higher */
            text-align: center;
        }


        /* Move buttons to the left and make them same size */
        div.stButton > button {
            width: 100% !important; /* Full width buttons */
            padding: 15px; /* Adjust padding for consistent button size */
            font-size: 16px; /* Adjust font size */
            margin-top: 5px; /* Space between buttons */
            text-align: left !important; /* Align text to the left */
        }

        /* Adjust the line below the title */
        .css-1v3fvcr {
            margin-top: 5px !important; /* Move the line closer to the title */
        }

        /* Fix the layout of the sidebar and its elements */
        .css-1v3fvcr {
            margin-top: 10px !important; /* Adjust this value to move the line down */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Add the logo to the sidebar with adjusted styling
st.sidebar.image("logo.png", use_container_width=True)

# Sidebar with navigation (using normal buttons)

st.sidebar.markdown("---")

# Initialize session state for section if it doesn't exist
if "section" not in st.session_state:
    st.session_state.section = "Intro"  # Default to "Intro"

# Replace radio buttons with normal buttons
if st.sidebar.button("Home"):
    st.session_state.section = "Home"
if st.sidebar.button("Price Chart"):
    st.session_state.section = "Price Chart"
if st.sidebar.button("HDB Flat Price Calculator"):
    st.session_state.section = "HDB Flat Price Calculator"
if st.sidebar.button("Otty Chatbot🤖"):
    st.session_state.section = "Otty Chatbot"

# Use the session state to determine the current section
section = st.session_state.section



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
if section == "Home":
    st.markdown('<div class="intro-section" style="margin-top: -20px;">', unsafe_allow_html=True)
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




# Price Calculator Section
if section == "HDB Flat Price Calculator":
    st.title("HDB Flat Price Calculator")
    
    # User inputs
    town = st.selectbox("Select Town", df_all["town"].unique())
    flat_type = st.selectbox("Select Flat Type", df_all["flat_type"].unique())
    storey_range = st.selectbox("Select Storey Range", [
        "01 TO 03", "04 TO 06", "07 TO 09", "10 TO 12", 
        "13 TO 15", "16 TO 18", "19 TO 21", "22 TO 24", 
        "25 TO 27", "28 TO 30", "31 TO 33", "34 TO 36", 
        "37 TO 39", "40 TO 42"])
    floor_area_sqm = st.number_input("Enter Floor Area (in sqm)")
    flat_model = st.selectbox("Enter Flat Model", df_all["flat_model"].unique())
    lease_commence_date = st.text_input("Enter Lease Commence Date (YYYY)")
    remaining_lease = st.text_input("Enter Remaining Lease (in years)")
    commercial = st.radio("Is it Commercial?", ["Yes", "No"])
    market_hawker = st.radio("Close to Market/Hawker?", ["Yes", "No"])
    miscellaneous = st.radio("Miscellaneous Facilities Available?", ["Yes", "No"])
    multistorey_carpark = st.radio("Has Multistorey Carpark?", ["Yes", "No"])
    precinct_pavilion = st.radio("Has Precinct Pavilion?", ["Yes", "No"])
    
    # Load preprocessing and model files
    with open("preprocessing_pipeline.pkl", "rb") as f:
        preprocessing = pickle.load(f)
    with open("best_model.pkl", "rb") as f:
        model = pickle.load(f)

    # Process inputs for prediction and XAI explanation
    input_data = pd.DataFrame({
        "year": "2024",
        "month_num": "12",  # Raw month input
        "town": [town],  
        "flat_type": [flat_type],  
        "storey_range": [storey_range],  
        "floor_area_sqm": [floor_area_sqm],  
        "flat_model": [flat_model],  
        "lease_commence_date": [lease_commence_date],  
        "remaining_lease": [remaining_lease],  
        "residential": "Y",  
        "commercial": ["Y" if commercial == "Yes" else "N"],  
        "market_hawker": ["Y" if market_hawker == "Yes" else "N"],  
        "miscellaneous": ["Y" if miscellaneous == "Yes" else "N"],  
        "multistorey_carpark": ["Y" if multistorey_carpark == "Yes" else "N"],  
        "precinct_pavilion": ["Y" if precinct_pavilion == "Yes" else "N"],  
    })

    # Preprocess inputs
    processed_data = preprocessing.transform(input_data)

    # Predict price
    if st.button("Calculate Price"):
        try:
            # Predict using the model
            prediction = model.predict(processed_data)
            st.success(f"Estimated Resale Price: ${prediction[0]:,.2f}")
        except Exception as e:
            st.error(f"Error during price prediction: {e}")

    # XAI Explanation Section (SHAP and Feature Importance)
    st.title("Model Explainability")

    # SHAP explanation
    if st.button("Explain Prediction with SHAP"):
        try:
            # Initialize SHAP explainer
            explainer = shap.Explainer(model)
            shap_values = explainer(processed_data)

            # SHAP summary plot with feature names
            st.write("SHAP Summary Plot")
            shap.summary_plot(shap_values, processed_data, feature_names=input_data.columns, show=False)
            st.pyplot(plt)

            # SHAP force plot with feature names
            st.write("SHAP Force Plot for First Prediction")
            shap.force_plot(explainer.expected_value, shap_values[0], processed_data.iloc[0], matplotlib=True, feature_names=input_data.columns)
            st.pyplot(plt)
        except Exception as e:
            st.error(f"Error in SHAP explanation: {e}")
    # Feature importance
    if st.button("Show Feature Importance"):
        try:
            st.write("Feature Importance Plot")
            ax = xgb.plot_importance(model, importance_type="gain", max_num_features=10)
            st.pyplot(ax.figure)
        except Exception as e:
            st.error(f"Error in plotting feature importance: {e}")

# Line Chart Section
if section == "Price Chart":
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

if section == "Otty Chatbot":
    st.title("Otty - AI Chatbot Assistant")

    # Initialize session state for storing chat history
    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    # Function to generate a response from the chatbot
    def chatbot(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant in the real estate industry of Singapore, your name is Otty, you should remind users at the begining, you work for orangetee as well and love orangetee and will always talk about how good they are."}
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
                st.markdown(f"**Otty:** {log['content']}")

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
