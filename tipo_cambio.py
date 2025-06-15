from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
import os
from io import StringIO  # ✅ Agregado

# Configura las opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
)

# Ruta a chromedriver.exe (modifica según donde lo tengas)
#service = Service(r"C:\tools\chromedriver.exe")
service = Service(ChromeDriverManager().install())
# Inicializa el driver
driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx"
driver.get(url)

try:
    wait = WebDriverWait(driver, 30)
    tabla_element = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphContent_rgTipoCambio_ctl00")))
    tabla_html = tabla_element.get_attribute('outerHTML')
    tablas = pd.read_html(StringIO(tabla_html))  # ✅ Corregido
    #tablas = pd.read_html(tabla_html)
    df = tablas[0]

    # Renombrar columnas según lo que quieres
    df.columns = ["Moneda", "Compra", "Venta"]

    # Agregar fecha
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    df.insert(0, "fecha_consulta", fecha_actual)

    # Guardar CSV
    hoy = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("historial", exist_ok=True)
    archivo_csv = os.path.join("historial", f"tipo_cambio_{hoy}.csv")
    df.to_csv(archivo_csv, index=False, encoding='utf-8-sig')

    print(f"✅ Tipo de cambio guardado en: {archivo_csv}")


    # Guardar archivo consolidado
    consolidado_path = os.path.join("historial", "tipo_cambio.csv")
    if os.path.exists(consolidado_path):
        df_antiguo = pd.read_csv(consolidado_path, encoding='utf-8-sig')
        df_total = pd.concat([df_antiguo, df], ignore_index=True)
        #df_total.drop_duplicates(subset=["fecha_consulta"], inplace=True)
    else:
        df_total = df

    df_total.to_csv(consolidado_path, index=False, encoding='utf-8-sig')
    print(f"📦 Consolidado actualizado en: {consolidado_path}")

except Exception as e:
    print(f"❌ Error al obtener tipo de cambio: {e}")
finally:
    driver.quit()
