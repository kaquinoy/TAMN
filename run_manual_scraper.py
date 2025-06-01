import os
import sys
from datetime import datetime, timedelta

if len(sys.argv) != 3:
    print("Uso: python run_manual_scraper.py <fecha_inicio> <fecha_fin>")
    sys.exit(1)

fecha_inicio = sys.argv[1]
fecha_fin = sys.argv[2]

try:
    start_date = datetime.strptime(fecha_inicio, "%d/%m/%Y")
    end_date = datetime.strptime(fecha_fin, "%d/%m/%Y")
except ValueError:
    print("Error en el formato de fecha. Usa dd/mm/yyyy")
    sys.exit(1)

current_date = start_date
while current_date <= end_date:
    fecha_str = current_date.strftime("%d/%m/%Y")
    print(f"Procesando: {fecha_str}")

    # Setea la variable de entorno que usará scrapersbs.py
    os.environ['FECHA_CONSULTA'] = fecha_str

    # Ejecuta el script del scraper
    exit_code = os.system("python scrapersbs.py")
    if exit_code != 0:
        print(f"Error ejecutando el scraper para {fecha_str}")
    else:
        print(f"Finalizado: {fecha_str}")

    current_date += timedelta(days=1)
