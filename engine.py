"""News summarizer
        News Brief is an AI prototype
        that serves to summarise news or videos from
        YouTube or web newspapers.
        Please, if you are going to use this software first
        you must first get an API Key to put in the section
        API KEY SECTION.
        Follow the instructions in the link: https://console.groq.com/docs/overview
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import streamlit as st
import re
import math
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse
from groq import Groq

def api_call(api_key):
    client = Groq(api_key=api_key)
    return client

def get_youtube_video_id(url: str) -> str:
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    result = re.search(pattern, url)
    return result.group(1) if result else None

def extract_phrases_and_concatenate(json_data: dict) -> str:
    sentence = []
    if isinstance(json_data, list):
        for item in json_data:
            if 'text' in item:
                sentence.append(item['text'])
    else:
        print("Unexpected JSON format")
    return " ".join(sentence)

def divide_and_resume(speech: str, num_parts: int, api_key: str, lang: str, selected_limit: int) -> None:
    words = speech.split()
    words_per_part = math.ceil(len(words) / num_parts)
    parts = [" ".join(words[i * words_per_part:(i + 1) * words_per_part]) for i in range(num_parts)]
    client = api_call(api_key)
    for i in range(min(num_parts, selected_limit if selected_limit else num_parts)):
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": parts[i]}],
            model="llama3-8b-8192",
            temperature=0,
        )
        response = chat_completion.choices[0].message.content
        with st.chat_message("assistant"):
            st.markdown(f"AI: {response}")
        st.session_state.messages.append({"role": "assistant", "content": response})

def answer_chat(prompt: str) -> None:
    response = f"AI: {prompt}"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

def split_speech(speech: str) -> int:
    return math.ceil(len(speech.split()) / 3000)

def validate_youtube_link(url: str) -> bool:
    youtube_patterns = [
        r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+',
        r'^(https?://)?(www\.)?(youtube\.com/embed/)[\w-]+',
        r'^(https?://)?(www\.)?(youtube\.com/shorts/)[\w-]+'
    ]
    return any(re.match(pattern, url) for pattern in youtube_patterns)

def get_youtube_transcript(video_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(directorio_actual, 'chromedriver')
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get(video_url)
        time.sleep(5)
        try:
            transcript_button = driver.find_element(By.CSS_SELECTOR, "#primary-button > ytd-button-renderer > yt-button-shape > button > yt-touch-feedback-shape > div > div.yt-spec-touch-feedback-shape__fill")
            driver.execute_script("arguments[0].click();", transcript_button)
            time.sleep(3)
        except Exception:
            return "No se encontró botón de transcripción."
        transcript_content = driver.find_element(By.CSS_SELECTOR, "#content > ytd-transcript-search-panel-renderer").text
        return transcript_content
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        driver.quit()

def yt_method(url_youtube: str, llm_api_key: str, language: str, selected_limit: int) -> None:
    if validate_youtube_link(url_youtube):
        transcript = get_youtube_transcript(url_youtube)
        if "Error" in transcript or "No se encontró" in transcript:
            answer_chat("No se pudo obtener la transcripción del video.")
            return
        split = split_speech(transcript)
        divide_and_resume(transcript, split, llm_api_key, language, selected_limit)
    else:
        answer_chat("The provided URL is not a valid YouTube video link.")
