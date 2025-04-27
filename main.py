import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

# Opcional para PDF
def try_import_pdf():
    try:
        import img2pdf
        return 'img2pdf'
    except ImportError:
        try:
            from fpdf import FPDF
            return 'fpdf'
        except ImportError:
            return None

PDF_LIB = try_import_pdf()

# --- Scraping Functions ---
def get_sections_years_links_from_file(html_path):
    """
    Parsea el archivo local HTML y retorna un dict {seccion: {año: [links]}} de manera dinámica.
    """
    print(f"Analizando archivo local: {html_path}")
    from bs4 import BeautifulSoup
    import re
    with open(html_path, encoding="latin1") as f:
        soup = BeautifulSoup(f, 'html.parser')

    result = {}
    # Buscar el <ul> principal
    main_ul = soup.find('ul')
    if not main_ul:
        print("No se encontró el <ul> principal")
        return result

    for li in main_ul.find_all('li', recursive=False):
        # Detectar la sección por <a name=...>
        section_a = li.find('a', attrs={'name': True})
        if not section_a:
            continue
        section_name = section_a.get('name').strip()
        section_title = section_a.get_text(strip=True)

        # Procesar el <ul> hijo para extraer años y links mezclados en cada <li>
        child_ul = li.find('ul')
        if not child_ul:
            continue

        years_links = {}
        for child_li in child_ul.find_all('li', recursive=False):
            # Parser secuencial: recorre los hijos del <li> y asocia links al año correcto
            from bs4 import NavigableString, Tag
            current_year = None
            for node in child_li.descendants:
                if isinstance(node, NavigableString):
                    # Buscar año en el texto
                    matches = re.findall(r'(20\d{2}|19\d{2})', str(node))
                    if matches:
                        current_year = matches[-1]
                elif isinstance(node, Tag) and node.name == 'a' and node.has_attr('href') and node['href'].endswith(('.asp', '.pdf')):
                    if current_year:
                        if current_year not in years_links:
                            years_links[current_year] = []
                        # Guardar tupla (texto, href)
                        years_links[current_year].append((node.get_text(strip=True), node['href']))
            # Si algún año no tiene links, no lo agregamos
        if years_links:
            result[section_title] = years_links

        # Solo agregar si hay años válidos
        if years_links:
            result[section_title] = years_links

    print("\nEstructura detectada (sección > año > cantidad de links):")
    for section, years in result.items():
        print(f"{section}:")
        for year, links in years.items():
            print(f"  {year}: {len(links)} links")
    return result

def get_images_from_exam_file(html_path):
    """
    Parsea un archivo local de parcial y devuelve una lista de URLs de imágenes dentro del div.exam_text
    """
    from bs4 import BeautifulSoup
    with open(html_path, encoding="latin1") as f:
        soup = BeautifulSoup(f, 'html.parser')
    exam_div = soup.find('div', class_='exam_text')
    if not exam_div:
        print(f"No se encontró el div.exam_text en {html_path}")
        return []
    images = []
    for img in exam_div.find_all('img', src=True):
        images.append(img['src'])
    print(f"Imágenes encontradas en {html_path}: {len(images)}")
    for src in images:
        print(f"  {src}")
    return images

def get_images_from_exam(exam_url):
    """
    Dado un enlace a un parcial (URL absoluta o relativa), obtiene todas las URLs de imágenes asociadas.
    """
    import requests
    from bs4 import BeautifulSoup
    import time

    # Si el link es relativo, anteponer el dominio
    if exam_url.startswith("http"):
        url = exam_url
    else:
        url = f"https://www.altillo.com/examenes/uba/cbc/algebra/{exam_url}"
    try:
        resp = requests.get(url, timeout=10)
        resp.encoding = resp.apparent_encoding
        if resp.status_code != 200:
            print(f"[ERROR] No se pudo acceder a {url} (status {resp.status_code})")
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        exam_div = soup.find('div', class_='exam_text')
        if not exam_div:
            print(f"[WARN] No se encontró el div.exam_text en {url}")
            return []
        images = []
        for img in exam_div.find_all('img', src=True):
            images.append(img['src'])
        return images
    except Exception as e:
        print(f"[ERROR] Excepción en {url}: {e}")
        return []

