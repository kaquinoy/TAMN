
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import json
from datetime import datetime
import time

#Entrando a la pagina de la sbs
driver = webdriver.Chrome()
driver.get('https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioPromedio.aspx')
time.sleep(3)

tbody = driver.find_element(By.XPATH, '//*[@id="ctl00_cphContent_rgTipoCambio_ctl00"]/tbody')

# Encontrar todas las filas (tr)
filas = tbody.find_elements(By.TAG_NAME, 'tr')

# Extraer los datos
datos = []
for fila in filas:
    columnas = fila.find_elements(By.TAG_NAME, 'td')
    if len(columnas) == 3:  # Esperamos 3 columnas: Moneda, Compra, Venta
        moneda = columnas[0].text.strip()
        compra = columnas[1].text.strip()
        venta = columnas[2].text.strip()
        if (compra=="0" and venta !="0"):
            compra=venta
        elif (venta=="0" and compra !="0"):
            venta=compra
        datos.append({
            "moneda": moneda,
            "compra": compra,
            "venta": venta
        })
# Mostrar resultado
for d in datos:
    print(d)

# Cerrar navegador
driver.quit()

fecha_hoy = datetime.now().strftime('%d-%m-%Y')

# Fecha de la consulta
nueva_fecha = datetime.now().strftime('%d/%m/%Y')
dia, mes, anio = nueva_fecha.split('/')
fecha_consulta_f = f"{anio}-{mes}-{dia}"

# Crear la carpeta destino
#ruta_carpeta = f"{fecha_hoy}/"
#os.makedirs(ruta_carpeta, exist_ok=True)
os.makedirs('historial', exist_ok=True)
# Definir el nombre del archivo
#ruta_archivo = os.path.join(ruta_carpeta, 'sbs_tipo_cambio.json')
ruta_archivo = os.path.join('historial', f"tipo_cambio_{fecha_consulta_f}.csv")
# Guardar los datos en formato JSON
with open(ruta_archivo, 'w', encoding='utf-8') as f:
    json.dump(datos, f, indent=4, ensure_ascii=False)

print(f"Datos guardados exitosamente en {ruta_archivo}")

