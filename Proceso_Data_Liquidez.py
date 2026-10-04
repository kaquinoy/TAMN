import json
import re
import time
from datetime import date
from os import replace
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import urlencode, urljoin

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


URL_BASE = "https://www.bcrp.gob.pe/operaciones-monetarias-y-cambiarias.html"
FECHA_INICIO = date(2009, 1, 5)
ARCHIVO_SALIDA = Path(__file__).with_name("operaciones_monetarias_bcrp.csv")
ARCHIVO_PROGRESO = Path(__file__).with_name("operaciones_monetarias_bcrp.progreso.json")
COLUMNAS = ["Fecha", "Hora", "Comentario", "Monto_millones", "Moneda"]
PAGINA_INICIAL_REANUDAR = 23
PATRON_MONTO = re.compile(
    r"(?P<moneda>US\$|S\s*/\s*\.?|S\.)\s*"
    r"(?P<monto>\d[\d\s.]*(?:,\d+)?)\s+millones?\b",
    re.IGNORECASE,
)


def extraer_monto(comentario):
    coincidencia = PATRON_MONTO.search(comentario)
    if coincidencia is None:
        return None, ""

    texto_monto = coincidencia.group("monto")
    monto = float(texto_monto.replace(" ", "").replace(".", "").replace(",", "."))
    contexto = comentario[max(0, coincidencia.start() - 40) : coincidencia.start()]
    if re.search(r"\bnegativ[oa]s?\b", contexto, re.IGNORECASE):
        monto = -monto

    moneda = "US$" if coincidencia.group("moneda").upper().startswith("US$") else "S/"
    return monto, moneda


def extraer_registros(soup):
    registros = []
    for bloque_fecha in soup.select(".newslist > div"):
        coincidencia_fecha = re.search(
            r"\d{4}/\d{2}/\d{2}", bloque_fecha.get_text(" ", strip=True)
        )
        if coincidencia_fecha is None:
            continue

        fecha = coincidencia_fecha.group(0)
        for elemento in bloque_fecha.select("ul.list-group > li"):
            hora_elemento = elemento.find("b")
            if hora_elemento is None:
                continue

            texto_hora = hora_elemento.get_text(" ", strip=True)
            hora = texto_hora.rstrip(": ").strip()
            comentario = elemento.get_text(" ", strip=True)[len(texto_hora) :].strip()
            monto, moneda = extraer_monto(comentario)
            registros.append(
                {
                    "Fecha": fecha,
                    "Hora": hora,
                    "Comentario": comentario,
                    "Monto_millones": monto,
                    "Moneda": moneda,
                }
            )

    return registros


def siguiente_pagina(soup, url_actual):
    for enlace in soup.select("a[href]"):
        if enlace.get_text(" ", strip=True).casefold() == "siguiente":
            return urljoin(url_actual, enlace["href"])
    return None


def cargar_pagina(page, url):
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    try:
        page.locator(".newslist ul.list-group li").first.wait_for(timeout=90_000)
    except PlaywrightTimeoutError as error:
        raise RuntimeError(
            "El BCRP no mostró registros. Verifica que Edge pueda abrir el portal "
            "y que no haya una verificación anti-bot pendiente."
        ) from error
    return BeautifulSoup(page.content(), "html.parser")


def construir_url(fecha_fin, numero_pagina):
    parametros = {"from": FECHA_INICIO.isoformat(), "to": fecha_fin.isoformat()}
    if numero_pagina > 1:
        parametros["page"] = str(numero_pagina)
    return f"{URL_BASE}?{urlencode(parametros)}"


def guardar_progreso(archivo_temporal, url_siguiente, pagina_siguiente):
    archivo_temporal_progreso = ARCHIVO_PROGRESO.with_suffix(".tmp")
    archivo_temporal_progreso.write_text(
        json.dumps(
            {
                "archivo_parcial": str(archivo_temporal.resolve()),
                "url_siguiente": url_siguiente,
                "pagina_siguiente": pagina_siguiente,
            }
        ),
        encoding="utf-8",
    )
    replace(archivo_temporal_progreso, ARCHIVO_PROGRESO)