# --- Download Functions ---
def download_image(img_url, dest_path):
    """Descarga una imagen y la guarda en la ruta destino."""
    # TODO: Implementar
    pass

# --- Organization Functions ---
def organize_images_by_year(images_dict):
    """Organiza las imágenes descargadas en carpetas por año."""
    # TODO: Implementar
    pass

# --- PDF Generation (Optional) ---
import img2pdf
from PyPDF2 import PdfMerger

def generar_pdf_seccion(seccion_folder, salida_pdf=None):
    """
    Genera un único PDF combinando todas las imágenes y PDFs de la carpeta (recursivo).
    Args:
        seccion_folder (str): Carpeta de la sección (ej: descargas/algebra/primeros_parciales/2024)
        salida_pdf (str, opcional): Ruta del PDF final. Si es None, se genera nombre automático.
    """
    import os, tempfile, glob
    imagenes_ext = ('.jpg', '.jpeg', '.png')
    pdfs = []
    temp_files = []
    # Recorrer recursivamente
    for root, _, files in os.walk(seccion_folder):
        files = sorted(files)
        for fname in files:
            ruta = os.path.join(root, fname)
            if fname.lower().endswith(imagenes_ext):
                # Convertir imagen a PDF temporal
                temp_fd, temp_pdf = tempfile.mkstemp(suffix='.pdf')
                os.close(temp_fd)
                with open(temp_pdf, 'wb') as f:
                    f.write(img2pdf.convert(ruta))
                pdfs.append(temp_pdf)
                temp_files.append(temp_pdf)
            elif fname.lower().endswith('.pdf'):
                pdfs.append(ruta)
    if not pdfs:
        print(f"No se encontraron imágenes ni PDFs en {seccion_folder}")
        return None
    if salida_pdf is None:
        nombre = os.path.basename(os.path.normpath(seccion_folder))
        salida_pdf = os.path.join(seccion_folder, f"{nombre}.pdf")
    merger = PdfMerger()
    for pdf in pdfs:
        try:
            merger.append(pdf)
        except Exception as e:
            print(f"[ERROR] No se pudo agregar {pdf}: {e}")
    merger.write(salida_pdf)
    merger.close()
    # Limpiar temporales
    for temp in temp_files:
        try:
            os.remove(temp)
        except Exception:
            pass
    print(f"PDF generado: {salida_pdf}")
    return salida_pdf

# --- Test rápido ---
if __name__ == "__main__":
    # Cambia esta ruta por una carpeta de sección real con imágenes y PDFs
    carpeta = "descargas/algebra/primeros_parciales/2024"
    generar_pdf_seccion(carpeta)


# --- Main Execution ---
def main():
    print("Iniciando scraper de exámenes de Álgebra CBC...")
    # Usar el archivo local HTML y mostrar la estructura por secciones
    sections = get_sections_years_links_from_file("page.html")
    for section, years in sections.items():
        print(f"Sección: {section}")
        for year, links in years.items():
            print(f"  Año {year}: {len(links)} links")
    print("Fin de validación de estructura por secciones.")

    # --- Prueba de scraping real: primeros parciales 2024 ---
    print("\nScraping real: primeros parciales 2024")
    seccion = "primeros_parciales"
    year = "2022"
    sections = get_sections_years_links_from_file("page.html")
    links = sections.get(seccion, {}).get(year, [])
    print(f"Total de links a procesar: {len(links)} (solo los 3 primeros para prueba)")
    import os
    for i, link in enumerate(links[:3]):
        print(f"\n[{i+1}] Parcial: {link}")
        # base_folder = os.path.join(seccion, year)
        # os.makedirs(base_folder, exist_ok=True)
        # nombre = os.path.splitext(os.path.basename(link))[0]
        # parcial_folder = os.path.join(base_folder, nombre)
        # os.makedirs(parcial_folder, exist_ok=True)
        if link.endswith('.pdf'):
            print(f"  [PDF] (simulado) URL: {link if link.startswith('http') else f'https://www.altillo.com/examenes/uba/cbc/algebra/{link}'}")
        else:
            images = get_images_from_exam(link)
            print(f"  Imágenes encontradas: {len(images)} (no se descargan en modo test)")
            for img in images:
                print(f"    [IMG] (simulado) URL: {img if img.startswith('http') else f'https://www.altillo.com/examenes/uba/cbc/algebra/{img}'}")

