from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import os

#os.chdir("C:/Users/kaqui/OneDrive/Escritorio/03.Tesis/Data/Basededatos")

# Configurar opciones de Chrome
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Reemplaza "--headless" por "--headless=new"
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.get("https://es.tradingeconomics.com/united-states/adp-employment-change")

# Esperar a que la tabla esté cargada (buscar por clase del <table>)
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-hover"))
)

# Buscar todas las filas visibles
rows = driver.find_elements(By.CSS_SELECTOR, "table.table-hover tbody tr")
data = []

for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    if len(cols) == 5:
        indicador = cols[0].text.strip()
        ultimo = cols[1].text.strip()
        anterior = cols[2].text.strip()
        unidad = cols[3].text.strip()
        referencia = cols[4].text.strip()
        data.append([indicador, ultimo, anterior, unidad, referencia])

# Crear el DataFrame
fecha_actual = datetime.now().strftime('%Y-%m-%d')
df = pd.DataFrame(data, columns=["Indicador", "Último", "Anterior", "Unidad", "Referencia"])
df.insert(0, "fecha_consulta", fecha_actual)
# print(df)


nueva_fecha = datetime.now().strftime('%d/%m/%Y')
dia, mes, anio = nueva_fecha.split('/')
fecha_consulta_f = f"{anio}-{mes}-{dia}"

# Guardar CSV
os.makedirs('historial', exist_ok=True)
nombre_archivo = os.path.join('historial', f"empleo_usa_{fecha_consulta_f}.csv")
df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
print("✅ Archivo generado correctamente:", nombre_archivo)

# Consolidado
archivo_consolidado = os.path.join('historial', "empleo_usa.csv")
if os.path.exists(archivo_consolidado):
    df_existente = pd.read_csv(archivo_consolidado, encoding='utf-8-sig')
    df_total = pd.concat([df_existente, df], ignore_index=True)
    df_total.drop_duplicates(subset=["fecha_consulta"], inplace=True)
else:
    df_total = df

df_total.to_csv(archivo_consolidado, index=False, encoding='utf-8-sig')
print("📦 Consolidado actualizado:", archivo_consolidado)


# Cerrar el navegador
driver.quit()
