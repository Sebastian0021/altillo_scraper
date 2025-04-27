import os
import tempfile
import img2pdf
from PyPDF2 import PdfMerger

def generar_pdf_seccion(seccion_folder, salida_pdf=None):
    """
    Genera un único PDF combinando todos los PDFs y las imágenes (agrupadas por subcarpeta) de la carpeta fuente.
    Args:
        seccion_folder (str): Carpeta de la sección (ej: descargas/algebra/primeros_parciales/2024)
        salida_pdf (str, opcional): Ruta del PDF final. Si es None, se genera nombre automático.
    """
    import os
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
            for root, _, files in os.walk(sub_path):
                files = sorted(files)
                for fname in files:
                    ruta = os.path.join(root, fname)
                    if fname.lower().endswith(imagenes_ext):
                        imagenes.append(ruta)
                    elif fname.lower().endswith('.pdf'):
                        sub_pdfs.append(ruta)
            # Si hay imágenes, las convertimos a PDF único por parcial
            if imagenes:
                imagenes = sorted(imagenes)
                temp_fd, temp_pdf = tempfile.mkstemp(suffix='.pdf')
                os.close(temp_fd)
                with open(temp_pdf, 'wb') as f:
                    f.write(img2pdf.convert(imagenes))
                pdfs.append(temp_pdf)
                temp_files.append(temp_pdf)
            # Agregar PDFs sueltos en la subcarpeta
            for p in sorted(sub_pdfs):
                pdfs.append(p)
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
    for temp in temp_files:
        try:
            os.remove(temp)
        except Exception:
            pass
    print(f"PDF generado: {salida_pdf}")
    return salida_pdf


if __name__ == "__main__":
    # Test rápido: cambiar la ruta a una carpeta real
    carpeta = "descargas/algebra/primeros_parciales/2024"
    generar_pdf_seccion(carpeta)
