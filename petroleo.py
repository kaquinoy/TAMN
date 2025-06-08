
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# URL a consultar
url = 'https://es.investing.com/commodities/crude-oil'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    def get_text(selector, attr, fallback='N/A'):
        element = soup.find('dd', {attr: selector})
        if element:
            value = element.text.strip().replace(',', '.').replace('%', '').replace('\xa0', ' ')
            return value.strip()
        return fallback

    def get_range(selector):
        element = soup.find('dd', {'data-test': selector})
        if element:
            valores = element.find_all('span', class_='key-info_dd-numeric__ZQFIs')
            if len(valores) >= 2:
                return (
                    valores[0].text.strip().replace(',', '.'),
                    valores[1].text.strip().replace(',', '.')
                )
        return ('N/A', 'N/A')

    # Datos adicionales al inicio
    precio_actual = soup.find('div', {'data-test': 'instrument-price-last'})
    variacion_abs = soup.find('span', {'data-test': 'instrument-price-change'})
    variacion_pct = soup.find('span', {'data-test': 'instrument-price-change-percent'})
    trading_time = soup.find('time', {'data-test': 'trading-time-label'})

    precio_actual = precio_actual.text.strip().replace(',', '.') if precio_actual else 'N/A'
    variacion_abs = variacion_abs.text.strip().replace(',', '.') if variacion_abs else 'N/A'
    variacion_pct = variacion_pct.text.strip().replace('%', '').replace(',', '.') if variacion_pct else 'N/A'
    trading_time = trading_time.text.strip() if trading_time else 'N/A'

    # Fecha y hora actuales
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Datos actuales
    cierre = get_text('prevClose', 'data-test')
    apertura = get_text('open', 'data-test')
    min_dia, max_dia = get_range('dailyRange')
    min_52s, max_52s = get_range('weekRange')
    volumen = get_text('volume', 'data-test')
    var_anual = get_text('oneYearReturn', 'data-test')
    mes_entrega = get_text('month_date', 'data-test')
    tamano_contrato = get_text('contract_size', 'data-test').split()[0]

    # Nuevos campos
    fecha_vencimiento = get_text('settlement_date', 'data-test')
    clase_liquidacion = get_text('settlement_type', 'data-test')
    ultimo_rollover = get_text('rollover_day', 'data-test')
    tamano_tick = get_text('tick_size', 'data-test')
    simbolo_base = get_text('base_symbol', 'data-test')
    valor_punto = get_text('point_value', 'data-test')
    meses = get_text('instrument_month', 'data-test')

    # Diccionario completo (campos nuevos al principio)
    datos = {
        'Fecha': [fecha_actual],
        'Precio_Actual': [precio_actual],
        'Variacion_Absoluta': [variacion_abs],
        'Variacion_Porcentual': [variacion_pct],
        'Hora_Ultima_Actualizacion': [trading_time],
        'Ultimo_Cierre': [cierre],
        'Apertura': [apertura],
        'Min_Dia': [min_dia],
        'Max_Dia': [max_dia],
        'Min_52_Semanas': [min_52s],
        'Max_52_Semanas': [max_52s],
        'Volumen': [volumen],
        'Var_Anual_Porc': [var_anual],
        'Mes_Entrega': [mes_entrega],
        'Tamano_Contrato_Barriles': [tamano_contrato],
        'Fecha_Vencimiento': [fecha_vencimiento],
        'Clase_Liquidacion': [clase_liquidacion],
        'Ultimo_Rollover': [ultimo_rollover],
        'Tamano_Tick': [tamano_tick],
        'Simbolo_Base': [simbolo_base],
        'Valor_Punto': [valor_punto],
        'Meses': [meses]
    }

    df = pd.DataFrame(datos)

    archivo_csv = 'petroleo.csv'
    df.to_csv(archivo_csv, mode='a', header=not os.path.exists(archivo_csv), index=False)

    print("✅ Datos guardados correctamente en petroleo.csv")
else:
    print(f"❌ Error {response.status_code} al acceder a la página")
    