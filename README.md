# Personalización de Zorin: inicio, favoritos y barra inteligente

Receta reproducible de la personalización realizada en **Zorin OS 18.1, GNOME Shell 46**, con instrucciones en español, capturas de una sesión de prueba, instaladores por componente y restauración.

## Qué hace

1. **Menú de inicio:** una sección «Favoritos» encima de «Todas las aplicaciones»; su lista es independiente de la barra. El menú se abre siempre en el centro horizontal de su monitor, anclado encima de la barra, sin seguir al botón de inicio. Clic derecho → **Agregar/Quitar de favoritos del inicio**.
2. **Barra de tareas:** normalmente muestra solo aplicaciones con ventanas abiertas, incluidas las minimizadas. Al pasar el mouse por un **espacio vacío**, aparecen los favoritos en la misma barra. Se ocultan al salir. No hay botón `+` ni ventana desplegable.
3. **Zonas excluidas:** inicio, mostrar aplicaciones, reloj y grupos de indicadores no activan el efecto, incluidos los huecos internos de esos grupos.
4. **Animación:** entrada escalonada por opacidad y desplazamiento; corrección explícita del tamaño final para evitar iconos que queden pequeños.
5. **Inicio de sesión GDM:** el wallpaper elegido puede aparecer nítido o con el desenfoque de GNOME usado en el bloqueo: radio **90**, brillo **0,65**. No cambia el fondo del escritorio ni del bloqueo.

## Ver el resultado

Las imágenes son **capturas reales de una sesión GNOME aislada** que ejecuta las personalizaciones instaladas, con aplicaciones y preferencias de prueba. La distribución de los controles usa los valores por defecto de esa sesión; no reproduce todos los ajustes personales del equipo original.

### Inicio con favoritos propios

![Favoritos independientes en el menú de inicio](docs/images/01-menu-favoritos.png)

### Solo aplicaciones abiertas → favoritos en la misma barra

![Barra con una aplicación abierta](docs/images/03-barra-solo-abiertas.png)

![Favoritos revelados mediante hover sobre un espacio vacío](docs/images/04-barra-favoritos.png)

Más imágenes, comparación del fondo y explicación de cada estado en [Capturas](docs/SCREENSHOTS.md).

## Instalación rápida en un Zorin compatible

```bash
git clone https://github.com/Maxdesigna7x/zorin-desktop-customizations.git
cd zorin-desktop-customizations
python3 scripts/customize.py doctor
python3 scripts/customize.py prepare --components menu taskbar
sudo python3 scripts/customize.py install
```

Después, **cerrar sesión y volver a entrar**. La preparación no cambia archivos del sistema. La instalación comprueba de nuevo que nada haya cambiado y crea un respaldo antes de sustituir archivos.

Si `doctor` o `prepare` indican una versión no compatible, **detente y consulta [Compatibilidad y portabilidad](docs/PORTABILITY.md)**. No se deben forzar parches sobre otra versión de GNOME.

Atajo para repetir la instalación (diagnostica, prepara y solicita `sudo` al aplicar):

```bash
bash scripts/setup.sh              # menú y barra
bash scripts/setup.sh menu         # solo menú
bash scripts/setup.sh taskbar      # solo barra
```

Para instalar solo una función manualmente:

```bash
python3 scripts/customize.py prepare --components menu
# O bien:
python3 scripts/customize.py prepare --components taskbar
sudo python3 scripts/customize.py install
```

`install` aplica **el último bundle preparado**; preparar una segunda vez reemplaza esa selección, no instala ambos bundles anteriores.

La lista del menú se inicializa una sola vez copiando los favoritos existentes. Después las dos listas evolucionan por separado; una lista vacía permanece vacía. No se distribuye ninguna lista personal.

## Fondo de inicio con desenfoque

Este paso es independiente del menú y de la barra. Sustituye la ruta por tu propia imagen:

```bash
mkdir -p generated
python3 scripts/render_blur.py \
  --image "/ruta/a/tu-wallpaper.png" \
  --output "$PWD/generated/wallpaper-blur.png" \
  --width 1920 --height 1080
python3 scripts/wallpaper.py prepare --image "$PWD/generated/wallpaper-blur.png"
sudo python3 scripts/wallpaper.py apply
```

La imagen se renderiza con **Shell.BlurEffect de GNOME**, en una sesión temporal aislada. Usa la resolución de la pantalla de inicio deseada. El resultado es una imagen estática: si cambias de wallpaper o de resolución, vuelve a generarla. No se sincroniza automáticamente.

Para un fondo nítido, prepara directamente un PNG:

```bash
python3 scripts/wallpaper.py prepare --image "/ruta/a/tu-wallpaper.png"
sudo python3 scripts/wallpaper.py apply
```

El cambio se verá en el siguiente inicio de sesión o reinicio. Los scripts **no reinician GDM**, porque eso cerraría la sesión abierta.

## Volver atrás

```bash
# Menú y/o barra: volver al estado anterior a la última instalación del repositorio.
sudo python3 scripts/customize.py restore

# Tema de GDM: volver a la alternativa activa antes de usar este repositorio.
sudo python3 scripts/wallpaper.py restore
```

Cierra sesión y vuelve a entrar. Si una actualización del sistema cambió los archivos desde la instalación, la restauración del menú/barra se detiene para no sobrescribirla: revisa [Solución de problemas](docs/TROUBLESHOOTING.md).

## Compatibilidad real

| Entorno | Estado |
|---|---|
| Zorin OS 18.1 + GNOME Shell 46 + versiones exactas registradas | Base comprobada en el equipo original |
| Zorin con otros archivos/versiones de extensiones | Requiere adaptar y probar parches |
| Ubuntu/Fedora/Debian con GNOME estándar | No es instalación directa: faltan Zorin Menu/Taskbar y puede cambiar el tema de GDM |
| KDE Plasma, Cinnamon, XFCE, Windows, macOS | Requiere otra implementación |

Los archivos `compatibility.json` identifican la versión compatible por **SHA-256 del contenido**, no solo por el nombre de la distribución. El renderizador de desenfoque incluido declara GNOME 46; otras versiones requieren revisar sus API.

## Guías

- [Instalación detallada y requisitos](docs/INSTALL.md)
- [Compatibilidad y cómo portarlo a otro sistema](docs/PORTABILITY.md)
- [Arquitectura, almacenamiento y animaciones](docs/ARCHITECTURE.md)
- [Capturas explicadas](docs/SCREENSHOTS.md)
- [Solución de problemas y restauración](docs/TROUBLESHOOTING.md)
- [Validación y reproducción de capturas](docs/VALIDATION.md)

## Licencia y origen

GPL-3.0-or-later. Los parches conservan y modifican código de las extensiones GPL de Zorin; consulta [LICENSE](LICENSE) y [NOTICE](NOTICE). Se incluyen los parches y módulos añadidos, no una copia completa de las extensiones ni los wallpapers del equipo original. Proyecto independiente, sin afiliación con Zorin OS.
