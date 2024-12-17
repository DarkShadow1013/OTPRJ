import streamlit as st
import openai

# Streamlit layout settings
st.set_page_config(layout="wide")
openai.api_key = "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"  # Assuming you're using secrets management for safety

# Custom CSS for chatbox
st.markdown(
    """
    <style>
    .chatbox {
        margin-top: 30px;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        width: 80%;
        margin-left: auto;
        margin-right: auto;
        height: 400px; /* Set the fixed height for the chatbox */
        overflow-y: auto; /* Enable scrolling */
    }
    .chatbox-title {
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .chatbox-messages {
        max-height: 350px;
        overflow-y: auto;
        margin-bottom: 10px;
    }
    .message {
        margin-bottom: 10px;
    }
    .message-user {
        color: #007bff;
        font-weight: bold;
    }
    .message-ai {
        color: #28a745;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True
)

# Chatbot Section
st.markdown('<div class="chatbox">', unsafe_allow_html=True)
st.markdown('<div class="chatbox-title">Chat with our AI Assistant</div>', unsafe_allow_html=True)

# Display chat history with a scrollable area
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
message_count = len(st.session_state.messages)
max_display = 10  # Set a maximum number of messages to display at a time

# Show only the most recent messages, up to the max_display count
for message in st.session_state.messages[max(0, message_count - max_display):]:
    if message['role'] == 'User':
        st.markdown(f'<div class="message message-user">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="message message-ai">{message["content"]}</div>', unsafe_allow_html=True)

# Input for the user's message
user_input = st.text_input("Your message", key="user_input", placeholder="Ask me anything about the real estate market...")

if st.button("Send Message"):
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "User", "content": user_input})
        
        # Call OpenAI API for response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can adjust to another model if preferred
            messages=[
                {"role": "system", "content": "You are a helpful assistant in the real estate industry."},
                {"role": "user", "content": user_input}
            ]
        )
        
        # Extract the assistant's reply from the response
        ai_response = response['choices'][0]['message']['content']
        
        # Add AI response to chat history
        st.session_state.messages.append({"role": "AI", "content": ai_response})

        # Clear the input field and automatically rerun to display the new message
        st.rerun()


st.markdown('</div>', unsafe_allow_html=True)
