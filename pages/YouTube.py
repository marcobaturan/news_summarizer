# imput
import streamlit as st
import time
from engine import *
st.set_page_config(page_title="YT",
                   page_icon=":tv:")

# header
st.markdown("# YouTube summarizer :tv:️")
# sidebar
st.sidebar.markdown("# Welcome to News summarizer! 👋")
st.sidebar.markdown("# Newspapers summarizer :newspaper:")
st.sidebar.markdown("# YouTube summarizer :tv:️")
# chat
st.title("For print to PDF just type Crtl + P.")
# Get LLM API key from user
llm_api_key = st.text_input("Please enter your LLM API key:", "")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Please, paste the YouTube's URL here."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = prompt

    # Display assistant response in chat message container
    time.sleep(1)  # simulate response delay (1 second)
    yt_method(response, llm_api_key)
