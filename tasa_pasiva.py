from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
from datetime import datetime
import os

#os.chdir("C:/Users/kaqui/OneDrive/Escritorio/03.Tesis/Data/Basededatos")

# Opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Reemplaza "--headless" por "--headless=new"
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

# Inicializa el driver
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Carga la página
driver.get("https://www.sbs.gob.pe/app/pp/EstadisticasSAEEPortal/Paginas/TIPasivaMercado.aspx?tip=B")


# Obtener fecha
nueva_fecha = datetime.now().strftime('%d/%m/%Y')
dia, mes, anio = nueva_fecha.split('/')
fecha_consulta_f = f"{anio}-{mes}-{dia}"

try:
    # Esperar hasta que el contenido esté disponible (30 seg máx)
    wait = WebDriverWait(driver, 30)
    tipmn_element = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphContent_lblVAL_TIPMN_TASA")))
    tipmex_element = wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphContent_lblVAL_TIPMEX_TASA")))

    # Obtener texto
    tipmn = tipmn_element.text.strip()
    tipmex = tipmex_element.text.strip()

    # Crear DataFrame con los datos
    df = pd.DataFrame({
       "fecha_consulta": [fecha_consulta_f, fecha_consulta_f],        
        "Moneda": ["Nacional (TIPMN)", "Extranjera (TIPMEX)"],
        "Tasa (%)": [tipmn, tipmex],
        "Periodo": ["Anual", "Anual"]
    })

    nueva_fecha = datetime.now().strftime('%d/%m/%Y')
    dia, mes, anio = nueva_fecha.split('/')
    fecha_consulta_f = f"{anio}-{mes}-{dia}"

    # Guardar CSV
    os.makedirs('historial', exist_ok=True)
    nombre_archivo = os.path.join('historial', f"tasa_pasiva_{fecha_consulta_f}.csv")
    df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    print("✅ Archivo generado correctamente:", nombre_archivo)


    # Consolidar en tasa_pasiva.csv
    archivo_consolidado = os.path.join('historial', 'tasa_pasiva.csv')
    if os.path.exists(archivo_consolidado):
        df_existente = pd.read_csv(archivo_consolidado, encoding='utf-8-sig')
        df_total = pd.concat([df_existente, df], ignore_index=True)
        df_total.drop_duplicates(subset=['fecha_consulta', 'moneda'], inplace=True)
    else:
        df_total = df

    df_total.to_csv(archivo_consolidado, index=False, encoding='utf-8-sig')
    print("📦 Consolidado actualizado:", archivo_consolidado)

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    driver.quit()