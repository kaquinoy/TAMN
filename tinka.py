import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

url = 'https://www.resultadosdetinka.com/tinka-resultados.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Error {response.status_code} al acceder a la página")

soup = BeautifulSoup(response.text, 'html.parser')

# 1. Extraer la fecha del sorteo
time_tag = soup.find('time')
fecha = time_tag.text.strip() if time_tag else 'Fecha no encontrada'

# 2. Extraer los 6 números principales
numeros = [tag.text.strip() for tag in soup.find_all('span', class_='label label-tinka')[:6]]

# 3. Extraer Boliyapa
# Busca el texto "Boliyapa" y luego toma el siguiente span con la clase correspondiente
boliyapa = 'No encontrada'
boli_section = soup.find(string=lambda t: t and 'Boliyapa' in t)
if boli_section:
    boli_span = soup.find('span', class_='label label-primary')
    if boli_span:
        boliyapa = boli_span.text.strip()

# 4. Extraer "Sí o Sí"
# Busca el texto "Sí o Sí" y luego toma el siguiente span con la clase correspondiente
siosi = ['No encontrada']
siosi_section = soup.find(string=lambda t: t and 'Sí o Sí' in t)
if siosi_section:
    all_primary_labels = soup.find_all('span', class_='label label-primary')
    if len(all_primary_labels) >= 2:
        siosi = all_primary_labels[1].text.strip().split()
        
        
# Mostrar resultados
print(f"🗓 Fecha del sorteo: {fecha}")
print(f"🎱 Números ganadores: {' - '.join(numeros)}")
print(f"🔵 Boliyapa: {boliyapa}")
print(f"🎯 Sí o Sí: {' - '.join(siosi)}")

# Guardar en CSV
datos = {
    'Fecha': [fecha],
    'Números principales': [' - '.join(numeros)],
    'BolaExtra': [boliyapa],
    'Sí o Sí': [' - '.join(siosi)]
}
df = pd.DataFrame(datos)
fn = 'resultados_tinka.csv'
df.to_csv(fn, mode='a', index=False, header=not os.path.exists(fn))
print(f"✅ Guardado en {fn}")
