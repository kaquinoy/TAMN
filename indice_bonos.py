from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import csv

def obtener_datos():
    # Configurar opciones para Selenium
    options = Options()
    options.add_argument('--headless')  # Comentarlo para ver el navegador
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Inicializar WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01129XM/html"
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        tabla = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "series")))

        # Extraer encabezados
        headers = [th.text.strip() for th in tabla.find_elements(By.TAG_NAME, "th")]

        # Extraer filas
        filas = tabla.find_elements(By.TAG_NAME, "tr")[1:]  # Omitir cabecera
        datos = []

        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, "td")
            fila_datos = [col.text.strip() for col in columnas]
            if fila_datos:
                datos.append(fila_datos)

        return headers, datos

    finally:
        driver.quit()

def guardar_csv(headers, datos):
    
    nueva_fecha = datetime.now().strftime('%d/%m/%Y')
    dia, mes, anio = nueva_fecha.split('/')
    fecha_consulta_f = f"{anio}-{mes}-{dia}"    

    #fecha = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("historial", exist_ok=True)
    #ruta_archivo = f"historial/indice_bonos_{fecha}.csv"
    ruta_archivo = os.path.join('historial', f"indice_bonos_{fecha_consulta_f}.csv")
    with open(ruta_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(datos)



    
    print(f"✅ CSV guardado como {ruta_archivo}")

def main():
    headers, datos = obtener_datos()
    guardar_csv(headers, datos)

if __name__ == "__main__":
    main()
