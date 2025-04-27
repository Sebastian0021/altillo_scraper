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
        print("Seleccione la sección:")
        for i, s in enumerate(secciones):
            print(f"  [{i+1}] {s}")
        print("  [0] Volver al menú principal")
        op = input("Opción: ").strip()
        if op == "0":
            return "menu_principal"
        if op.isdigit() and 1 <= int(op) <= len(secciones):
            return secciones[int(op)-1]

def menu_anios(estructura, seccion):
    while True:
        clear()
        anios = sorted(list(estructura[seccion].keys()))
        print(f"Sección: {seccion}")
        print("Seleccione el/los año/s a descargar:")
        for i, anio in enumerate(anios):
            print(f"  [{i+1}] {anio}")
        print("  [t] Descargar TODOS los años")
        print("  [rango] Descargar un rango (ej: 2020-2023)")
        print("  [varios] Descargar varios años separados por coma (ej: 2020,2022,2023)")
        print("  [0] Volver")
        op = input("Año/s: ").strip().lower()
        if op == "0":
            return None
        if op == "t":
            return anios
        # Rango de años
        if '-' in op:
            try:
                ini, fin = op.split('-')
                ini, fin = int(ini), int(fin)
                seleccionados = [a for a in anios if ini <= int(a) <= fin]
                if seleccionados:
                    return seleccionados
            except Exception:
                pass
            print("Rango inválido.")
            input("Presione Enter...")
            continue
        # Varios años selectos
        if ',' in op:
            seleccionados = [a for a in anios if a in [x.strip() for x in op.split(',')]]
            if seleccionados:
                return seleccionados
            print("Años inválidos.")
            input("Presione Enter...")
            continue
        # Selección individual
        if op.isdigit() and 1 <= int(op) <= len(anios):
            return [anios[int(op)-1]]
        if op in anios:
            return [op]
        print("Opción inválida.")
        input("Presione Enter...")

def menu_parciales(estructura, seccion, anio):
    while True:
        clear()
        links = estructura[seccion][anio]
        print(f"Sección: {seccion} | Año: {anio}")
        print("Seleccione los parciales a descargar (separados por coma, o 't' para TODOS los parciales del año):")
        for i, (link_text, link_href) in enumerate(links):
            clean_text = ' '.join(link_text.split())  # Elimina saltos de línea y espacios extra
            print(f"  [{i+1}] {clean_text} - {link_href}")
        print("  [t] Descargar TODOS los parciales del año")
        print("  [0] Volver")
        seleccion = input("Parciales: ").strip().lower()
        if seleccion == "0":
            return None
        if seleccion == "":
            continue
        if seleccion == "t":
            return links
        idxs = [int(x)-1 for x in seleccion.split(",") if x.strip().isdigit()]
        seleccionados = [links[i] for i in idxs if 0 <= i < len(links)]
        if seleccionados:
            return seleccionados

from pdf_utils import generar_pdf_seccion

def navegar_carpetas_y_generar_pdf(base_dir='descargas'):
    actual = base_dir
    while True:
        clear()
        if not os.path.exists(actual):
            print(f"No existe la carpeta {actual}")
            input("Presione Enter para volver...")
            return
        items = sorted(os.listdir(actual))
        dirs = [d for d in items if os.path.isdir(os.path.join(actual, d))]
        print(f"Carpeta actual: {actual}\nSeleccione una carpeta para navegar o generar PDF:")
        for i, d in enumerate(dirs):
            print(f"  [{i+1}] {d}/")
        print(f"  [g] Generar PDF de esta carpeta")
        if os.path.abspath(actual) != os.path.abspath(base_dir):
            print(f"  [..] Subir un nivel")
        print(f"  [0] Volver al menú principal")
        op = input("Opción: ").strip()
        if op == "0":
            return
        if op == "..":
            if os.path.abspath(actual) == os.path.abspath(base_dir):
                continue
            actual = os.path.dirname(actual)
            continue
        if op == "g":
            generar_pdf_seccion(actual)
            input("\nPresione Enter para continuar...")
            continue
        if op.isdigit() and 1 <= int(op) <= len(dirs):
            actual = os.path.join(actual, dirs[int(op)-1])
            continue

def main():
    while True:
        clear()
        print("--- Altillo Scraper CLI ---")
        print("[1] Descargar exámenes")
        print("[2] Generar PDF a partir de carpeta descargada")
        print("[0] Salir")
        op = input("Opción: ").strip()
        if op == "1":
            url, rel_url = input_url()
            estructura = download_and_analyze(url)
            while True:
                seccion = menu_secciones(estructura)
                if seccion == "menu_principal":
                    break  # Volver al menú principal
                anios = menu_anios(estructura, seccion)
                if anios is None:
                    continue  # Volver a seleccionar sección
                # Soportar lista de años
                for anio in anios:
                    seleccionados = menu_parciales(estructura, seccion, anio)
                    if seleccionados is None:
                        continue  # Saltar a otro año o volver a seleccionar sección
                    partes = [p for p in rel_url.split("/") if p and not p.lower().endswith(".asp")]
                    materia = partes[-1] if partes else "materia"
                    destino = input(f"Carpeta destino [descargas/{materia}/{seccion.replace(' ','_').lower()}/{anio}]: ").strip()
                    if not destino:
                        destino = os.path.join("descargas", materia, seccion.replace(' ','_').lower(), anio)
                    print(f"Descargando {len(seleccionados)} archivos a {destino} ...")
                    base_url = BASE_URL + os.path.dirname(rel_url) + "/"
                    download_links(seleccionados, base_url, destino)
                    input(f"\nDescarga finalizada para {anio}. Presione Enter para continuar...")
                # Al finalizar todos los años, vuelve a menú de secciones para seguir descargando


        elif op == "2":
            navegar_carpetas_y_generar_pdf()
        elif op == "0":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida.")
            input("Presione Enter para continuar...")


if __name__ == "__main__":
    main()
