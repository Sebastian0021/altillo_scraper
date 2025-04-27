# Scraper de Exámenes de Álgebra CBC (UBA)

Este proyecto descarga automáticamente los exámenes de Álgebra CBC disponibles en Altillo.com, organizándolos por año y generando PDFs opcionales.

## Uso rápido

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el scraper:
   ```bash
   python main.py
   ```

## Estructura esperada
- `Examenes_Algebra/`
  - `2024/`, `2023/`, ...
    - Imágenes descargadas
    - (Opcional) `2024.pdf`, ...

## Opciones avanzadas
- Puedes modificar el código en `main.py` para ajustar el scraping, la organización o la generación de PDFs.

## Notas
- El scraper respeta las buenas prácticas de scraping.
- (Opcional) Puedes implementar logs para registrar operaciones y errores.
# altillo_scraper
