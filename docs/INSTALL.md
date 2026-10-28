# Instalación detallada

## Requisitos

La receta comprobada usa Zorin OS 18.1, GNOME Shell 46 y las extensiones del sistema:

- `/usr/share/gnome-shell/extensions/zorin-menu@zorinos.com`
- `/usr/share/gnome-shell/extensions/zorin-taskbar@zorinos.com`
- GDM, con la alternativa `gdm-theme.gresource` y el recurso `assets/login-background.png` del tema de Zorin.

Herramientas: Python 3.9 o superior, `patch`, `glib-compile-schemas`, `gresource`, `glib-compile-resources`; para renderizar/capturar, `gnome-shell`, `gsettings`, `dbus-run-session` y un backend gráfico de GNOME funcional. La demostración con ventanas usa GJS y GTK 3.

En Zorin/Ubuntu las dependencias adicionales suelen estar en:

```bash
sudo apt update
sudo apt install git python3 patch libglib2.0-bin libglib2.0-dev-bin dbus-daemon gjs gir1.2-gtk-3.0
```

La sesión de GNOME, GDM y las extensiones de Zorin deben existir de antemano. Esta receta no instala ni cambia el entorno de escritorio.

## 1. Diagnosticar

```bash
python3 scripts/customize.py doctor
```

Cada archivo debe aparecer como `original compatible` o `personalizado compatible`. Un componente que mezcle estados o incluya un archivo desconocido requiere revisión. `prepare --components menu` no exige compatibilidad de la barra y viceversa.

## 2. Preparar sin privilegios

```bash
python3 scripts/customize.py prepare --components menu taskbar
```

Se comprueban hashes, se aplican parches sin tolerancia a cambios de contexto, se verifican los hashes finales y se compila el esquema de preferencias del menú. El bundle y el plan quedan en `generated/`, excluido de Git.

No uses `sudo` aquí: la preparación y el renderizado corresponden al usuario de la sesión gráfica.

## 3. Instalar con privilegios

```bash
sudo python3 scripts/customize.py install
```

El instalador vuelve a validar el origen y el bundle, guarda los archivos previos y un plan en `/var/backups/zorin-desktop-customizations/FECHA-PID/`, y reemplaza cada archivo de forma atómica. Ante un error durante la copia intenta restaurar el estado previo. No aplica ajustes de GNOME al usuario root ni altera la lista de favoritos de la barra.

Los respaldos se conservan. `restore` apunta al respaldo de la última instalación de este repositorio; instalar un nuevo componente después crea un respaldo nuevo que solo incluye ese componente. Para recuperar una instalación anterior, inspecciona los planes conservados y sigue la guía de restauración manual.

## 4. Activar

Guarda el trabajo, cierra sesión y vuelve a entrar. Desactivar/activar una extensión puede reutilizar módulos JavaScript ya importados; volver a entrar garantiza que cargue el código actualizado.

## 5. Administrar las dos listas

- Menú de inicio: clic derecho en una aplicación → **Agregar/Quitar de favoritos del inicio**.
- Barra: anclar o desanclar desde el menú propio de sus iconos o de la vista de aplicaciones de GNOME.
- Editar una lista no cambia la otra.

## 6. Preparar GDM por separado

Consulta el comando de fondo en el README. Para elegir la imagen que usa el escritorio:

```bash
gsettings get org.gnome.desktop.background picture-uri
gsettings get org.gnome.desktop.background picture-uri-dark
```

El resultado es una URI. En los comandos usa la ruta del archivo correspondiente, sin las comillas de GSettings ni el prefijo `file://`; decodifica los espacios de la URI si los contiene. Se espera una imagen de entrada compatible con GNOME; `wallpaper.py prepare` espera un **PNG** para sustituir un recurso `.png`.

El renderizado usa el tamaño elegido y escala `zoom`; radio 90 corresponde a escala 1. Si la pantalla de inicio usa escala 2, revisa y compara el radio (el bloqueo multiplica el radio por el factor de escala). El ajuste visual exacto depende de la resolución y del escalado.

`wallpaper.py apply` instala su propio recurso en `/usr/local/share/zorin-desktop-customizations/` y lo registra con `update-alternatives`, sin sobrescribir el recurso empaquetado de Zorin. El estado original se conserva en `gdm-state.json` para restaurarlo.
