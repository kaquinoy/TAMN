import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configurar navegador en modo headless
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Inicializar driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Acceder a la página de tipo de cambio SBS
driver.get('https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx')
time.sleep(3)

# Extraer tabla de tipo de cambio
tbody = driver.find_element(By.XPATH, '//*[@id="ctl00_cphContent_rgTipoCambio_ctl00"]/tbody')
filas = tbody.find_elements(By.TAG_NAME, 'tr')

datos = []
for fila in filas:
    columnas = fila.find_elements(By.TAG_NAME, 'td')
    if len(columnas) == 3:
        moneda = columnas[0].text.strip()
        compra = columnas[1].text.strip()
        venta = columnas[2].text.strip()
        if compra == "0" and venta != "0":
            compra = venta
        elif venta == "0" and compra != "0":
            venta = compra
        datos.append({
            "moneda": moneda,
            "compra": compra,
            "venta": venta
        })

# Cerrar navegador
driver.quit()

# Fecha de la consulta
nueva_fecha = datetime.now().strftime('%d/%m/%Y')
dia, mes, anio = nueva_fecha.split('/')
fecha_consulta_f = f"{anio}-{mes}-{dia}"

# Guardar en CSV
df = pd.DataFrame(datos)
os.makedirs('historial', exist_ok=True)
nombre_archivo = os.path.join('historial', f"tipo_cambio_{fecha_consulta_f}.csv")
df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
print("✅ Archivo generado correctamente:", nombre_archivo)


