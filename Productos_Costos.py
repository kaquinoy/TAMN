import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

# Configuración headless para GitHub Actions
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")
chrome_options.add_argument("--remote-debugging-port=9222")

# Inicializar driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 20)

def get_options_text(id_select):
    select = Select(wait.until(EC.presence_of_element_located((By.ID, id_select))))
    opciones = [o.text.strip() for o in select.options if o.get_attribute("value").strip() != ""]
    print(f"Opciones de {id_select}: {opciones}")
    return opciones

def select_option(id_select, texto):
    select = Select(wait.until(EC.element_to_be_clickable((By.ID, id_select))))
    opciones = [o.text.strip() for o in select.options if o.get_attribute("value").strip() != ""]
    coincidencias = [opcion for opcion in opciones if texto.lower() in opcion.lower()]
    
    if not coincidencias:
        print(f"Opción '{texto}' no encontrada en {id_select}. Opciones disponibles: {opciones}")
        raise Exception(f"Opción '{texto}' no está en el select {id_select}")
    
    print(f"Seleccionando {coincidencias[0]} en {id_select}")
    select.select_by_visible_text(coincidencias[0])
    time.sleep(2)

def extraer_tabla_manual():
    print("Extrayendo tabla...")
    table = wait.until(EC.presence_of_element_located((By.ID, "myTable")))
    thead = table.find_element(By.TAG_NAME, "thead")
    encabezados = [th.text.strip() for th in thead.find_elements(By.TAG_NAME, "th")]
    tbody = table.find_element(By.TAG_NAME, "tbody")
    filas = tbody.find_elements(By.TAG_NAME, "tr")
    
    datos = []
    for fila in filas:
        celdas = fila.find_elements(By.TAG_NAME, "td")
        fila_texto = [celda.text.strip().replace('%','').strip() for celda in celdas]
        datos.append(fila_texto)
    
    df = pd.DataFrame(datos, columns=encabezados)
    print(f"Tabla extraída con {len(df)} filas y {len(df.columns)} columnas")
    return df

def main_scraping():
    base_url = "https://www.sbs.gob.pe/app/retasas/paginas/retasasInicio.aspx?p=D"
    driver.get(base_url)

    df_acumulado = pd.DataFrame()  # DataFrame vacío para acumular todos los datos
    
    try:
        regiones = get_options_text("ddlDepartamento")

        for region in regiones:
            select_option("ddlDepartamento", region)
            tipos_operacion = get_options_text("ddlTipoProducto")

            for tipo in tipos_operacion:
                select_option("ddlTipoProducto", tipo)
                productos = get_options_text("ddlProducto")

                for producto in productos:
                    select_option("ddlProducto", producto)
                    WebDriverWait(driver, 10).until(
                        lambda d: len(get_options_text("ddlCondicion")) > 0
                    )

                    condiciones = get_options_text("ddlCondicion")

                    if not condiciones:
                        print(f"Sin condiciones: {region} - {tipo} - {producto}")
                        continue

                    for condicion in condiciones:
                        try:
                            select_option("ddlCondicion", condicion)
                        except Exception as e:
                            print(f"Error seleccionando condición: {condicion} | {e}")
                            continue

                        try:
                            btn_consultar = wait.until(EC.element_to_be_clickable((By.ID, "btnConsultar")))
                            btn_consultar.click()
                            time.sleep(3)
                            
                            wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrmContendedor")))
                            df = extraer_tabla_manual()
                            driver.switch_to.default_content()

                            if df.empty:
                                print(f"Tabla vacía: {region}, {tipo}, {producto}, {condicion}")
                                continue

                            # Agregar columnas con metadatos
                            df['DEPARTAMENTO'] = region
                            df['TIPO_DE_PRODUCTO'] = tipo
                            df['PRODUCTO'] = producto
                            df['CONDICION'] = condicion
                            df['FECHA'] = datetime.now().strftime("%d-%m-%Y")

                            # Acumular
                            df_acumulado = pd.concat([df_acumulado, df], ignore_index=True)

                        except Exception as e:
                            print(f"Error en el proceso principal: {str(e)}")
                            driver.save_screenshot('error_screenshot.png')
                        
                        finally:
                            driver.get(base_url)
                            select_option("ddlDepartamento", region)
                            select_option("ddlTipoProducto", tipo)
                            select_option("ddlProducto", producto)

    except Exception as e:
        print(f"Error crítico: {str(e)}")
        driver.save_screenshot('critical_error.png')
    
    finally:
        driver.quit()
        print("Proceso completado")
    
    return df_acumulado

if __name__ == "__main__":
    df_final = main_scraping()
    print(f"Datos acumulados: {len(df_final)} filas")
   
    nueva_fecha = datetime.now().strftime('%d/%m/%Y')
    dia, mes, anio = nueva_fecha.split('/')
    fecha_consulta_f = f"{anio}-{mes}-{dia}"
    #df_final.to_excel("SBS_RETASAS_acumulado.xlsx", index=False)
    # Guardar CSV
    os.makedirs('historial', exist_ok=True)
    nombre_archivo = os.path.join('historial', f"producto_costo_{fecha_consulta_f}.csv")
    df_final.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
    print("✅ Archivo generado correctamente:", nombre_archivo)
