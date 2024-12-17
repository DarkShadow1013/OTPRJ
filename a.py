import openai
import streamlit as st

# Set OpenAI API Key (Ensure to replace with your actual key)
openai.api_key = "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"

# ChatGPT API interaction
def get_chatbot_response(user_input):
    try:
        # Using ChatCompletion API (ensure to call with correct parameters)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or use another model that is available to you
            messages=[
                {"role": "system", "content": "You are a helpful assistant for real estate analytics."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=100
        )
        
        # The correct way to access the response from the new OpenAI API
        return response['choices'][0]['message']['content'].strip()
    except openai.error.InvalidRequestError as e:
        # Handle specific error
        return f"Error: Invalid request. Please check your parameters. Details: {str(e)}"
    except openai.error.AuthenticationError as e:
        # Handle authentication issues
        return f"Error: Authentication failed. Please check your API key. Details: {str(e)}"
    except Exception as e:
        # Catch other general exceptions
        return f"Error: {str(e)}"

# Persistent Chatbot in Streamlit
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
