# altillo_scraper

Scraper universal para descargar exámenes de cualquier materia disponible en [Altillo.com](https://www.altillo.com/examenes/), con organización automática por materia, sección y año. Interfaz interactiva por consola.

---

## 🚀 Recomendación de uso

> **Ejecuta siempre el programa desde `cli.py` para la mejor experiencia interactiva:**
>
> ```bash
> python cli.py
> ```

---

## 🛠️ Instalación y entorno recomendado

1. **Crea un entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📋 ¿Qué hace este scraper?

- Permite elegir la materia y página de exámenes de Altillo (ej: `uba/cbc/algebra/index.asp`).
- Analiza la página y te muestra las secciones, años y parciales disponibles.
- Permite seleccionar exactamente qué descargar (secciones, años, parciales).
- Descarga PDFs y/o imágenes y los organiza automáticamente en carpetas:

  ```
  descargas/<materia>/<seccion>/<año>/
  ```

  Ejemplo: `descargas/algebra/primeros_parciales/2024/`

- Mantiene los nombres originales de los archivos.
- (Opcional) Puedes extenderlo para generar PDFs o logs.

---

## 🖥️ Uso paso a paso

1. **Ejecuta la interfaz CLI:**
   ```bash
   python cli.py
   ```
2. **Ingresa la ruta relativa de la materia** (ejemplo: `uba/cbc/algebra/index.asp`)
3. **Navega por los menús** para elegir sección, año y parciales a descargar.
4. **Los archivos se guardarán organizados** en la carpeta `descargas/`.

---

## 📝 Generación de PDF desde carpetas descargadas

El proyecto incluye una herramienta integrada en la CLI que permite generar un archivo PDF unificado a partir de los exámenes e imágenes descargados en una carpeta específica.

**¿Cómo se utiliza?**

1. Descarga los exámenes normalmente utilizando la CLI.
2. Selecciona la opción correspondiente en el menú para "Generar PDF".
3. Navega hasta la carpeta de descargas que deseas convertir (puede ser una materia, sección o año).
4. La herramienta combinará automáticamente todos los archivos PDF e imágenes presentes en la carpeta en un único archivo PDF.

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

## ✅ Buenas prácticas y recomendaciones

- **No subas tu entorno virtual ni archivos descargados a GitHub** (ya están ignorados en `.gitignore`).
- Si quieres compartir el proyecto, solo sube el código fuente y el `requirements.txt`.
- Puedes modificar el código para adaptarlo a otras estructuras de Altillo o agregar nuevas funciones.

---

## 📝 Créditos y licencia

- Proyecto desarrollado para facilitar el acceso organizado a exámenes de Altillo.com.
- Uso educativo.
