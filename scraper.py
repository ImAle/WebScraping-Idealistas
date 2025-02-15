import random
import tempfile
import os
from datetime import datetime
import pandas as pd
import time
import ftp_client as ftp
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

def extraer_info(pisos):
    info = []

    for piso in pisos:
        time.sleep(tiempo_esperar()-1)
        browser.get(piso)
        html = BeautifulSoup(browser.page_source, 'html.parser')

        try:
            localizacion = html.find('span', class_='main-info__title-main').text.strip()
        except AttributeError:
            localizacion = "N/A"

        try:
            elemento_precio = html.find('span', class_='info-data-price')
            precio = elemento_precio.find('span', class_='txt-bold').text.strip() + ' €'
        except AttributeError:
            precio = "N/A"

        try:
            # Extraer características
            div_caracteristicas = html.find('div', class_='info-features')
            spans = div_caracteristicas.find_all('span')

            metros_cuadrados = spans[0].text.strip() if len(spans) > 0 else "N/A"
            habitaciones = spans[1].text.strip() if len(spans) > 1 else "N/A"
            planta = spans[2].text.strip() if len(spans) > 2 else "N/A"
        except AttributeError:
            metros_cuadrados = habitaciones = planta = "N/A"

        try:
            # Extraer características básicas (excluyendo m² y habitaciones)
            div_extra = html.find('div', class_='details-property_features')
            items_extra = [
                li.text.strip() for li in div_extra.find_all('li')
                if 'm²' not in li.text and 'habitacion' not in li.text.lower()
            ]
        except AttributeError:
            items_extra = []

        info.append({
            "localizacion": localizacion,
            "habitaciones": habitaciones,
            "precio": precio,
            "espacio": metros_cuadrados,
            "planta": planta,
            "extras": items_extra,
            "link": piso,
        })

    return info

# Extraigo los links a los espejos
def obtener_enlace(data, pagina_actual, url_base):
    soup = BeautifulSoup(data, "html.parser")
    pisos = []

    anuncios = soup.find_all('div', class_="item-info-container")

    for anuncio in anuncios:
        try:
            anuncio_enlace = anuncio.find("a", class_="item-link")
            enlace = anuncio_enlace['href']
        except AttributeError:
            enlace = None

        if enlace is not None and "inmueble" in enlace:
            pisos.append("https://www.idealista.com" + enlace)

    return pisos

def guardar_archivo(archivo):
    default_nombre = f"idealistas_{datetime.now().strftime('%Y_%m_%d-%H')}.csv"

    opcion = input("¿Desea guardar el archivo en el servidor (S) o localmente (L)? ").strip().upper()
    if opcion == "S":
        nuevo_nombre = input(f"Nombre remoto para el archivo (deje vacío para usar '{default_nombre}'): ").strip()
        if not nuevo_nombre:
            nuevo_nombre = default_nombre
        if not nuevo_nombre.endswith(".csv"):
            nuevo_nombre += ".csv"
        try:
            temp_dir = tempfile.gettempdir()
            temp_filename = os.path.join(temp_dir, nuevo_nombre)
            with open(temp_filename, "w", newline="", encoding="utf-8") as f:
                f.write(archivo)

            print(f"Archivo preparado para subir remotamente como '{nuevo_nombre}'.")

            # Llamamos al cliente FTP pasándole la ruta con el nombre deseado
            ftp.main(temp_filename)
            os.remove(temp_filename)
        except Exception as e:
            print("Error al guardar para subir al servidor:", e)

    elif opcion == "L":
        nuevo_nombre = input(f"Nombre del archivo a guardar (deje vacío para usar '{default_nombre}'): ").strip()
        if not nuevo_nombre:
            nuevo_nombre = default_nombre
        if not nuevo_nombre.endswith(".csv"):
            nuevo_nombre += ".csv"
        try:
            with open(nuevo_nombre, "w", newline="", encoding="utf-8") as f:
                f.write(archivo)
            print(f"Archivo guardado localmente como {nuevo_nombre}")
        except Exception as e:
            print("Error al guardar localmente:", e)
    else:
        print("Opción no válida. No se realizó ninguna acción.")


if __name__ == "__main__":
    # Datos a pedir
    precio_min = input("Precio mínimo del piso: ")
    precio_max = input("Precio máximo del piso: ")
    num_habitaciones = input("Numero de habitaciones mínimo (0 (estudio), 1, 2, 3, 4 o más): ")
    opcion = input("¿Comprar o Alquilar?: ")

    entre_valores = aplicar_precio(precio_min, precio_max)

    boton_habitaciones = ""

    if num_habitaciones not in ("", 0, None):
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

    try:
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

        # Simular comportamiento humano con movimientos de ratón y desplazamiento
        actions.move_to_element(button_rechazar).pause(tiempo_esperar()).click().perform()

        # No buscar el botón si el usuario no introdució un valor
        if boton_habitaciones != "":
            # Aplicar filtro de habitaciones
            check_habitaciones = (WebDriverWait(browser, 10).
                                  until(EC.presence_of_element_located((By.CSS_SELECTOR, f'[id="{boton_habitaciones}"]'))))

            # Simular comportamiento humano con movimientos de ratón y desplazamiento
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
            # Extraer los links a los pisos filtrados
            pisos.extend(obtener_enlace(html,pagina,url_target))
            print(f"Extraido links de la página {pagina}")
            try: # Esperar a que el botón de 'siguiente' esté disponible y clickarlo
                boton_siguiente = (WebDriverWait(browser, 10)
                .until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.icon-arrow-right-after"))))
                actions.move_to_element(boton_siguiente).pause(tiempo_esperar()).click().perform()
                pagina += 1
            except Exception: # Si no hay 'siguiente' salta excepción y rompemos el bucle
                break

        # Extraemos la información de cada piso
        info = extraer_info(pisos)

    finally:
        # Manejo de cookies y sesiones
        # Limpiamos cookies y almacenamiento local entre sesiones
        browser.delete_all_cookies()
        browser.execute_script("window.localStorage.clear();")

        # Termina el scraping
        browser.quit()

    # Manejamos el archivo csv
    df = pd.DataFrame(info)
    csv = df.to_csv(index=False, encoding="utf-8")
    guardar_archivo(csv)
