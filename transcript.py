from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
# Configuración de Chrome en modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# ruta del chromedriver
directorio_actual = os.path.dirname(os.path.abspath(__file__))
chromedriver_path = os.path.join(directorio_actual, 'chromedriver')
# Configurar el driver
service = Service(chromedriver_path)  # Asegúrate de que la ruta sea correcta
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_youtube_transcript(video_url):
    driver.get(video_url)
    time.sleep(5)  # Esperar a que la página cargue
    
    try:
        # Hacer clic en el botón de transcripción
        transcript_button = driver.find_element(By.CSS_SELECTOR, "#primary-button > ytd-button-renderer > yt-button-shape > button > yt-touch-feedback-shape > div > div.yt-spec-touch-feedback-shape__fill")
        driver.execute_script("arguments[0].click();", transcript_button)
        time.sleep(3)
        
        # Obtener el contenido de la transcripción
        transcript_content = driver.find_element(By.CSS_SELECTOR, "#content > ytd-transcript-search-panel-renderer").text
        return transcript_content
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    video_link = "https://www.youtube.com/watch?v=JzJ4ht0mraA"
    transcript = get_youtube_transcript(video_link)
    print(transcript)

