import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


nueva_fecha = datetime.now().strftime('%d/%m/%Y')
dia, mes, anio = nueva_fecha.split('/')
fecha_consulta_f = f"{anio}-{mes}-{dia}"

# Crear carpeta con la fecha actual
hoy = datetime.today().strftime('%Y-%m-%d')
#base_path = os.path.join("data", hoy)
#os.makedirs(base_path, exist_ok=True)

# -------------------------------------
# 1. Scraping FED Funds Rate desde FRED
# -------------------------------------

fed_api_csv = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS"

try:
    r = requests.get(fed_api_csv)
    r.raise_for_status()
    #fed_path = os.path.join("data", "fed", hoy)
    fed_path = os.path.join('historial', f"fed_{fecha_consulta_f}.csv")  
    os.makedirs(fed_path, exist_ok=True)
    with open(os.path.join(fed_path, f"fed_{fecha_consulta_f}.csv"), "wb") as f:
        f.write(r.content)
    #print(f"[✓] Datos de la FED guardados en {fed_path}\\fedfunds.csv")
except Exception as e:
    print(f"[✗] Error al acceder a FRED: {e}")



# -------------------------------------
# 2. Scraping inflación Perú desde TradingEconomics
# -------------------------------------

te_url = "https://tradingeconomics.com/peru/inflation-cpi"
categoria = "inflacion_peru"

try:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    r = requests.get(te_url, headers=headers)
    r.raise_for_status()

    tables = pd.read_html(r.text)  # pandas para leer tablas del html

    #te_path = os.path.join("data", categoria, hoy)
    #os.makedirs(te_path, exist_ok=True)

    for i, tabla in enumerate(tables):
        #archivo_csv = os.path.join(te_path, f"tabla_{i+1}.csv")
        archivo_csv = os.path.join('historial', f"inflacion_{fecha_consulta_f}_{i+1}.csv") 
        tabla.to_csv(archivo_csv, index=False)
        #print(f"[✓] Tabla {i+1} guardada en: {archivo_csv}")

except Exception as e:
    print(f"[✗] Error al acceder a TradingEconomics: {e}")
    
