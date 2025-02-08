import random
import time
import undetected_chromedriver as uc # Driver modificado
from fake_useragent import UserAgent # Cambiar de user-agent dinámicamente
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

#Evitar el modo “headless” básico
#Usa undetected-chromedriver (una versión de Selenium para evitar detección):
driver = uc.Chrome(use_subprocess=True)
driver.get("https://www.idealista.com")

# Opciones de Chrome Stealth
# Configura argumentos específicos para evitar huellas:
options = uc.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--incognito") # Modo incognito

# Rotación de User-Agent y Resolución de pantalla
ua = UserAgent()
user_agent = ua.random
options.add_argument(f"user-agent={user_agent}")

# Simulación de resoluciones
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
    "width": 1366,
    "height": 768,
    "deviceScaleFactor": 1,
    "mobile": False
})

# Usa proxies residenciales rotativos, evitando el bloqueo por IP
# Opciones: BrightData, Oxylabs, Smartproxy
proxy_options = {
    "proxy": {
        "http": "http://usuario:password@ip_proxy:puerto",
        "verify_ssl": False
    }
}

driver = webdriver.Chrome(seleniumwire_options=proxy_options)

# Simular comportamiento humano
# Movimientos de ratón y desplazamiento
actions = ActionChains(driver)
element = driver.find_element(By.TAG_NAME, "body")
actions.move_to_element(element).perform()

# tiempos de espera aleatorios
time.sleep(random.uniform(1.5, 4.5)) # Espera entre 1.5 y 4.5


# Evitar huellas de navegador
# Deshabilita WebDriver y sobrescribe el navigator.webdriver
driver.execute_script("window.navigator.chrome = {runtime: {}};")
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver' {
            get: () => undefined
        });
    """
})

# Manejo de cookies y sesiones
# Limpia cookies y almacenamiento local entre sesiones
driver.delete_all_cookies()
driver.execute_script("window.localStorage.clear();")

# Varía los horarios (no siempre a la misma hora)
# Máximo 1-2 páginas por minuto
# Usa rutas de navegación no lineales (no siempre vayas a la siguiente página, sino vuelve ocasionalmente a otro lado)
# Si aparece un CAPTCHAs:
#   - Detén el scraping inmediatamente y cambia de IP/proxy
#   - Usa servicios de resolución de CAPTCHA como 2Captcha o Anti-Captcha
