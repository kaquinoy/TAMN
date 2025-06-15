import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime  # ✅ Importar datetime
import os
import pandas as pd

# Lista de indicadores esperados
indicadores_esperados = [
    "Ganancias horarias promedio (Mensual)",
    "Ganancias promedio por hora (Interanual)",
    "Promedio de horas semanales",
    "Personas ocupadas",
    "Índice De Costo De Empleo",
    "Employment Cost - Benefits",
    "Employment Cost - Wages",
    "Tasa De Empleo",
    "Trabajadores a tiempo completo",
    "Nóminas gubernamentales",
    "Despidos laborales y despidos",
    "Jolts Vacantes de Empleo",
    "Renuncias laborales informe JOLTs",
    "Tasa de abandonos del trabajo",
    "Ofertas de empleo",
    "Tasa de participación",
    "Salarios",
    "Tasa de desempleo de largo plazo",
    "Nóminas manufactureras",
    "Nóminas no agrícolas",
    "Nóminas privadas no agrícolas",
    "Productividad No Agrícola",
    "Empleo de Tiempo Parcial",
    "Productividad",
    "Tasa de desempleo U-6",
    "Personas desempleadas",
    "Tasa de desempleo",
    "Costes laborales unitarios",
    "Salarios",
    "Salarios en la industria",
    "Tasa de desempleo juvenil"
]

# URL del sitio
url = 'https://es.tradingeconomics.com/united-states/u6-unemployment-rate'

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept-Language': 'es-ES,es;q=0.9'
}
hoy = datetime.now().strftime("%Y-%m-%d")
# Realizar la solicitud
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Buscar el div que contiene la tabla de indicadores relacionados
    tabla_div = soup.select_one('#ctl00_ContentPlaceHolder1_ctl00_ctl02_PanelPeers table')

    if tabla_div:
        filas = tabla_div.find_all('tr')

        fila_datos = []

        for i, fila in enumerate(filas):
            columnas = fila.find_all('td')
            if len(columnas) >= 2:
                valor = columnas[1].get_text(strip=True).replace(",", "")
                fila_datos.append(valor)

        # Rellenar con None si faltan datos
        while len(fila_datos) < len(indicadores_esperados):
            fila_datos.append(None)

        # 👉 Agregar la fecha y hora actual
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fila_datos.append(fecha_actual)
        archivo_csv = os.path.join("historial", f"empleo_usa_completo_{hoy}.csv")
        # Escribir en el CSV (sin necesidad de usar pandas)
        try:
            # Abrir el archivo en modo append, para agregar sin sobrescribir
            with open(archivo_csv, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Si el archivo está vacío, escribir los encabezados primero
                if file.tell() == 0:
                    writer.writerow(indicadores_esperados)

                # Escribir la nueva fila de datos
                writer.writerow(fila_datos)

            print("✅ CSV actualizado con fecha y hora.")

            # Crear DataFrame para acumulado
            columnas_completas = indicadores_esperados + ['fecha_hora']
            datos = pd.DataFrame([fila_datos], columns=columnas_completas)
            datos['fecha_carga'] = datetime.now().strftime("%Y-%m-%d")
            
            # Guardar/actualizar acumulado
            acumulado_path = os.path.join('historial', 'empleo_usa_completo.csv')
            try:
                if os.path.exists(acumulado_path):
                    acumulado = pd.read_csv(acumulado_path)
            
                    # Validar que no haya columnas duplicadas
                    if acumulado.columns.duplicated().any():
                        acumulado = acumulado.loc[:, ~acumulado.columns.duplicated()]
            
                    # Reordenar las columnas para que coincidan
                    acumulado = acumulado.reindex(columns=datos.columns, fill_value=None)
            
                    df_final = pd.concat([acumulado, datos], ignore_index=True)
                    df_final = df_final.drop_duplicates()
                else:
                    df_final = datos
            
                df_final.to_csv(acumulado_path, index=False)
                print(f"✅ Datos acumulados guardados en {acumulado_path}")
            
            except Exception as e:
                print(f"❌ Error al escribir en el archivo CSV: {e}")


        except Exception as e:
            print(f"❌ Error al escribir en el archivo CSV: {e}")
    else:
        print("❌ No se encontró el contenedor de la tabla de indicadores.")
else:
    print(f"❌ Error {response.status_code} al acceder a la página.")

print(f"📊 Datos extraídos: {fila_datos}")  