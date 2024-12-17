import openai
import streamlit as st

# OpenAI API Key (add your key here)
openai.api_key = "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"

# ChatGPT API interaction
def get_chatbot_response(user_input):
    try:
        # Using the updated ChatCompletion interface
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use gpt-3.5-turbo for faster responses
            messages=[
                {"role": "system", "content": "You are a helpful assistant for real estate analytics."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100
        )
        
        # Get the response text from the updated structure
        return response['choices'][0]['message']['content'].strip()
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
