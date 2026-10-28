# Llevarlo a otro sistema

## Mismo Zorin y mismas versiones

La ruta rápida es ejecutar `doctor`, preparar e instalar. `compatibility.json` compara los archivos de las extensiones con los hashes originales y personalizados comprobados. Que ambos sistemas digan «Zorin 18» no garantiza que los paquetes sean idénticos.

## Otro Zorin o una actualización de GNOME

1. Guarda el estado actual y usa una máquina virtual o una sesión de prueba.
2. Obtén los archivos originales de la **versión de destino**. No uses como originales archivos que ya estén modificados.
3. Revisa los parches con el código nuevo: clases, métodos, señales, ciclo de vida, API de `St`, `Clutter` y `Shell` pueden variar.
4. Adapta los módulos de `components/` si cambiaron esas API. Revisa también el formato de `allocationMap` y las propiedades de iconos.
5. Genera nuevos parches y hashes de antes/después en `compatibility.json` después de revisar el resultado. **No basta con cambiar hashes para pasar la comprobación.**
6. Ejecuta pruebas y genera capturas en el destino. Comprueba el menú, la independencia de listas, minimización, cierre de ventanas, hover vacío, zonas excluidas, animación final, búsqueda, clic derecho y restauración.
7. Documenta la nueva combinación de paquetes como una variante comprobada; no sustituyas silenciosamente la compatibilidad anterior.

## Ubuntu, Fedora o Debian con GNOME estándar

El código parchea **Zorin Menu y Zorin Taskbar**. GNOME estándar no incluye esas extensiones, por lo que no basta con copiar los archivos o instalar los parches.

Opciones de adaptación:

- Si se instalan extensiones compatibles equivalentes, traducir los puntos de integración a su API.
- Reescribir la misma lógica como una extensión específica para el menú/dock elegido.
- Conservar la separación conceptual: dos listas persistentes diferentes, selección de aplicaciones con ventanas, detección de espacios vacíos y exclusión de controles.

Para GDM, comprobar el tema y las alternativas de la distribución. Ubuntu puede usar otra alternativa y recursos distintos; Fedora puede cargar otro tema. El script se detiene si no reconoce la estructura de Zorin. No lo apuntes a un recurso distinto sin revisar cómo se carga el greeter.

## Otros entornos

KDE, Cinnamon y XFCE tienen paneles y gestores de sesión distintos. Los requisitos visuales se pueden reproducir, pero se necesitan sus propias API, widgets o plugins. Estos scripts no son instaladores universales para Linux, Windows ni macOS.

## Wayland, X11, HiDPI y varios monitores

La implementación se desarrolló sobre la sesión X11 de Zorin del equipo original. Las capturas y comprobaciones aisladas ejecutan GNOME Shell 46 con backend Wayland headless. Eso no equivale a haber probado todas las configuraciones de una sesión Wayland real.

Cada instancia de barra tiene su propio controlador. Multi-monitor, escalado fraccional y disposiciones verticales requieren validación adicional; no se anuncian como combinaciones exhaustivamente probadas. El render de GDM guarda una sola resolución; compara el resultado en cada monitor y escala.
