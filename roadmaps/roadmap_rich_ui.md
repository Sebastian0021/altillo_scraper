# Roadmap de Mejora de UI CLI con Rich

Este roadmap describe los pasos para transformar la interfaz de línea de comandos del proyecto usando la librería Rich y navegación dinámica.

## 1. Definición del Alcance y Dependencias
- Identificar los objetivos de mejora (menús dinámicos, animación de descargas, colores y UI amigable).
- Determinar las librerías necesarias: `rich` (principal), `readchar` o similar para input con flechas.

## 2. Análisis del Código Actual
- Revisar todos los puntos de entrada y salida de la UI en los archivos `cli.py` y funciones de descarga en `main.py`.
- Identificar los menús y prompts actuales que serán reemplazados.

## 3. Instalación y Configuración de Dependencias
- Añadir `rich` y otras librerías necesarias a `requirements.txt`.
- Probar la importación y funcionamiento básico de Rich en el proyecto.

## 4. Implementación de Menú Dinámico
- Crear una función reutilizable para menús navegables con flechas.
- Utilizar Rich para resaltar la opción seleccionada (color, subrayado, etc.).
- Reemplazar los menús actuales basados en `input()` por la nueva función.

## 5. Refactorización de Menús
- Adaptar los menús principales y secundarios (`menu_secciones`, `menu_anios`, `menu_parciales`, etc.) para usar la nueva función dinámica.
- Asegurar navegación fluida y visual atractiva.

## 6. Mejora de Animación de Descargas
- Integrar `rich.progress.Progress` en la función de descarga de archivos.
- Mostrar barras de progreso animadas y mensajes claros de éxito/error.

## 7. Pruebas, Ajustes y Documentación
- Realizar pruebas de usabilidad de la nueva UI.
- Ajustar detalles visuales: colores, paneles, mensajes de error y feedback.
- Documentar los cambios y el uso de la nueva interfaz en el README y este roadmap.

---

## Estado Actual

- ✅ Todos los puntos del roadmap han sido implementados: la CLI ahora cuenta con menús Rich interactivos, navegación por flechas, colores, barras de progreso animadas, mensajes claros y firma de autoría.
- La experiencia visual es moderna, clara y amigable para el usuario.

**Mejoras futuras sugeridas:**
- Agregar más ejemplos visuales o capturas de pantalla en la documentación.
- Explorar animaciones avanzadas con Rich si se desea aún más dinamismo.

Este roadmap sirvió como guía para implementar una CLI moderna, dinámica y amigable para el usuario.
