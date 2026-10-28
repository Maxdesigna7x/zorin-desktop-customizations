# Validación y capturas reproducibles

## Comprobaciones de este repositorio

```bash
make check
# Sin Node/Make, las pruebas Python se pueden ejecutar por separado:
python3 -m unittest discover -s tests -v
```

En el equipo de referencia se ejecutaron seis pruebas Python, incluida la integración con archivos reales de las extensiones:

- Formato de hashes y presencia de módulos.
- Rechazo de fuentes desconocidas sin modificarlas.
- Copia/restauración y eliminación de archivos añadidos.
- Rechazo de restauración sobre archivos reemplazados por una actualización.
- Reconstrucción temporal de los originales revirtiendo los parches, aplicación de nuevo y comprobación de hashes finales.
- Preparación sobre una versión ya personalizada sin aplicar el parche por segunda vez.

La prueba de integración requiere extensiones Zorin instaladas que coincidan con los hashes originales o personalizados registrados. En un entorno sin Zorin se omite; las otras pruebas no validan por sí solas una sesión de escritorio.

También se comprobaron sintaxis Python, JavaScript y shell, compilación del esquema local, `doctor`, preparación del bundle y preparación/recompilación de un tema GDM en archivos temporales. **No se reinstalaron los cambios en el equipo anfitrión solo para preparar el repositorio**, ni se reinició GDM.

## Comprobaciones durante la implementación original

En sesiones GNOME Shell 46 separadas se verificaron el menú y la búsqueda; el clic derecho; la independencia de ambas listas; persistencia de una lista vacía; ventanas de prueba; minimización; cierre de la última ventana; aparición y ocultamiento con movimiento de puntero; tamaño/opacidad finales y limpieza de temporizadores.

La versión final de exclusión de grupos se comprobó por geometría y la demostración actual comprueba que pasar por el reloj no active la revelación. Esto no sustituye probar indicadores nuevos o configuraciones de monitores distintas.

## Regenerar capturas del menú y la barra

Con la personalización **ya instalada**, en un equipo Zorin compatible:

```bash
python3 scripts/capture_demo.py
```

El script crea un perfil temporal para GNOME, dconf, XDG y D-Bus, elige aplicaciones de prueba y captura los estados de la interfaz. La ventana de demostración usa GTK 3. No cambia las listas de favoritos de la sesión principal. Los logs quedan en `generated/demo-capture.log` y no se suben a Git.

La sesión de prueba usa las extensiones instaladas en el sistema; si aún no están personalizadas, la captura falla en vez de producir una demostración falsa. Se espera backend headless operativo de GNOME 46. Los portales gráficos pueden montar sistemas FUSE dentro del runtime temporal; el helper intenta desmontarlos antes de limpiar sus propios archivos.

## Regenerar comparación del fondo

Usa nombres nuevos si los PNG ya existen:

```bash
python3 scripts/render_blur.py --image docs/demo-wallpaper.svg \
  --output "$PWD/generated/demo-nitido.png" --width 1600 --height 900 --radius 0 --brightness 1
python3 scripts/render_blur.py --image docs/demo-wallpaper.svg \
  --output "$PWD/generated/demo-blur.png" --width 1600 --height 900 --radius 90 --brightness 0.65
```

Son capturas reales de un fondo renderizado por GNOME. No se modifica el wallpaper personal ni se aplica un cambio al gestor de inicio de sesión durante esta prueba.
