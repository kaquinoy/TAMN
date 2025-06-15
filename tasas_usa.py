from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os
import time
from datetime import datetime, timedelta
import pandas as pd

def obtener_tasas_fed():
    url = "https://www.global-rates.com/es/tipos-de-interes/bancos-centrales/1002/interes-americano-fed-federal-funds-rate/"

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 60)
        tabla = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))

        filas = tabla.find_elements(By.TAG_NAME, "tr")[1:]  # saltar encabezado
        data = []
        for fila in filas:
            celdas = fila.find_elements(By.TAG_NAME, "td")
            if len(celdas) >= 2:
                fecha = celdas[0].text.strip()
                tasa = celdas[1].text.strip().replace('%', '').replace(',', '.')
                data.append([fecha, tasa])
        return data

    
    finally:
        driver.quit()
 
def main():

    # Aplica funcion
    datos = obtener_tasas_fed()

    # Crea el compilado de data
    df = pd.DataFrame(datos, columns=['fecha', 'tasa'])

    # Fecha de archivo
    nueva_fecha = datetime.now().strftime('%d/%m/%Y')
    dia, mes, anio = nueva_fecha.split('/')
    fecha_consulta_f = f"{anio}-{mes}-{dia}"


    # Guardar CSV
    os.makedirs('historial', exist_ok=True)
    nombre_archivo = os.path.join('historial', f"tasas_usa_{fecha_consulta_f}.csv")
    df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    print("✅ Archivo generado correctamente:", nombre_archivo)


    # Guardar/actualizar archivo acumulado PBI.csv con columna fecha_carga
    acumulado_path = os.path.join('historial', 'tasas_usa.csv')
    #acumulado_path = "PBI.csv"
    fecha_carga = datetime.now().strftime("%Y-%m-%d")
    df['fecha_carga'] = fecha_carga
    
    # Leer acumulado si existe
    if os.path.exists(acumulado_path):
        acumulado = pd.read_csv(acumulado_path)
        df_final = pd.concat([acumulado, df], ignore_index=True)
        # Eliminar duplicados basados en fecha y tasa (ignora fecha_carga)
        # df_final = df_final.drop_duplicates(subset=['fecha', 'tasa'])
    else:
        df_final = df

    # Guardar archivo actualizado
    df_final.to_csv(acumulado_path, index=False)
    print(f"✅ Datos acumulados guardados en {acumulado_path}")



if __name__ == "__main__":
    main()
