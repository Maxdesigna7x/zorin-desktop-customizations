# Problemas frecuentes

## No veo cambios tras instalar

Cierra sesión y vuelve a entrar. Comprueba que estén habilitadas `zorin-menu@zorinos.com` y/o `zorin-taskbar@zorinos.com`:

```bash
gnome-extensions info zorin-menu@zorinos.com
gnome-extensions info zorin-taskbar@zorinos.com
journalctl --user -b --no-pager | rg 'zorin|JS ERROR|TypeError'
```

Los nombres de aplicaciones y algunos textos pueden depender de la traducción disponible. Los títulos y acciones añadidos seleccionan español cuando el idioma de la sesión comienza por `es`.

## `prepare` se detiene con «versión no compatible»

No fuerces los hashes ni apliques el parche con tolerancia. Puede haber una actualización, una modificación anterior distinta o una extensión diferente. Sigue [Portabilidad](PORTABILITY.md). El diagnóstico puede marcar la barra como ausente y aun así permitir preparar solo el menú, o viceversa.

## Las listas del inicio y de la barra todavía cambian juntas

Asegúrate de haber instalado el componente `menu` completo, incluidos `menuFavorites.js` y su esquema, y de haber vuelto a entrar en la sesión. En el menú debe aparecer **Agregar/Quitar de favoritos del inicio**, no la acción heredada del dash. La barra conserva los favoritos de GNOME; el inicio usa su clave propia.

## Iconos pequeños, incompletos o sin animación

Confirma que se aplicaron juntos el parche de `taskbar.js` y el módulo actual `compactFavorites.js`. La versión final evita la entrada por escala y asienta el tamaño a los 700 ms. Si GNOME tiene desactivadas las animaciones, el objetivo sigue siendo llegar al estado final completo.

## El reloj o el inicio revelan los favoritos

La versión final usa `allocationMap` para excluir los grupos completos. Si otra extensión añadió controles fuera de esos grupos, hay que incorporarlos a la detección. En otras versiones de Zorin puede haber cambiado el mapa; eso necesita una adaptación del componente.

Los iconos ya revelados permanecen al moverte dentro de la barra para poder usarlos. Las zonas excluidas impiden **activar** la revelación; no fuerzan su cierre inmediato al pasar por ellas.

## No se genera el fondo desenfocado

Lee el archivo `.render.log` junto al PNG de salida. El renderizador requiere un GNOME Shell 46 funcional con backend headless. No necesitas cerrar tu sesión actual; se crea otra sesión temporal. La disponibilidad del backend gráfico depende de GPU/controladores y del sistema.

No ejecutes el renderizador como root. `sudo` solo corresponde a instalar/restaurar. Si la generación falla, no se aplica ningún tema a GDM. Un archivo de salida existente no se sobrescribe: elige otro nombre o aparta la versión anterior.

## Cambié mi wallpaper y GDM conserva el anterior

Es intencionado: GDM usa una copia estática y no lee tu carpeta personal al arrancar. Renderiza y prepara otra imagen, luego aplica el recurso nuevo. El script conserva la alternativa original para la restauración.

## El fondo no se aplica o cambió tras una actualización

Comprueba:

```bash
readlink -f /usr/share/gnome-shell/gdm-theme.gresource
update-alternatives --query gdm-theme.gresource
```

Debe seleccionarse el recurso propio de `/usr/local/share/zorin-desktop-customizations/`. No sustituyas a ciegas `gdm3-theme.gresource`: en el Zorin de referencia se comprobó que el modo GDM usa `gdm-theme.gresource`. La estructura puede ser distinta en otra distribución.

## Recuperación del menú/barra

Normalmente:

```bash
sudo python3 scripts/customize.py restore
```

La restauración conserva la configuración de favoritos del usuario; revierte los archivos instalados. Si el estado anterior ya estaba personalizado, vuelve a ese estado anterior, no a un paquete original de fábrica.

Los respaldos permanecen en `/var/backups/zorin-desktop-customizations/`. Cada `plan.json` relaciona `target`, `backup`, hash previo y hash instalado. Si hubo una actualización, `restore` se detiene en vez de sobrescribirla. En ese caso, revisa las diferencias o reinstala los paquetes correspondientes desde los repositorios de tu distribución; no copies un respaldo antiguo sobre un paquete nuevo sin revisión.

Si una extensión impide usar el escritorio, entra por una TTY (por ejemplo Ctrl+Alt+F3) y ejecuta la restauración desde la carpeta del repositorio. Después vuelve a iniciar la sesión gráfica.

## Recuperación de GDM

```bash
sudo python3 scripts/wallpaper.py restore
```

La alternativa previa queda registrada en `/usr/local/share/zorin-desktop-customizations/gdm-state.json`. Si fuera necesario hacerlo manualmente, inspecciona su campo `Value` y selecciónalo con `update-alternatives --set gdm-theme.gresource RUTA_PREVIA`. Nunca reinicies GDM con trabajo sin guardar: cerraría la sesión.
