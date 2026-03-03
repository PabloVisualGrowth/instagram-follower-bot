import os
import time
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Load credentials
load_dotenv()
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")

STEALTH_JS = '''
(() => {
    delete Object.getPrototypeOf(navigator).webdriver;
    Object.defineProperty(navigator, 'plugins', {
        get: () => [
            {0: {type: 'application/x-google-chrome-pdf', description: 'Portable Document Format'}},
            {1: {type: 'application/pdf', description: 'Portable Document Format'}}
        ]
    });
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-ES','en','es']
    });
})();
'''

def setup_driver():
    options = Options()
    # Stealth arguments
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=es-ES")
    options.add_argument("--headless=new") # Required for cloud
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Inject stealth JS
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": STEALTH_JS})
    
    return driver

def login(driver):
    print("Iniciando sesión en Instagram con Ultra-Sigilo...")
    driver.get("https://www.instagram.com/accounts/login/")
    wait = WebDriverWait(driver, 15)
    
    # Accept cookies
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Permitir todas las cookies')] | //button[contains(text(), 'Aceptar todas')]")))
        print("Botón de cookies encontrado. Click...")
        cookie_btn.click()
        time.sleep(2)
    except:
        pass
        
    # Fill login form - Stealthy interaction
    try:
        user_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@name='username' or @name='email']")))
        pass_field = driver.find_element(By.XPATH, "//input[@name='password' or @name='pass']")
        
        print("Campos encontrados. Typing...")
        actions = webdriver.ActionChains(driver)
        
        # Type username naturally
        actions.move_to_element(user_field).click().perform()
        time.sleep(1)
        for char in USERNAME:
            user_field.send_keys(char)
            time.sleep(0.05)
            
        time.sleep(0.5)
        # Type password naturally
        actions.move_to_element(pass_field).click().perform()
        time.sleep(1)
        for char in PASSWORD:
            pass_field.send_keys(char)
            time.sleep(0.05)
            
        time.sleep(1.5)
        
        # Click login button
        login_btn = None
        for sel in ["button[type='submit']", "//button[contains(., 'Iniciar sesión')]", "//div[text()='Iniciar sesión']"]:
            try:
                if sel.startswith("//"): login_btn = driver.find_element(By.XPATH, sel)
                else: login_btn = driver.find_element(By.CSS_SELECTOR, sel)
                if login_btn.is_displayed(): break
            except: pass
            
        if login_btn:
            print("Haciendo click en Iniciar sesión...")
            driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
            time.sleep(1)
            # Try a coordinated click
            actions.move_to_element(login_btn).click().perform()
            time.sleep(1)
            # Fallback JS click if still on page
            if "login" in driver.current_url:
                print("Aún en login, intentando click directo JS...")
                driver.execute_script("arguments[0].click();", login_btn)
        else:
            print("Botón no encontrado, enviando ENTER...")
            pass_field.send_keys(Keys.ENTER)
            
    except Exception as e:
        print(f"Error en login sigiloso: {e}")

    print("Esperando redirección (20s)...")
    time.sleep(20)
    driver.save_screenshot("after_ultra_stealth_login.png")
    
    try:
        not_now_save = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(text(), 'Ahora no')] | //button[contains(text(), 'Ahora no')]")))
        not_now_save.click()
    except:
        pass
        
    time.sleep(2)
    try:
        not_now_notify = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ahora no')]")))
        not_now_notify.click()
    except:
        pass

