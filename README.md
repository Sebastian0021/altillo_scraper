# altillo_scraper 📚

Scraper universal para descargar exámenes de cualquier materia disponible en [Altillo.com](https://www.altillo.com/examenes/), con organización automática por materia, sección y año. Interfaz interactiva por consola.

> [!IMPORTANT]
>
> **Requisito:** Debes tener [Python 3.8+](https://www.python.org/downloads/) instalado en tu computadora.
>
> _En el futuro se planea ofrecer un ejecutable para usuarios sin experiencia en la terminal o entornos de desarrollo._

---

## 📋 ¿Qué hace este scraper?

- Permite elegir la materia y página de exámenes de Altillo (ej: `uba/cbc/algebra/index.asp`).
- Analiza la página y te muestra las secciones, años y parciales disponibles.
- Permite seleccionar exactamente qué descargar (secciones, años, parciales).
- Descarga PDFs y/o imágenes y los organiza automáticamente en **carpetas**:

  ```
  descargas/<materia>/<seccion>/<año>/
  ```

  Ejemplo: `descargas/algebra/primeros_parciales/2024/`

- Mantiene los nombres originales de los archivos.
- (Opcional) Puedes extenderlo para generar PDFs o logs.

---

## 📝 Generación de PDF desde carpetas descargadas

El proyecto incluye una herramienta integrada en la CLI que permite generar un archivo PDF unificado a partir de los exámenes e imágenes descargados en una carpeta específica.

**¿Cómo se utiliza?**

1. Descarga los exámenes normalmente utilizando la CLI.
2. Selecciona la opción correspondiente en el menú para "Generar PDF".
3. Navega hasta la carpeta de descargas que deseas convertir (puede ser una materia, sección o año).
4. La herramienta combinará automáticamente todos los archivos PDF e imágenes presentes en la carpeta en un único archivo PDF.

---

## 🚀 Instalación y ejecución

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/Sebastian0021/altillo_scraper.git
   cd altillo-scrapper
   ```

2. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

   Si usas Anaconda:

   ```bash
   conda create -n altillo-scraper python=3.10
   conda activate altillo-scraper
   pip install -r requirements.txt
   ```

3. **Ejecuta la CLI profesional:**
   ```bash
   python -m altillo_scraper.cli.main
   ```
   Esto lanzará el menú interactivo para descargar exámenes o generar PDFs desde carpetas descargadas.

---

## 🖥️ Uso paso a paso

1. **Ingresa la ruta relativa de la materia** (ejemplo: `uba/cbc/algebra/index.asp`)
2. **Navega por los menús** para elegir sección, año y parciales a descargar.
3. **Los archivos se guardarán organizados** en la carpeta `descargas/`.

---

## 📦 Características principales y organización de archivos

- Permite elegir la materia y página de exámenes de Altillo (ej: `uba/cbc/algebra/index.asp`).
- Analiza la página y te muestra las secciones, años y parciales disponibles.
- Permite seleccionar exactamente qué descargar (secciones, años, parciales).
- Descarga PDFs y/o imágenes y los organiza automáticamente en **carpetas**:

  ```
  descargas/<materia>/<seccion>/<año>/
  ```

  Ejemplo: `descargas/algebra/primeros_parciales/2024/`

- Mantiene los nombres originales de los archivos.
- (Opcional) Puedes extenderlo para generar PDFs o logs.

---

## 📦 Estructura de carpetas generada

```
descargas/
  └── algebra/
      └── primeros_parciales/
          └── 2024/
              ├── alg_2024_p1a/           # Carpeta de imágenes de un parcial
              ├── r98compressed.pdf       # PDF descargado
              └── ...
```

---

## 🎨 Experiencia Visual Mejorada con Rich

La CLI ahora ofrece una experiencia visual moderna y amigable gracias a la integración de la librería [Rich](https://rich.readthedocs.io/):

- **Menús interactivos y navegables:** Usa las flechas para moverte y Enter para seleccionar.
- **Colores y resaltado:** Diferenciación clara entre carpetas, acciones y rutas.
- **Barras de progreso animadas:** Durante descargas y generación de PDF.
- **Firma de autoría:** Siempre visible en la parte inferior de los menús.
- **Mensajes claros de éxito y error.**

**Ejemplo de menú:**

```
──────────────────────────── Carpeta actual: descargas/algebra/2024 ────────────────────────────
  alg_2024_p1a/
  alg_2024_p1b/
> Generar PDF de esta carpeta
  Carpeta anterior
  Volver al menú principal
────────────────────────────── Hecho por: https://sebastianpenaloza.com ──────────────────────────────
```

**Ejemplo de barra de progreso:**

```
Descargando archivos...
┃███████████████████████████████████████┃ 10/10 00:05
✔ Archivo descargado: alg_2024_p1a.pdf
```

---

> ```bash
> python cli.py
> ```

---

## ✅ Buenas prácticas y recomendaciones

- **No subas tu entorno virtual ni archivos descargados a GitHub** (ya están ignorados en `.gitignore`).
- Si quieres compartir el proyecto, solo sube el código fuente y el `requirements.txt`.
- Puedes modificar el código para adaptarlo a otras estructuras de Altillo o agregar nuevas funciones.

---

## 📝 Créditos y licencia

- Proyecto desarrollado por [Sebastian Peñaloza](https://sebastianpenaloza.com) 👨‍💻 (Sebastian0021) para facilitar el acceso organizado a exámenes de Altillo.com.
- Uso educativo.
