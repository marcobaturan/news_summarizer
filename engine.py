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

# import
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
import re
import math
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin, urlparse


def api_call(api_key):
    # instance object Groq
    client = Groq(
        api_key=api_key,
    )
    return client


def get_youtube_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.

    Args:
        url (str): The YouTube URL.

    Returns:
        str: The ID of the video if found, otherwise None.
    """
    # Pattern to find the YouTube video ID
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    result = re.search(pattern, url)
    return result.group(1) if result else validate_youtube_link(url)


def extract_phrases_and_concatenate(json_data: dict) -> str:
    """
    Extracts sentences from a JSON file and concatenates them into a single text variable.

    Args:
        json_data (dict): The JSON content loaded as a dictionary.

    Returns:
        str: All text concatenated into a single string.
    """
    # Verify that the JSON contains an expected field with transcripts.
    sentence = []
    if isinstance(json_data, list):
        for item in json_data:
            # Make sure that the ‘text’ field exists in each element.
            if 'text' in item:
                sentence.append(item['text'])
    else:
        print("Unexpected JSON format")

    # Concatenate all sentences into one variable
    full_text = " ".join(sentence)
    return full_text


def divide_and_resume(speech: str, num_parts: int, api_key: str, lang: str, selected_limit: int, ) -> tuple[
    str, str | None]:
    """Divide a given text into parts and process them with a language model.

        Args:
            speech (str): The input text to be processed
            num_parts (int): Number of parts to divide the text into
            api_key (str): API key for making language model calls
            lang (str): Target language for processing
            selected_limit (int, optional): Limit on number of parts to process.
                                            0 means process all parts. Defaults to 0.

        Returns:
            Tuple containing:
            - List of original text parts
            - List of processed results (or None if processing fails)"""

    # Validate input parameters
    if num_parts <= 0:
        st.session_state.messages.append({"role": "assistant", "content": "Maximum cycle limit reached"})

    # Split text into words
    words = speech.split()
    total_words = len(words)

    # Calculate words per part
    words_per_part = math.ceil(total_words / num_parts)

    # Divide text into parts of approximately equal word count
    parts = []
    for i in range(num_parts):
        start = i * words_per_part
        end = (i + 1) * words_per_part
        part = ' '.join(words[start:end])
        parts.append(part)

    # Determine how many parts to process
    # If selected_limit is 0 or greater than total parts, process all parts
    process_limit = (
        num_parts if selected_limit == 0 or selected_limit > num_parts
        else selected_limit
    )

    # Process each part with LLM
    results = []
    counter = 0
    client = api_call(api_key)
    for i in range(process_limit):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": """STRICT INFORMATION PROCESSING INSTRUCTIONS:
                                 0. Inner control thought:
                                     - Review internally step by step all the information received and in a logical way, be careful in the process.
                                     - No factual inaccuracies.
                                     - No personal opinions
                                     - No emotional tone
                                     - No subjective statements
                                     - No personal anecdotes
                                     - No political opinions
                                     - No sarcasm
                                     - No negation
                                     - No exaggeration
                                     - No irony
                                 1. OUTPUT FORMAT:
                                 - Executive summary in maximum 5 points
                                 - Neutral and direct language
                                 - No subjective assessments
                                 - Style: informative and objective
                                 - Do not be verbatim.

                                 2. MANDATORY ANALYSIS:
                                 - Identify MAIN FACTS
                                 - Extract CONCRETE DATA
                                 - Contextualize without personal opinion
                                 - Prioritize verifiable information
                                 - Extract key points from the text
                                 - Read between the lines.
                                 - Which important background info has author omitted? 
                                 - What are his political positions? 
                                 - What was his intent in publishing this?

                                 3. RESTRICTIONS:
                                 - Prohibited use of emotional adjectives
                                 - Avoid personal interpretations
                                 - Maximum linguistic neutrality
                                 - Mathematical precision in description

                                 4. STRUCTURE:
                                 [Objective headline]
                                 - Point 1: What happened
                                 - Point 2: Who was involved
                                 - Point 3: When and where
                                 - Point 4: Immediate consequences
                                 - Point 5: Relevant context
                                 
                                 5. Flow work in divided resume:
                                 - If the resume is divided then retain the previous analysis to concatenate the process.
                                 
                                 6. Imperative: translate to language: {language}
                                 {id_video}""".format(id_video=parts[i], language=lang)
                }
            ],
            model="llama3-8b-8192",
            temperature=0,
        )

        prompt = "PART: " + str(counter), chat_completion.choices[0].message.content
        response = f"AI: {prompt[0]} - {prompt[1]}"
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response[0]})


def answer_chat(prompt: str) -> None:
    """
    Displays an assistant response in the chat interface.

    Args:
        prompt (str): The text to be displayed as the assistant's response.

    Returns:
        None
    """
    response = f"AI: {prompt}"
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response[0]})


def split_speech(speech: str) -> int:
    """
        Calculates the number of parts to divide a given speech into, based on a threshold of 3000 words per part.

        Args:
            speech (str): The input speech to be divided.

        Returns:
            int: The number of parts to divide the speech into.
    """
    words = speech.split()
    divide = math.ceil(len(words) / 3000)
    return divide


def validate_youtube_link(url: str) -> bool:
    """
        Validates whether a given URL is a valid YouTube link.

        Args:
            url (str): The URL to be validated.

        Returns:
            bool: True if the URL is a valid YouTube link, False otherwise.
    """
    # Regular expression patterns for different YouTube link formats
    youtube_patterns = [
        r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+',
        r'^(https?://)?(www\.)?(youtube\.com/embed/)[\w-]+',
        r'^(https?://)?(www\.)?(youtube\.com/shorts/)[\w-]+'
    ]

    # Check if the URL matches any YouTube patterns
    for pattern in youtube_patterns:
        if re.match(pattern, url):
            return True


def yt_method(url_youtube: str, llm_api_key: str, language: str, selected_limit: int) -> None:
    """
    Retrieves the transcript of a YouTube video and generates a summary.

    Args:
        url_youtube (str): The URL of the YouTube video.
        llm_api_key (str): The API key for the LLM model.
        language (str): The language of the transcript.
        selected_limit (int): The number of summaries to generate.

    Returns:
        None

    Raises:
        ValueError: If the YouTube URL is invalid or the transcript cannot be retrieved.

    Notes:
        This function uses the YouTubeTranscriptApi to retrieve the transcript of the video.
        It then uses the extract_phrases_and_concatenate function to extract phrases from the transcript
        and concatenate them into a single string. The speech is then split into parts based on a threshold
        of 3000 words using the split_speech function. Finally, the divide_and_resume function is used
        to generate and display the summaries.
    """
    # Validate the YouTube URL
    global json
    if validate_youtube_link(url_youtube):
        # Get the video ID from the URL
        id_video = get_youtube_video_id(url_youtube)
        # Retrieve the transcript of the video in the specified language
        json = YouTubeTranscriptApi.get_transcript(id_video,  languages=['es', 'en', 'fr', 'de', 'it', 'hr', 'pt'], proxies={"https:":"https://8c5906b99fbd1c0bcd0f916d545c565ade3e4f4217dafebc86980c29d70fb8f762c7b52634015e6ee91455c0ebf218b7bdc251d17cde3b5d7a135776a83b0d3b:ttarelx4u19q@proxy.toolip.io:31111"})
        # Extract phrases and concatenate them into a single string
        text = extract_phrases_and_concatenate(json)

        # Split the speech into parts based on a threshold of 3000 words
        split = split_speech(text)

        # Generate and display the summaries
        divide_and_resume(text, split, llm_api_key, language, selected_limit)
    else:
        # Display a message if the URL is not a valid YouTube link
        answer_chat("The provided URL is not a valid YouTube video link.")


def np_method(text: str, llm_api_key: str, language: str, selected_limit: str) -> None:
    """
    Generates a summary of a newspaper article using the provided text and LLM API key.

    Args:
        text (dict): A dictionary containing the text of the newspaper article.
        llm_api_key (str): The API key for the LLM model.
        language (str): The language of the text.
        selected_limit (int): The number of summaries to generate.

    Returns:
        None

    Raises:
        ValueError: If the text is not a valid dictionary or the LLM API key is invalid.

    Notes:
        This function uses the provided text to generate a summary using the LLM API.
        It first extracts the linked pages text from the dictionary, then splits the text into parts based on a threshold of 3000 words.
        Finally, it uses the divide_and_resume function to generate and display the summaries.
    """
    # Prompt user to enter Newspaper URL
    if True:
        # Extract linked pages text from the dictionary
        dict_to_strign = "{}".format(text["linked_pages_text"])

        # Split the speech into parts based on a threshold of 3000 words
        split = split_speech(dict_to_strign)

        # Generate and display the summaries
        divide_and_resume(dict_to_strign, split, llm_api_key, language, selected_limit)
    else:
        # Display a message if the URL is not a valid Newspaper article link
        answer_chat("The provided URL is not a valid Newspaper article link. Format must be https://website.com")


"""
Web Page Text Extraction Utility

