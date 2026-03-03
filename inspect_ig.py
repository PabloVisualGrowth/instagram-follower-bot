import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")

def inspect():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--lang=es-ES")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(10)
        
        print("--- DOM INSPECTION ---")
        
        # Accept cookies first to see the form
        try:
            cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'todas las cookies')]")
            cookie_btn.click()
            time.sleep(5)
        except: pass

        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, inp in enumerate(inputs):
            print(f"Input {i}: name='{inp.get_attribute('name')}', type='{inp.get_attribute('type')}', placeholder='{inp.get_attribute('placeholder')}'")
            
        with open("ig_login_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect()
