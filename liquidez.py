# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import csv
from typing import List
import os
import pandas as pd
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36'
}

URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN00187MM/html"

def fetch_liquidez_table() -> pd.DataFrame:
    """
    Extrae la tabla de liquidez en soles desde la web del BCRP y la retorna como DataFrame de dos columnas: Fecha, Liquidez.
    Procesa la tabla por pares de columnas (fecha, valor) en cada fila, incluyendo el encabezado correcto.
    """
    resp = requests.get(URL, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    tabla = soup.find('table', class_='series')
    if not tabla:
        raise ValueError("No se encontró la tabla de liquidez en la página.")
    filas = tabla.find_all('tr')
    fechas = []
    valores = []
    # Procesar encabezado
    encabezado = filas[0].find_all('th')
    if len(encabezado) >= 2:
        col_fecha = encabezado[0].get_text(strip=True)
        col_valor = encabezado[1].get_text(strip=True)
    else:
        col_fecha = "Fecha"
        col_valor = "Liquidez"
    # Procesar datos
    for fila in filas[1:]:  # saltar encabezado
        celdas = [celda.get_text(strip=True) for celda in fila.find_all('td')]
        for i in range(0, len(celdas)-1, 2):
            fecha = celdas[i]
            valor = celdas[i+1]
            if fecha and valor:
                fechas.append(fecha)
                valores.append(valor)
    df = pd.DataFrame({col_fecha: fechas, col_valor: valores})
    df = df.drop_duplicates()
    return df

def save_to_csv(data: pd.DataFrame, folder: str, tipo: str = ""):
    """
    Guarda el DataFrame en un archivo CSV en la carpeta indicada, con nombre personalizado.
    Solo guarda un nuevo archivo si la data es diferente a la última guardada en la carpeta.
    tipo: prefijo para el nombre del archivo (ej: 'CPI', 'Liquidez')
    """
    import glob
    fecha = os.path.basename(folder)
    fecha_2 = datetime.now().strftime("%Y-%m-%d")

    if tipo:
        filename = f"datos{tipo}_{fecha}_{fecha_2}.csv"
    else:
        filename = f"datos_{fecha}_{fecha_2}.csv"
    path = os.path.join(folder, filename)
    temp_path = path + '.tmp'
    data.to_csv(temp_path, index=False)
    csv_files = sorted(glob.glob(os.path.join(folder, f'datos{tipo}_*_{fecha_2}.csv')))
    last_csv = csv_files[-1] if csv_files else None
    is_different = True
    if last_csv:
        with open(last_csv, 'r', encoding='utf-8') as f1, open(temp_path, 'r', encoding='utf-8') as f2:
            is_different = f1.read() != f2.read()
    if is_different:
        os.replace(temp_path, path)
    else:
        os.remove(temp_path)
    
    
fecha = datetime.now().strftime("%Y-%m-%d")
os.makedirs("historial", exist_ok=True)
datos = fetch_liquidez_table()
save_to_csv(datos, "historial", tipo='Liquidez')



# Guardar/actualizar archivo acumulado PBI.csv con columna fecha_carga
acumulado_path = os.path.join('historial', 'liquidez.csv')
#acumulado_path = "PBI.csv"
fecha_carga = datetime.now().strftime("%Y-%m-%d")
datos['fecha_carga'] = fecha_carga

# Leer acumulado si existe
if os.path.exists(acumulado_path):
    acumulado = pd.read_csv(acumulado_path)
    # Concatenar y eliminar duplicados
    df_final = pd.concat([acumulado, datos], ignore_index=True)
    df_final = df_final.drop_duplicates()
else:
    df_final = datos

# Guardar archivo actualizado
df_final.to_csv(acumulado_path, index=False)
print(f"✅ Datos acumulados guardados en {acumulado_path}")
