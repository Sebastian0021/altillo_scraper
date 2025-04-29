import os
import tempfile
import img2pdf
from PyPDF2 import PdfMerger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

def generar_pdf_seccion(seccion_folder, salida_pdf=None, solo_enunciados=False):
    """
    Genera un único PDF combinando todos los PDFs y las imágenes (agrupadas por subcarpeta) de la carpeta fuente.
    Args:
        seccion_folder (str): Carpeta de la sección (ej: descargas/algebra/primeros_parciales/2024)
        salida_pdf (str, opcional): Ruta del PDF final. Si es None, se genera nombre automático.
    """

    imagenes_ext = ('.jpg', '.jpeg', '.png', '.gif')
    pdfs = []
    temp_files = []
    # 1. PDFs sueltos e imágenes en la carpeta fuente
    imagenes_principales = []
    for fname in sorted(os.listdir(seccion_folder)):
        ruta = os.path.join(seccion_folder, fname)
        if os.path.isfile(ruta):
            if fname.lower().endswith('.pdf'):
                pdfs.append(ruta)
            elif fname.lower().endswith(imagenes_ext):
                imagenes_principales.append(ruta)
    # Si hay imágenes en la carpeta principal, conviértelas a PDF temporal
    if imagenes_principales:
        imagenes_principales.sort()
        if solo_enunciados:
            imagenes_principales = imagenes_principales[:1]
        temp_fd, temp_pdf = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)
        with open(temp_pdf, 'wb') as f:
            f.write(img2pdf.convert(imagenes_principales))
        temp_files.append(temp_pdf)
        pdfs.append(temp_pdf)
    def recolectar_primera_imagen_hojas(carpeta):
        """Busca recursivamente la primera imagen de cada subcarpeta hoja (sin subcarpetas) que tenga imágenes."""
        imagenes_encontradas = []
        for root, dirs, files in os.walk(carpeta):
            # Es hoja si no tiene subcarpetas
            if not dirs:
                imagenes = sorted([os.path.join(root, f) for f in files if f.lower().endswith(imagenes_ext)])
                if imagenes:
                    imagenes_encontradas.append(imagenes[0])
        return imagenes_encontradas

    def recolectar_todas_las_imagenes_recursiva(carpeta):
        """Busca recursivamente todas las imágenes en todos los niveles y retorna una lista ordenada."""
        todas = []
        for root, dirs, files in os.walk(carpeta):
            imagenes = sorted([os.path.join(root, f) for f in files if f.lower().endswith(imagenes_ext)])
            todas.extend(imagenes)
        return todas

    if solo_enunciados:
        # Solo la primera imagen de cada subcarpeta hoja (parcial)
        todas_las_imagenes = recolectar_primera_imagen_hojas(seccion_folder)
        console.print(f"[cyan]Total de enunciados (primeras imágenes de parciales) encontrados: {len(todas_las_imagenes)}[/cyan]")
        for img in todas_las_imagenes:
            console.print(f"[dim]Enunciado:[/dim] {img}")
        if todas_las_imagenes:
            temp_fd, temp_pdf = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
            with open(temp_pdf, 'wb') as f:
                f.write(img2pdf.convert(todas_las_imagenes))
            temp_files.append(temp_pdf)
            pdfs.append(temp_pdf)
    else:
        # Recolecta todas las imágenes recursivamente
        todas_las_imagenes = recolectar_todas_las_imagenes_recursiva(seccion_folder)
        console.print(f"[cyan]Total de imágenes encontradas: {len(todas_las_imagenes)}[/cyan]")
        for img in todas_las_imagenes:
            console.print(f"[dim]Imagen:[/dim] {img}")
        if todas_las_imagenes:
            temp_fd, temp_pdf = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
            with open(temp_pdf, 'wb') as f:
                f.write(img2pdf.convert(todas_las_imagenes))
            temp_files.append(temp_pdf)
            pdfs.append(temp_pdf)
        # PDFs sueltos recursivos (además de imágenes)
        for root, dirs, files in os.walk(seccion_folder):
            pdfs_sueltos = sorted([os.path.join(root, f) for f in files if f.lower().endswith('.pdf')])
            pdfs.extend(pdfs_sueltos)
    pdfs.sort()

    pdfs.sort()

    if not salida_pdf:
        nombre = os.path.basename(os.path.normpath(seccion_folder))
        if solo_enunciados:
            salida_pdf = os.path.join(seccion_folder, f"{nombre} (solo-enunciado).pdf")
        else:
            salida_pdf = os.path.join(seccion_folder, f"{nombre}.pdf")
    merger = PdfMerger()
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold magenta]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        merge_task = progress.add_task("Uniendo PDFs...", total=len(pdfs))
        for pdf in pdfs:
            try:
                if solo_enunciados:
                    if pdf in temp_files:
                        # PDF generado a partir de imágenes: agregar TODAS las páginas
                        merger.append(pdf)
                    else:
                        # Solo la primera página de cada PDF suelto
                        with open(pdf, 'rb') as f:
                            from PyPDF2 import PdfReader
                            reader = PdfReader(f)
                            if len(reader.pages) > 0:
                                merger.append(reader, pages=(0,1))
                else:
                    merger.append(pdf)
                progress.console.print(f"[green]✔ Agregado:[/green] {os.path.basename(pdf)}")
            except Exception as e:
                progress.console.print(f"[red]✖ No se pudo agregar {pdf}: {e}[/red]")
            progress.update(merge_task, advance=1)
        merger.write(salida_pdf)
        merger.close()
    for temp in temp_files:
        try:
            os.remove(temp)
        except Exception:
            pass
    console.print(f"[bold green]PDF generado:[/bold green] [underline]{salida_pdf}[/underline]")
    return salida_pdf


if __name__ == "__main__":
    # Test rápido: cambiar la ruta a una carpeta real
    carpeta = "descargas/algebra/primeros_parciales/2024"
    generar_pdf_seccion(carpeta)