def fix_encoding(text):
    # Intenta arreglar problemas de doble decodificación latin1/utf8
    try:
        return text.encode('latin1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def save_scrap_analysis(structure, materia="Álgebra CBC", out_path="scrap.txt"):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"Materia: {materia}\n\n")
        for section, years in structure.items():
            section_fixed = fix_encoding(section)
            f.write(f"Sección: {section_fixed}\n")
            for year, links in years.items():
                year_fixed = fix_encoding(year)
                f.write(f"  Año: {year_fixed}\n")
                for link_text, link_href in links:
                    link_text_fixed = fix_encoding(link_text)
                    link_href_fixed = fix_encoding(link_href)
                    f.write(f"    {link_text_fixed}: {link_href_fixed}\n")
            f.write("\n")
    print(f"\nAnálisis estructurado guardado en {out_path}\n")


import os
import requests

from bs4 import BeautifulSoup

def download_links(links, base_url, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for link_text, link_href in links:
        if link_href.lower().endswith('.pdf'):
            # Descargar PDF normal
            url = link_href if link_href.startswith('http') else base_url + link_href
            fname = os.path.join(out_dir, link_href.split('/')[-1])
            print(f"Descargando PDF {link_text}: {url} -> {fname}")
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                with open(fname, 'wb') as f:
                    f.write(resp.content)
                print(f"  OK")
            except Exception as e:
                print(f"  ERROR: {e}")
        elif link_href.lower().endswith('.asp'):
            # Descargar HTML y extraer imágenes
            url = link_href if link_href.startswith('http') else base_url + link_href
            print(f"Descargando examen {link_text}: {url}")
            try:
                resp = requests.get(url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.content, 'html.parser')
                img_tags = soup.find_all('img')
                if not img_tags:
                    print("  No se encontraron imágenes en el examen.")
                    continue
                # Carpeta para este examen (sin .asp)
                exam_name = os.path.splitext(link_href.split('/')[-1])[0]
                exam_dir = os.path.join(out_dir, exam_name)
                os.makedirs(exam_dir, exist_ok=True)
                for img in img_tags:
                    img_src = img.get('src')
                    if not img_src:
                        continue
                    img_url = img_src if img_src.startswith('http') else base_url + img_src
                    img_fname = os.path.join(exam_dir, img_src.split('/')[-1])
                    print(f"  Descargando imagen: {img_url} -> {img_fname}")
                    try:
                        img_resp = requests.get(img_url)
                        img_resp.raise_for_status()
                        with open(img_fname, 'wb') as f:
                            f.write(img_resp.content)
                        print(f"    OK")
                    except Exception as e:
                        print(f"    ERROR: {e}")
            except Exception as e:
                print(f"  ERROR: {e}")
        else:
            print(f"Tipo de archivo no soportado: {link_href}")

if __name__ == "__main__":
    # --- Análisis dinámico ---
    estructura = get_sections_years_links_from_file("page.html")
    save_scrap_analysis(estructura)

    # Descargar todos los primeros parciales del año 2024
    seccion = "Segundos Parciales"
    anio = "2024"
    base_url = "https://www.altillo.com/examenes/uba/cbc/algebra/"
    if seccion in estructura and anio in estructura[seccion]:
        links = estructura[seccion][anio]
        out_dir = os.path.join("descargas", "segundos_parciales", anio)
        download_links(links, base_url, out_dir)
    else:
        print(f"No se encontraron links para {seccion} año {anio}")
    # (El resto del main queda comentado o en modo test)

