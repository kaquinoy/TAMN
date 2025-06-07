from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import csv
import os

def obtener_datos():
    # Configurar Chrome para GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        current_date = datetime.now()
        start_date = "2006-8"
        end_date = f"{current_date.year}-{current_date.month}"
        url = f"https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01129XM/html/{start_date}/{end_date}/"
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'series')))
        
        headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]
        
        meses = {
            'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12'
        }
        
        data = []
        rows = table.find_elements(By.TAG_NAME, 'tr')[1:]
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 2:
                fecha_raw = cells[0].text.strip()
                valor = cells[1].text.strip()
                
                # Extraer y separar año y mes
                mes_codigo = fecha_raw[:3]
                año = f"20{fecha_raw[3:]}" if len(fecha_raw) == 5 else f"20{fecha_raw[3:]}" if int(fecha_raw[3:]) < 50 else f"19{fecha_raw[3:]}"
                mes = meses.get(mes_codigo, '00')
                
                data.append([año, mes, valor])
        
        return headers, data
    
    finally:
        driver.quit()

def main():
    #filename = "bcrp_bonos.csv"
    headers, scraped_data = obtener_datos()
    
    nueva_fecha = datetime.now().strftime('%d/%m/%Y')
    dia, mes, anio = nueva_fecha.split('/')
    fecha_consulta_f = f"{anio}-{mes}-{dia}"
    #df_final.to_excel("SBS_RETASAS_acumulado.xlsx", index=False)
    # Guardar CSV
    os.makedirs('historial', exist_ok=True)
    nombre_archivo = os.path.join('historial', f"indice_bonos_{fecha_consulta_f}.csv")
    scraped_data.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    print("✅ Archivo generado correctamente:", nombre_archivo)


  
    # Verificar últimos datos existentes
    #last_date = None
    #if os.path.exists(filename):
    #    with open(filename, 'r', encoding='utf-8') as f:
    #        reader = csv.reader(f)
     #       rows = list(reader)
     #       if len(rows) > 1:
     #           last_ano = rows[-1][0]
     #           last_mes = rows[-1][1]
     #           last_date = f"{last_ano}-{last_mes}"

    # Filtrar nuevos registros
    #new_data = []
    #for row in scraped_data:
    #    current_date = f"{row[0]}-{row[1]}"
    #    if not last_date or current_date > last_date:
    #        new_data.append(row)

    # Escribir al archivo
    #if new_data:
    #    mode = 'a' if os.path.exists(filename) else 'w'
     #   with open(filename, mode, newline='', encoding='utf-8') as file:
     #       writer = csv.writer(file)
    #        if mode == 'w':
    #            writer.writerow(['Año', 'Mes', headers[1]])
    #        writer.writerows(new_data)
    #    print(f"Datos actualizados: {len(new_data)} nuevos registros")
    #else:
    #    print("No se encontraron datos nuevos")

if __name__ == "__main__":
    main()
