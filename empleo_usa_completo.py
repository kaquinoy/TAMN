import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime  # ✅ Importar datetime
import os
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
        except Exception as e:
            print(f"❌ Error al escribir en el archivo CSV: {e}")
    else:
        print("❌ No se encontró el contenedor de la tabla de indicadores.")
else:
    print(f"❌ Error {response.status_code} al acceder a la página.")

print(f"📊 Datos extraídos: {fila_datos}")  