def get_followers(driver):
    wait = WebDriverWait(driver, 20)
    
    print("Navegando al Perfil desde la barra lateral...")
    try:
        # Click on 'Profile' link in sidebar
        # Using a broad selector for the profile link which usually contains 'Profile' or the username
        profile_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/" + USERNAME + "/')] | //span[text()='Perfil']//ancestor::a")))
        driver.execute_script("arguments[0].click();", profile_link)
        time.sleep(5)
        driver.save_screenshot("profile_page_reached.png")
    except Exception as e:
        print(f"Error navegando al perfil: {e}")
        driver.get(f"https://www.instagram.com/{USERNAME}/") # Fallback to direct if UI fails
        time.sleep(5)

    print("Abriendo el modal de seguidores...")
    try:
        # Click on the 'followers' link on the profile page
        followers_trigger = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/followers/')]")))
        driver.execute_script("arguments[0].click();", followers_trigger)
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        time.sleep(3)
        driver.save_screenshot("followers_modal_opened.png")
    except Exception as e:
        print(f"Error abriendo el modal de seguidores: {e}")
        return []

    # Find the scrollable area
    scroll_box = driver.execute_script("""
        return document.querySelector('div[role="dialog"] ._aano') || 
               document.querySelector('div[role="dialog"] div[style*="overflow-y: auto"]') ||
               document.querySelector('div[role="dialog"] div[style*="overflow: hidden auto"]');
    """)
    
    if not scroll_box:
        print("Error: No se encontró el área de scroll en el modal.")
        return []

    followers = set()
    last_height = 0
    
    print("Extrayendo seguidores reales (Filtro preciso: Suprimir)...")
    for i in range(15):
        # Refined JS: More robust row detection and diagnostic text return
        js_extract = """
        let found = [];
        let rows = document.querySelectorAll('div[role="dialog"] [class*="x1dm5otj"], div[role="dialog"] li, div[role="dialog"] div[style*="flex-direction: column"] > div');
        
        rows.forEach(row => {
            let rowText = row.innerText || "";
            let lowerText = rowText.toLowerCase();
            if (lowerText.includes('suprimir') || lowerText.includes('eliminar')) {
                // Find any link that looks like a username
                let links = Array.from(row.querySelectorAll('a[href*="/"]'));
                let name = "";
                for (let link of links) {
                    let n = link.innerText.split('\\n')[0].trim();
                    if (n && !n.includes(' ') && n.length > 2) {
                        name = n;
                        break;
                    }
                }
                if (name) {
                    found.push({name: name, fullText: rowText.replace(/\\n/g, ' | ')});
                }
            }
        });
        return { results: found };
        """
        
        result = driver.execute_script(js_extract)
        results = result.get('results', [])
            
        for item in results:
            followers.add(item['name'])
        
        # Scroll down
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
        time.sleep(2)
        
        new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
        if new_height == last_height:
            time.sleep(1)
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_box)
            if new_height == last_height:
                break
        last_height = new_height
        print(f"Scroll {i+1}, seguidores reales detectados: {len(followers)}")
        if "olbapperez" in followers:
            print("¡Confirmado olbapperez encontrado!")
        
    print(f"Finalizado. Se han encontrado {len(followers)} seguidores reales.")
    
    # Print the specific list requested by the user
    print("\n--- LISTA DE SEGUIDORES REALES ---")
    sorted_followers = sorted(list(followers))
    for f in sorted_followers:
        print(f)
    print("---------------------------\n")
    
    return sorted_followers

def save_and_compare(new_followers_list):
    db_path = "followers.json"
    
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            old_followers = set(json.load(f))
    else:
        old_followers = set()
    
    current_followers = set(new_followers_list)
    new_ones = current_followers - old_followers
    unfollowed = old_followers - current_followers
    
    # Only show new followers if we already had a record (don't show everyone as 'new' on first run)
    if old_followers:
        if new_ones:
            print("\n!!! NUEVOS SEGUIDORES DETECTADOS !!!")
            for fan in new_ones:
                print(f"- {fan}")
        else:
            print("\nNo hay nuevos seguidores desde la última revisión.")
            
        if unfollowed:
            print("\nUsuarios que te han dejado de seguir:")
            for quitter in unfollowed:
                print(f"- {quitter}")
    else:
        print("\nPrimera ejecución: Guardando lista inicial de seguidores.")

    results = {
        "new_followers": list(new_ones),
        "unfollowers": list(unfollowed),
        "first_run": not old_followers
    }

    # Always update the database
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(list(current_followers), f, indent=4)
        
    return results

def run_bot():
    """Main function to run the bot and return results."""
    driver = setup_driver()
    try:
        login(driver)
        f_list = get_followers(driver)
        results = save_and_compare(f_list)
        driver.save_screenshot("ultimo_scrappeo.png")
        return {
            "success": True,
            "followers": f_list,
            "changes": results
        }
    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("error_scrappeo.png")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        driver.quit()

if __name__ == "__main__":
    run_bot()