def cargar_estado():
    if ARCHIVO_PROGRESO.exists():
        estado = json.loads(ARCHIVO_PROGRESO.read_text(encoding="utf-8"))
        archivo_temporal = Path(estado["archivo_parcial"])
        if not archivo_temporal.exists():
            raise RuntimeError(
                f"No se encuentra el CSV parcial indicado por {ARCHIVO_PROGRESO}."
            )
        print(
            f"Reanudando desde la página {estado['pagina_siguiente']}.", flush=True
        )
        return (
            archivo_temporal,
            estado["url_siguiente"],
            estado["pagina_siguiente"],
        )

    archivos_parciales = sorted(
        ARCHIVO_SALIDA.parent.glob("operaciones_bcrp_*.parcial.csv"),
        key=lambda archivo: archivo.stat().st_mtime,
        reverse=True,
    )
    if len(archivos_parciales) > 1:
        raise RuntimeError(
            "Hay varios CSV parciales y no se puede elegir cuál reanudar. "
            "Conserva el archivo correcto y mueve los demás fuera de esta carpeta."
        )

    if archivos_parciales:
        archivo_temporal = archivos_parciales[0]
        pagina_siguiente = PAGINA_INICIAL_REANUDAR
        url_siguiente = construir_url(date.today(), pagina_siguiente)
        guardar_progreso(archivo_temporal, url_siguiente, pagina_siguiente)
        print(
            f"CSV parcial encontrado. Reanudando desde la página {pagina_siguiente}.",
            flush=True,
        )
        return archivo_temporal, url_siguiente, pagina_siguiente

    with NamedTemporaryFile(
        prefix="operaciones_bcrp_",
        suffix=".parcial.csv",
        dir=ARCHIVO_SALIDA.parent,
        delete=False,
    ) as temporal:
        archivo_temporal = Path(temporal.name)

    pagina_siguiente = 1
    url_siguiente = construir_url(date.today(), pagina_siguiente)
    guardar_progreso(archivo_temporal, url_siguiente, pagina_siguiente)
    return archivo_temporal, url_siguiente, pagina_siguiente


def cargar_registros_existentes(archivo_temporal):
    if archivo_temporal.stat().st_size == 0:
        return set(), 0

    tabla = pd.read_csv(archivo_temporal, keep_default_na=False)
    vistos = set(
        tabla[["Fecha", "Hora", "Comentario"]].itertuples(index=False, name=None)
    )
    return vistos, len(tabla)


def main():
    fecha_fin = date.today()
    archivo_temporal, url_actual, numero_pagina = cargar_estado()
    vistos, total_registros = cargar_registros_existentes(archivo_temporal)

    print("Abriendo Microsoft Edge para consultar el portal del BCRP...", flush=True)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="msedge", headless=False)
            page = browser.new_page()
            while url_actual:
                try:
                    soup = cargar_pagina(page, url_actual)
                except PlaywrightError:
                    try:
                        browser.close()
                    except PlaywrightError:
                        pass
                    browser = playwright.chromium.launch(
                        channel="msedge", headless=False
                    )
                    page = browser.new_page()
                    soup = cargar_pagina(page, url_actual)
                registros = []
                for registro in extraer_registros(soup):
                    clave = (registro["Fecha"], registro["Hora"], registro["Comentario"])
                    if clave not in vistos:
                        vistos.add(clave)
                        registros.append(registro)

                if registros:
                    pd.DataFrame(registros, columns=COLUMNAS).to_csv(
                        archivo_temporal,
                        mode="a" if total_registros else "w",
                        header=total_registros == 0,
                        index=False,
                        encoding="utf-8-sig" if total_registros == 0 else "utf-8",
                    )
                    total_registros += len(registros)

                print(
                    f"Página {numero_pagina}: {len(registros)} registros; "
                    f"total {total_registros}",
                    flush=True,
                )
                url_actual = siguiente_pagina(soup, url_actual)
                numero_pagina += 1
                guardar_progreso(archivo_temporal, url_actual, numero_pagina)
                if url_actual:
                    time.sleep(0.25)
            browser.close()

        if total_registros == 0:
            raise RuntimeError("No se encontraron registros de operaciones monetarias.")

        replace(archivo_temporal, ARCHIVO_SALIDA)
        ARCHIVO_PROGRESO.unlink(missing_ok=True)
        print(
            f"Extracción finalizada: {total_registros} registros guardados en "
            f"{ARCHIVO_SALIDA}",
            flush=True,
        )
    except Exception:
        print(
            f"Extracción incompleta. Se reanudará desde la página {numero_pagina}. "
            f"CSV parcial: {archivo_temporal}",
            flush=True,
        )
        raise


if __name__ == "__main__":
    main()