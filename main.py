"""News summarizer
        News Brief is an AI prototype
        that serves to summarise news or videos from
        YouTube or web newspapers.
        Please, if you are going to use this software first
        you must first get an API Key to put in the section
        API KEY SECTION.
        Follow the instructions in the link: https://console.groq.com/docs/overview
"""
# import
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import re

# instance object Groq
client = Groq(
    api_key="PLEASE, PUT YOUR API KEY HERE"  # os.environ.get("GROQ_API_KEY"),
)


def get_youtube_video_id(url):
    """
    Extracts the video ID from a YouTube URL.

    Args:
        url (str): The YouTube URL.

    Returns:
        str: The ID of the video if found, otherwise None.
    """
    # Pattern to find the YouTube video ID
    patron = r'(?:v=|\/)([0-9A-Za-z_-]{11})'
    resultado = re.search(patron, url)
    return resultado.group(1) if resultado else None


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


# Prueba del script
def resume_transcript(id_video):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": """STRICT INFORMATION PROCESSING INSTRUCTIONS:
                            1. OUTPUT FORMAT:
                            - Executive summary in maximum 5 points
                            - Neutral and direct language
                            - No subjective assessments
                            - Style: informative and objective
                            
                            2. MANDATORY ANALYSIS:
                            - Identify MAIN FACTS
                            - Extract CONCRETE DATA
                            - Contextualize without personal opinion
                            - Prioritize verifiable information
                            
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
                            
                            {id_video}""".format(id_video=id_video)
            }
        ],
        model="llama3-8b-8192",
        temperature=0,
        max_tokens=1000,
        n=1,
    )
    print(chat_completion.choices[0].message.content)


if __name__ == "__main__":
    # Prompt user to enter YouTube URL
    url_youtube = input("Enter the URL of the YouTube video: ").strip()
    id_video = get_youtube_video_id(url_youtube)
    json = YouTubeTranscriptApi.get_transcript(id_video, languages=['es'])
    text = extract_phrases_and_concatenate(json)
    resume_transcript(text)
