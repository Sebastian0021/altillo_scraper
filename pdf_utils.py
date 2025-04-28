import os
import tempfile
import img2pdf
from PyPDF2 import PdfMerger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn

console = Console()

def generar_pdf_seccion(seccion_folder, salida_pdf=None):
    """
    Genera un único PDF combinando todos los PDFs y las imágenes (agrupadas por subcarpeta) de la carpeta fuente.
    Args:
        seccion_folder (str): Carpeta de la sección (ej: descargas/algebra/primeros_parciales/2024)
        salida_pdf (str, opcional): Ruta del PDF final. Si es None, se genera nombre automático.
    """

    imagenes_ext = ('.jpg', '.jpeg', '.png')
    pdfs = []
    temp_files = []
    # 1. PDFs sueltos en la carpeta fuente
    for fname in sorted(os.listdir(seccion_folder)):
        ruta = os.path.join(seccion_folder, fname)
        if os.path.isfile(ruta) and fname.lower().endswith('.pdf'):
            pdfs.append(ruta)
    # 2. Subcarpetas (parciales)
    for sub in sorted(os.listdir(seccion_folder)):
        sub_path = os.path.join(seccion_folder, sub)
        if os.path.isdir(sub_path):
            imagenes = []
            sub_pdfs = []
    pdfs.sort()
    if not salida_pdf:
        nombre = os.path.basename(os.path.normpath(seccion_folder))
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
