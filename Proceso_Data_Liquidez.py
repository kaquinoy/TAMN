from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os, re, time
from datetime import date, datetime
from pathlib import Path

# Parámetros
URL_BASE = "https://www.bcrp.gob.pe/operaciones-monetarias-y-cambiarias.html"
ARCHIVO_SALIDA = Path(__file__).with_name("operaciones_monetarias_bcrp.csv")
COLUMNAS = ["Fecha", "Hora", "Comentario", "Monto_millones", "Moneda"]

PATRON_MONTO = re.compile(
    r"(?P<moneda>US\$|S\s*/\s*\.?|S\.)\s*"
    r"(?P<monto>\d[\d\s.]*(?:,\d+)?)\s+millones?\b",
    re.IGNORECASE,
)

# Configuración de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get(URL_BASE)

registros = []

def extraer_monto(comentario):
    coincidencia = PATRON_MONTO.search(comentario)
    if coincidencia is None:
        return None, ""
    texto_monto = coincidencia.group("monto")
    monto = float(texto_monto.replace(" ", "").replace(".", "").replace(",", "."))
    moneda = "US$" if coincidencia.group("moneda").upper().startswith("US$") else "S/"
    return monto, moneda

try:
    while True:
        wait = WebDriverWait(driver, 60)
        bloque = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".newslist")))

        bloques_fecha = bloque.find_elements(By.CSS_SELECTOR, ".newslist > div")
        for bf in bloques_fecha:
            fecha_linea = bf.text.split("\n")[0].strip()
            items = bf.find_elements(By.CSS_SELECTOR, "ul.list-group > li")
            for item in items:
                try:
                    hora = item.find_element(By.TAG_NAME, "b").text.strip(": ")
                except:
                    hora = ""
                comentario = item.text.replace(hora, "").strip()
                monto, moneda = extraer_monto(comentario)
                registros.append([fecha_linea, hora, comentario, monto, moneda])

        # Intentar ir a la siguiente página
        try:
            boton_siguiente = driver.find_element(By.LINK_TEXT, "Siguiente")
            boton_siguiente.click()
            time.sleep(2)
        except:
            print("No hay más páginas.")
            break

    # Guardar CSV
    df = pd.DataFrame(registros, columns=COLUMNAS)
    df.to_csv(ARCHIVO_SALIDA, index=False, encoding="utf-8-sig")
    print(f"✅ Datos guardados en: {ARCHIVO_SALIDA}")

except Exception as e:
    print(f"❌ Error en {driver.current_url}: {e}")
finally:
    driver.quit()

