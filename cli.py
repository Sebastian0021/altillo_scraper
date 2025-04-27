import os
import sys
import requests
from main import get_sections_years_links_from_file, save_scrap_analysis, download_links

BASE_URL = "https://www.altillo.com/examenes/"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_url():
    clear()
    print("Ingrese la ruta relativa de la página de exámenes a partir de: https://www.altillo.com/examenes/")
    print("Ejemplo: uba/cbc/algebra/index.asp")
    rel_url = input("Ruta: ").strip()
    full_url = BASE_URL + rel_url
    return full_url, rel_url

def download_and_analyze(url, local_filename="page_tmp.html"):
    clear()
    print(f"Descargando página: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    with open(local_filename, "wb") as f:
        f.write(resp.content)
    print("Página descargada. Analizando...")
    estructura = get_sections_years_links_from_file(local_filename)
    save_scrap_analysis(estructura, out_path="scrap_tmp.txt")
    return estructura

def menu_secciones(estructura):
    while True:
        clear()
        secciones = list(estructura.keys())
        print("Seleccione una sección:")
        for i, sec in enumerate(secciones):
            print(f"  [{i+1}] {sec}")
        print("  [0] Salir")
        op = input("Opción: ").strip()
        if op == "0":
            sys.exit(0)
        if op.isdigit() and 1 <= int(op) <= len(secciones):
            return secciones[int(op)-1]

def menu_anios(estructura, seccion):
    while True:
        clear()
        anios = list(estructura[seccion].keys())
        print(f"Sección: {seccion}")
        print("Seleccione un año:")
        for i, anio in enumerate(anios):
            print(f"  [{i+1}] {anio}")
        print("  [0] Volver")
        op = input("Opción: ").strip()
        if op == "0":
            return None
        if op.isdigit() and 1 <= int(op) <= len(anios):
            return anios[int(op)-1]

def menu_parciales(estructura, seccion, anio):
    while True:
        clear()
        links = estructura[seccion][anio]
        print(f"Sección: {seccion} | Año: {anio}")
        print("Seleccione los parciales a descargar (separados por coma, 0 para todos):")
        for i, (link_text, link_href) in enumerate(links):
            clean_text = ' '.join(link_text.split())  # Elimina saltos de línea y espacios extra
            print(f"  [{i+1}] {clean_text} - {link_href}")
        print("  [0] Volver")
        seleccion = input("Parciales: ").strip()
        if seleccion == "0":
            return None
        if seleccion == "":
            continue
        if seleccion == "0":
            return links
        idxs = [int(x)-1 for x in seleccion.split(",") if x.strip().isdigit()]
        seleccionados = [links[i] for i in idxs if 0 <= i < len(links)]
        if seleccionados:
            return seleccionados

def main():
    url, rel_url = input_url()
    estructura = download_and_analyze(url)
    while True:
        seccion = menu_secciones(estructura)
        anio = menu_anios(estructura, seccion)
        if anio is None:
            continue
        seleccionados = menu_parciales(estructura, seccion, anio)
        if seleccionados is None:
            continue
        # Extraer materia de la ruta relativa (último segmento no vacío antes de index.asp, o penúltimo si termina en /index.asp)
        partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
        materia = partes[-1] if partes else "materia"
        destino = input(f"Carpeta destino [descargas/{materia}/{seccion.replace(' ','_').lower()}/{anio}]: ").strip()
        if not destino:
            destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
        print(f"Descargando {len(seleccionados)} archivos a {destino} ...")
        base_url = BASE_URL + os.path.dirname(rel_url) + "/"
        download_links(seleccionados, base_url, destino)
        input("\nDescarga finalizada. Presione Enter para volver al menú principal...")

if __name__ == "__main__":
    main()
