# import
import streamlit as st
from engine import *
import time

# main body
st.set_page_config(page_title="Welcome",
                   page_icon=":newspaper:")
# header
st.markdown("# Newspapers summarizer :newspaper:")
# sidebar
st.sidebar.markdown("# Welcome to News summarizer! 👋")
st.sidebar.markdown("# Newspapers summarizer :newspaper:")
st.sidebar.markdown("# YouTube summarizer :tv:️")
# body chat
st.title("For print to PDF just type Crtl + P.")
# Get LLM API key from user
llm_api_key = st.text_input("Please enter your LLM API key:", "")
language = st.selectbox("Please, select a language: ", ["Spanish", "Croatian", "German", "English"])
limit = st.selectbox("Please, select nº of articles: ",
                     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 23, 24, 25])
depth = st.selectbox("Please, select depth of search: ", [0, 1])
# Initialize chat history
if "newspapers" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Please, paste the website's URL here. Format: https://example.com"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # response = extract_webpage_text(url=prompt)
    response = extract_webpage_text(url=prompt, timeout=10, max_depth=depth)
    # Display assistant response in chat message container
    time.sleep(1)  # simulate response delay (1 second)
    # pass from dictionary the section of linked pages to the np method for feed the llm
    np_method(response, llm_api_key, language=language, selected_limit=limit)
