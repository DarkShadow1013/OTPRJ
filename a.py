import os
import openai
import pandas as pd
import plotly.graph_objects as go
import gdown
import streamlit as st
from openai import OpenAI

# Set wide layout
st.set_page_config(layout="wide")

# OpenAI API Key (set via environment variable)
client = OpenAI(
    api_key="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",  # Fetches from environment variable
)

# Custom CSS for chatbot and intro styling
st.markdown(
    """
    <style>
    .chatbox-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        background-color: white;
        border: 1px solid #ccc;
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
        padding: 10px;
        z-index: 1000;
    }
    .chatbox-header {
        background-color: #007BFF;
        color: white;
        padding: 10px;
        font-weight: bold;
        text-align: center;
        border-radius: 10px 10px 0 0;
    }
    .chatbox-body {
        max-height: 300px;
        overflow-y: auto;
        padding: 10px;
        font-size: 14px;
    }
    .chatbox-input {
        display: flex;
        margin-top: 10px;
    }
    .chatbox-input input {
        flex: 1;
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 5px;
    }
    .chatbox-input button {
        margin-left: 10px;
        background-color: #007BFF;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        cursor: pointer;
    }
    .chatbox-input button:hover {
        background-color: #0056b3;
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

# ChatGPT API interaction (Updated with new OpenAI client method)
def get_chatbot_response(user_input):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": f"You are a helpful assistant for real estate analytics. Answer the following question: {user_input}"}
            ],
            model="gpt-4",  # You can use gpt-3.5-turbo for faster responses
        )
        return chat_completion["choices"][0]["message"]["content"].strip()  # Extracts the correct response
    except Exception as e:
        return f"Error: {e}"

# Persistent Chatbot
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown('<div class="chatbox-container">', unsafe_allow_html=True)
st.markdown('<div class="chatbox-header">Chatbot Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="chatbox-body" id="chatbox-body">', unsafe_allow_html=True)

# Display chat history
for chat in st.session_state.chat_history:
    st.markdown(chat, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
user_input = st.text_input("Type your question:", key="chat_input")
if user_input:
    user_response = get_chatbot_response(user_input)
    st.session_state.chat_history.append(f"**You:** {user_input}<br>**Bot:** {user_response}")
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)
