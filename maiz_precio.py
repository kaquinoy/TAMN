import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
import os
import pandas as pd
from datetime import datetime

def iniciar_chrome():
    ruta = ChromeDriverManager().install()

    options = Options()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--no-proxy-server")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 🚫 Desactivar temporalmente para pruebas
    options.add_argument("--headless")

    exp_opt = ["enable-automation", "ignore-certificate-errors", "enable-logging"]
    options.add_experimental_option("excludeSwitches", exp_opt)

    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False
    }
    options.add_experimental_option("prefs", prefs)

    s = Service(ruta)
    driver = webdriver.Chrome(service=s, options=options)
    return driver

if __name__ == "__main__":
    driver = iniciar_chrome()
    url = "https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/resultados/PN01685PM/html"
    driver.get(url)

    wait = WebDriverWait(driver, 30)

    try:
        # Espera que el formulario esté listo
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "formulario-contenedor")))

        boton_mes = wait.until(EC.presence_of_element_located((By.ID, 'mes2')))
        pulsar_mes_dic = boton_mes.find_elements(By.TAG_NAME, "option")
        pulsar_mes_dic[-1].click()

        boton_anio = wait.until(EC.presence_of_element_located((By.ID, 'anio2')))
        pulsar_ultimo_anio = boton_anio.find_elements(By.TAG_NAME, "option")
        pulsar_ultimo_anio[0].click()

        boton_actualizar = wait.until(EC.presence_of_element_located((By.ID, "btnBuscar")))
        boton_actualizar.click()

        time.sleep(1)

        div_tabla = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "barra-resultados")))
        tr_div_tabla = div_tabla.find_elements(By.TAG_NAME, "tr")
        
        tabla_completa = []
        header = ["Fecha", "Precios de productos sujetos al sistema de franjas de precios (US$ por toneladas) - Maíz"]

        for i, fila in enumerate(tr_div_tabla):
            if i == 0:
                continue
            texto = fila.text.split(" ")
            tabla_completa.append(texto)

        conjunto = set(i[0][-2:] for i in tabla_completa)
        lista_ordenada_conjunto = sorted(conjunto)
        cantidad_columnas = len(lista_ordenada_conjunto)

        tabla_por_fechas = [[] for _ in range(cantidad_columnas)]

        for i, sufijo in enumerate(lista_ordenada_conjunto):
            for fila in tabla_completa:
                if fila[0][-2:] == sufijo:
                    tabla_por_fechas[i].append(fila)

        nueva_fecha = datetime.now().strftime('%d/%m/%Y')
        dia, mes, anio = nueva_fecha.split('/')
        fecha_consulta_f = f"{anio}-{mes}-{dia}"

        ruta_base = "datos_maiz_por_anio"
        os.makedirs("historial", exist_ok=True)

        for subtabla in tabla_por_fechas:
            if not subtabla:
                continue
            fecha = subtabla[0][0]
            anio_subtabla = "19" + fecha[-2:] if fecha[-2:] > "91" else "20" + fecha[-2:]

            ruta_carpeta = os.path.join(ruta_base, anio_subtabla)
            os.makedirs(ruta_carpeta, exist_ok=True)

            df = pd.DataFrame(subtabla, columns=header)
            ruta_csv = os.path.join('historial', f"maiz_precio_{fecha_consulta_f}_{anio_subtabla}.csv")
            df.to_csv(ruta_csv, index=False, encoding='utf-8')

            print(f"✅ Guardado: {ruta_csv}")

    except Exception as e:
        print("❌ Error durante la ejecución:", e)
        driver.save_screenshot("debug.png")
        print("📸 Captura de pantalla guardada como debug.png")

    finally:
        driver.quit()
  