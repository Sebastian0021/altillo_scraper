# Roadmap: Adaptación de la CLI a Windows CMD usando Rich

Este roadmap describe los pasos para mejorar la compatibilidad visual y funcional de la interfaz CLI basada en Rich en la consola cmd.exe de Windows, priorizando las recomendaciones oficiales de la documentación de Rich.

---

## 1. Diagnóstico y pruebas iniciales
- [x] Identificar los principales problemas visuales y de sobreescritura en cmd.exe.
- [x] Confirmar que en PowerShell y Windows Terminal la experiencia es aceptable.
- [ ] Documentar ejemplos de errores visuales (screenshots, descripciones).

## 2. Aplicar recomendaciones oficiales de Rich
- [ ] Usar `screen=True` en los contextos de `Live` para aprovechar la pantalla alterna y evitar sobreescritura.
- [ ] Ajustar el uso de `transient=True` para limpiar la pantalla tras menús interactivos si corresponde.
- [ ] Ajustar el parámetro `vertical_overflow` para evitar glitches visuales si el contenido es muy grande.
- [ ] Probar `refresh_per_second` y `auto_refresh` para reducir flicker.

## 3. Limpieza de pantalla y fallback manual
- [ ] Implementar limpieza manual con `os.system('cls')` en Windows si `console.clear()` no funciona correctamente.
- [ ] Detectar si el entorno es cmd.exe y, si es así, aplicar workarounds adicionales.

## 4. Ajustes de inicialización de Rich
- [ ] Inicializar `Console` con parámetros compatibles: `color_system='windows'`, `force_terminal=True/False` según detección.
- [ ] Permitir desactivar colores/effects si el usuario lo prefiere (modo simple).

## 5. Mensajes y recomendaciones al usuario
- [ ] Si se detecta cmd.exe, mostrar un aviso recomendando PowerShell o Windows Terminal para mejor experiencia.
- [ ] Documentar en el README y la ayuda de la CLI las limitaciones conocidas en cmd.exe.

## 6. Pruebas cruzadas y feedback
- [ ] Probar todos los cambios en cmd.exe, PowerShell y Windows Terminal.
- [ ] Recopilar feedback y ajustar parámetros según resultados.

---

> **Prioridad:** Seguir las recomendaciones de la documentación oficial de Rich antes de aplicar workarounds manuales.

Actualiza este roadmap a medida que avances y documenta los resultados de cada etapa.