This module provides a robust mechanism for extracting textual content
from web pages using modern web scraping techniques. The utility focuses
on retrieving meaningful text while maintaining a clean, pythonic approach.

Author: Assistant
Date: November 2024
Licence: MIT
"""


def extract_webpage_text(url: str, timeout: int = 10, max_depth: int = 0) -> dict:
    """
    Extracts all readable text content from a specified web page and its first-level links.

    This function retrieves the HTML content of a given URL and systematically extracts
    human-readable text, filtering out navigation elements, scripts, and other non-textual
    components. It can also crawl first-level links for additional text extraction.

    Args:
        url (str): The fully qualified URL of the webpage to scrape.
        timeout (int, optional): Maximum time in seconds to wait for server response.
                                 Defaults to 10 seconds.
        max_depth (int, optional): Maximum depth of link crawling. Defaults to 1 (first-level links).

    Returns:
        dict: A dictionary containing:
            - 'main_page_text': Text extracted from the main page
            - 'linked_pages_text': Dictionary of texts from first-level links

    Raises:
        requests.RequestException: If there are network-related issues.
        ValueError: If the URL is invalid or cannot be processed.
    """
    # Initialise logging for tracking potential extraction issues
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up headers to mimic browser behaviour
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Function to extract text from a webpage
    def extract_text_from_page(page_url):
        try:
            # Perform HTTP request
            response = requests.get(page_url, headers=headers, timeout=timeout)
            response.raise_for_status()

            # Parse HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements which do not contain readable text
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            # Extract text from all paragraph, heading, and div elements
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'])

            # Concatenate text, stripping unnecessary whitespace
            extracted_text = ' '.join(element.get_text(strip=True) for element in text_elements)

            # Log successful extraction
            logger.info(f"Successfully extracted text from {page_url}")
            return extracted_text

        except requests.RequestException as network_error:
            logger.error(f"Network error occurred while extracting {page_url}: {network_error}")
            return f"Network error occurred: {network_error}"

    # Main extraction process
    try:
        # Extract text from the main page
        main_page_text = extract_text_from_page(url)

        # Prepare result dictionary
        result = {
            'main_page_text': main_page_text,
            'linked_pages_text': {}
        }

        # Extract first-level links
        soup = BeautifulSoup(requests.get(url, headers=headers, timeout=timeout).text, 'html.parser')

        # Get the base domain to ensure we stay on the same site
        base_domain = urlparse(url).netloc

        # Find all links on the page
        links = soup.find_all('a', href=True)

        # Set to keep track of processed URLs to avoid duplicates
        processed_urls = set()

        # Process first-level links
        for link in links:
            # Construct absolute URL
            full_link = urljoin(url, link['href'])

            # Check if the link is on the same domain and hasn't been processed
            if (urlparse(full_link).netloc == base_domain and
                    full_link not in processed_urls and
                    full_link != url):
                try:
                    # Extract text from the linked page
                    linked_page_text = extract_text_from_page(full_link)

                    # Store the extracted text
                    result['linked_pages_text'][full_link] = linked_page_text

                    # Add to processed URLs
                    processed_urls.add(full_link)

                except Exception as e:
                    logger.error(f"Error processing link {full_link}: {e}")

        return result

    except requests.RequestException as network_error:
        return {"error": f"Network error occurred: {network_error}"}





