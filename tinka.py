from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import csv
import os

def obtener_resultados_tinka():
    options = Options()
    # COMENTA HEADLESS para ver el navegador en ejecución (para depurar)
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://www.tinkaresultados.com/"
        driver.get(url)

        wait = WebDriverWait(driver, 30)

        # Esperar que aparezcan al menos 6 bolas como señal de carga completa
        bolas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.resultado .numero')))
        numeros_tinka = [b.text.strip() for b in bolas[:6]]

        # Captura screenshot para depuración
        driver.save_screenshot("debug_tinka.png")

        # Extraer Sí o Sí
        si_o_si = driver.find_element(By.CSS_SELECTOR, ".siosi .numero").text.strip()

        # Extraer Boliyapa
        boliyapa = driver.find_element(By.CSS_SELECTOR, ".boliyapa .numero").text.strip()

        return {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "numeros": numeros_tinka,
            "si_o_si": si_o_si,
            "boliyapa": boliyapa
        }

    finally:
        driver.quit()

def guardar_csv(data):
    nueva_fecha = datetime.now().strftime('%d/%m/%Y')
    dia, mes, anio = nueva_fecha.split('/')
    fecha_consulta_f = f"{anio}-{mes}-{dia}"    

    os.makedirs("historial", exist_ok=True)
    ruta_archivo = os.path.join('historial', f"tinka_{fecha_consulta_f}.csv")
    with open(ruta_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Fecha", "Números", "Sí o Sí", "Boliyapa"])
        writer.writerow([
            data["fecha"],
            " ".join(data["numeros"]),
            data["si_o_si"],
            data["boliyapa"]
        ])

    print(f"✅ Resultados guardados en {ruta_archivo}")

def main():
    data = obtener_resultados_tinka()
    guardar_csv(data)

if __name__ == "__main__":
    main()