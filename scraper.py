import random
import pandas as pd
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def tiempo_esperar():
    return random.uniform(1.5, 4.5)

def aplicar_precio(minimo, maximo):
    filtro_min = f"con-precio-desde_{minimo}" if minimo not in ("", 0, None) else ""
    filtro_max = f"con-precio-hasta_{maximo}" if maximo not in ("", 0, None) else ""

    if filtro_max != "":
        filtro_min = filtro_min.replace("con-", "")

    if filtro_min and filtro_max:
        return f"{filtro_max},{filtro_min}"

    return filtro_min or filtro_max

def extraer_info(data, pagina_actual):
    soup = BeautifulSoup(data, "html.parser")
    pisos = []

    anuncios = soup.find_all('div', class_="item-info-container")
    if pagina_actual == 1: # Eliminamos el primer elemento que no corresponde con un anuncio en la primera página
        anuncios.pop(0)

    for anuncio in anuncios:
        try:
            localizacion = anuncio.find("a", class_="item-link").text.strip()
        except AttributeError:
            localizacion = "N/A"
        try:
            precio = anuncio.find("span", class_="item-price h2-simulated").text.replace("/mes", "").strip()
        except AttributeError:
            precio = "N/A"

        detalles_div = anuncio.find("div", class_="item-detail-char")
        detalles = detalles_div.find_all("span", class_="item-detail") if detalles_div else []

        habitaciones = detalles[0].text.replace("hab.", "").strip() if len(detalles) > 0 else "N/A"
        espacio = detalles[1].text.replace("m²", "").strip() if len(detalles) > 1 else "N/A"
        planta = detalles[2].text.strip() if len(detalles) > 2 else "N/A"

        pisos.append({
            "localizacion": localizacion,
            "precio": precio,
            "habitaciones": habitaciones,
            "espacio": espacio,
            "planta": planta
        })

    return pisos


if __name__ == "__main__":
    # Datos a pedir
    precio_min = input("Precio mínimo del piso: ")
    precio_max = input("Precio máximo del piso: ")
    num_habitaciones = input("Numero de habitaciones mínimo (0 (estudio), 1, 2, 3, 4 o más): ")
    opcion = input("¿Comprar o Alquilar?: ")

    entre_valores = aplicar_precio(precio_min, precio_max)
    boton_habitaciones = f"rooms_{num_habitaciones}" if int(num_habitaciones) < 4 else f"rooms_4_more"
    opcion_alquiler_compra = "venta-viviendas" if opcion.strip().lower() == "comprar" else "alquiler-viviendas"

    url_target = f"https://www.idealista.com/{opcion_alquiler_compra}/cadiz-cadiz/{entre_valores}"

    # Rotación de perfiles de user-agent
    ua = UserAgent()
    user_agent = ua.random

    # Opciones de Chrome Stealth
    # Configuramos argumentos específicos para evitar huellas
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--incognito") # Modo incognito

    # Creación del navegador con las opciones
    browser = uc.Chrome(options=options)

    # Simulación de resoluciones variables
    browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    resoluciones = [
        (1280, 720), (1366, 768), (1440, 900), (1536, 864)
    ]

    ancho, alto = random.choice(resoluciones)

    browser.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "width": ancho,
        "height": alto,
        "deviceScaleFactor": 1,
        "mobile": False
    })

    # Evitar huellas de navegador
    # Deshabilitamos WebDriver y sobrescribimos el navigator.webdriver
    browser.execute_script("window.navigator.chrome = {runtime: {}};")
    browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver' {
                get: () => undefined
            });
        """
    })
    # Navegar a la página
    browser.get(url_target)
    actions = ActionChains(browser)

    # Rechazar cookies
    button_rechazar = ((WebDriverWait(browser, 10)).
                       until(EC.presence_of_element_located((By.CSS_SELECTOR, '[id=\"didomi-notice-disagree-button\"]'))))

    # Aplicar filtro de habitaciones
    check_habitaciones = (WebDriverWait(browser, 10).
                          until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[id="{boton_habitaciones}"]'))))

    # Simular comportamiento humano con movimientos de ratón y desplazamiento
    actions.move_to_element(button_rechazar).pause(tiempo_esperar()).click().perform()
    actions.move_to_element(check_habitaciones).pause(tiempo_esperar()).click().perform()

    # url_target adquiere el filtrado de habitaciones
    url_target = browser.current_url

    pisos = []
    pagina = 1
    while True:
        # Tiempo de espera aleatorio
        time.sleep(tiempo_esperar())
        # Extraer el código fuente
        html = browser.page_source
        # Extraer los datos del código fuente
        pisos.extend(extraer_info(html,pagina))
        print(f"Extraido datos de la página {pagina}")
        try: # Esperar a que el botón de 'siguiente' esté disponible y clickarlo
            boton_siguiente = (WebDriverWait(browser, 10)
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.icon-arrow-right-after"))))
            actions.move_to_element(boton_siguiente).pause(tiempo_esperar()).click().perform()
            pagina += 1
        except Exception: # Si no hay 'siguiente' salta excepción y rompemos el bucle
            break

    df = pd.DataFrame(pisos)
    df.to_csv('pisos_idealistas.csv', index=False, encoding="utf-8")

    # Manejo de cookies y sesiones
    # Limpiamos cookies y almacenamiento local entre sesiones
    browser.delete_all_cookies()
    browser.execute_script("window.localStorage.clear();")

    browser.quit()
