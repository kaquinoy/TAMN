from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os

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
'''
def guardar_csv(data, archivo):
    existe = os.path.exists(archivo)

     # Leer fechas existentes
    fechas_existentes = set()
    if existe:
        with open(archivo, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # saltar encabezado
            for fila in reader:
                if fila:
                    fechas_existentes.add(fila[0])

    # Filtrar datos nuevos
    nuevos = [fila for fila in data if fila[0] not in fechas_existentes]

    # Guardar solo datos nuevos
    if nuevos:
        with open(archivo, 'a' if existe else 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not existe:
                writer.writerow(["Fecha", "Tasa"])
            writer.writerows(nuevos)
        print(f"Datos guardados: {len(nuevos)} nuevas filas")
    else:
        print("No se encontraron datos nuevos")
 '''   
def main():
    #filename = "PARCIAL/fed_tasas.csv"
    datos = obtener_tasas_fed()
    #guardar_csv(datos, filename)

    nueva_fecha = datetime.now().strftime('%d/%m/%Y')
    dia, mes, anio = nueva_fecha.split('/')
    fecha_consulta_f = f"{anio}-{mes}-{dia}"
    #df_final.to_excel("SBS_RETASAS_acumulado.xlsx", index=False)
    # Guardar CSV
    os.makedirs('historial', exist_ok=True)
    nombre_archivo = os.path.join('historial', f"tasas_usa_{fecha_consulta_f}.csv")
    datos.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    print("✅ Archivo generado correctamente:", nombre_archivo)


if __name__ == "__main__":
    main()
