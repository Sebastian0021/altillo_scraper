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
def get_sections_years_links_from_file(html_path=None, html_content=None, verbose=True):
    """
    Parsea un archivo local HTML o un string HTML y retorna un dict {seccion: {año: [links]}} de manera dinámica.
    Prioridad: html_content > html_path.
    """
    from bs4 import BeautifulSoup, NavigableString, Tag
    import re
    if html_content is not None:
        soup = BeautifulSoup(html_content, 'html.parser')
        if verbose:
            print("Analizando HTML recibido en memoria")
    elif html_path is not None:
        if verbose:
            print(f"Analizando archivo local: {html_path}")
        with open(html_path, encoding="latin1") as f:
            soup = BeautifulSoup(f, 'html.parser')
    else:
        raise ValueError("Se debe especificar html_path o html_content")

    result = {}
    
    # Encontrar todas las secciones principales (buscar por anclas 'a name=')
    section_anchors = soup.find_all('a', attrs={'name': True})
    
    for section_a in section_anchors:
        section_name = section_a.get('name').strip()
        section_title = section_a.get_text(strip=True)
        
        # Buscar la estructura de años que sigue a esta sección
        # Para manejar diferentes estructuras, buscamos cualquier <ul> que sea hermano o descendiente cercano
        
        # Primero, verificamos si estamos en un <li> que contiene un <ul>
        parent_li = section_a.find_parent('li')
        if parent_li:
            child_ul = parent_li.find('ul')
            if child_ul:
                years_links = process_years_section(child_ul)
                if years_links:
                    result[section_title] = years_links
                continue
        
        # Si no, buscamos el siguiente <ul> después de esta sección
        next_ul = None
        # Verificar si está en un <p> o <font> o similar
        container = section_a.find_parent(['p', 'font', 'b'])
        if container:
            # Buscar el siguiente <ul> después de este contenedor
            sibling = container.find_next_sibling()
            while sibling and not next_ul:
                if sibling.name == 'ul':
                    next_ul = sibling
                    break
                sibling = sibling.find_next_sibling()
        
        # Si encontramos un <ul>, procesarlo
        if next_ul:
            years_links = process_years_section(next_ul)
            if years_links:
                result[section_title] = years_links
    
    # Mostrar la estructura detectada
    if verbose:
        print("Estructura detectada (sección > año > cantidad de links):")
        for section, years in result.items():
            print(f"{section}:")
            for year, links in years.items():
                print(f"  {year}: {len(links)} links")
    return result

def process_years_section(ul_element):
    """
    Procesa un elemento <ul> que contiene años y links
    """
    import re
    from bs4 import NavigableString, Tag
    
    years_links = {}
    
    for li in ul_element.find_all('li', recursive=False):
        # Parser secuencial: recorre los hijos del <li> y asocia links al año correcto
        current_year = None
        
        for node in li.descendants:
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
    
    return years_links

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

def save_scrap_analysis(structure, materia="Álgebra CBC", out_path=None):
    """
    Si out_path se especifica, guarda el análisis en disco. Si no, retorna el string generado.
    """
    lines = [f"Materia: {materia}\n\n"]
    for section, years in structure.items():
        section_fixed = fix_encoding(section)
        lines.append(f"Sección: {section_fixed}\n")
        for year, links in years.items():
            year_fixed = fix_encoding(year)
            lines.append(f"  Año: {year_fixed}\n")
            for link_text, link_href in links:
                link_text_fixed = fix_encoding(link_text)
                link_href_fixed = fix_encoding(link_href)
                lines.append(f"    {link_text_fixed}: {link_href_fixed}\n")
        lines.append("\n")
    result_str = ''.join(lines)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result_str)
        print(f"\nAnálisis estructurado guardado en {out_path}\n")
    else:
        return result_str


import os
import requests

from bs4 import BeautifulSoup

from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

console = Console()

def download_links(links, base_url, out_dir, solo_primera_imagen=False):
    os.makedirs(out_dir, exist_ok=True)
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Descargando archivos...", total=len(links))
        for link_text, link_href in links:
            if link_href.lower().endswith('.pdf'):
                url = link_href if link_href.startswith('http') else base_url + link_href
                fname = os.path.join(out_dir, link_href.split('/')[-1])
                try:
                    resp = requests.get(url)
                    resp.raise_for_status()
                    with open(fname, 'wb') as f:
                        f.write(resp.content)
                    progress.console.print(f"[green]✔ PDF descargado:[/green] {link_text} -> {fname}")
                except Exception as e:
                    progress.console.print(f"[red]✖ Error descargando PDF {link_text}: {e}[/red]")
            elif link_href.lower().endswith('.asp'):
                url = link_href if link_href.startswith('http') else base_url + link_href
                try:
                    resp = requests.get(url)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    img_tags = soup.find_all('img')
                    if not img_tags:
                        progress.console.print(f"[yellow]No se encontraron imágenes en el examen {link_text}.[/yellow]")
                        progress.update(task, advance=1)
                        continue
                    exam_name = os.path.splitext(link_href.split('/')[-1])[0]
                    exam_dir = os.path.join(out_dir, exam_name)
                    os.makedirs(exam_dir, exist_ok=True)
                    parcial_name = str(link_text)[:22]
                    if solo_primera_imagen:
                        img_tags = img_tags[:1]
                        mensaje_extra = ' (posible enunciado)'
                    else:
                        mensaje_extra = ''
                    img_task = progress.add_task(f"Imágenes de {parcial_name}{mensaje_extra}", total=len(img_tags))
                    for idx, img in enumerate(img_tags, start=1):
                        img_src = img.get('src')
                        if not img_src:
                            progress.update(img_task, advance=1)
                            continue
                        img_url = img_src if img_src.startswith('http') else base_url + img_src
                        # Guardar como 1.jpg, 2.jpg, ... según el orden
                        ext = os.path.splitext(img_src)[-1].lower()
                        if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                            ext = '.jpg'  # fallback
                        img_fname = os.path.join(exam_dir, f"{idx}{ext}")
                        try:
                            img_resp = requests.get(img_url)
                            img_resp.raise_for_status()
                            with open(img_fname, 'wb') as f:
                                f.write(img_resp.content)
                            progress.console.print(f"[green]  ✔ Imagen descargada:[/green] {img_url} -> {img_fname}")
                        except Exception as e:
                            progress.console.print(f"[red]  ✖ Error descargando imagen {img_url}: {e}[/red]")
                        progress.update(img_task, advance=1)
                    progress.remove_task(img_task)
                except Exception as e:
                    progress.console.print(f"[red]✖ Error descargando examen {link_text}: {e}[/red]")
            else:
                progress.console.print(f"[yellow]Tipo de archivo no soportado:[/yellow] {link_href}")
            progress.update(task, advance=1)


def download_and_analyze(url, local_filename=None):
    clear()
    print(f"Descargando página: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    html_content = resp.content.decode('latin1', errors='replace')
    print("Página descargada. Analizando...")
    estructura = get_sections_years_links_from_file(html_content=html_content)

    return estructura

if __name__ == "__main__":
    # --- Análisis dinámico ---
    estructura = get_sections_years_links_from_file(html_path="page.html")
    save_scrap_analysis(estructura)

    # Descargar todos los primeros parciales del año 2024
    seccion = "Segundos Parciales"
    anio = "2024"
    base_url = "https://www.altillo.com/examenes/uba/cbc/algebra/"
