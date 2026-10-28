# Arquitectura

## Menú: almacenamiento independiente

El parche de `sections.js` construye tres elementos antes de la cuadrícula alfabética: título Favoritos, cuadrícula propia y título Todas las aplicaciones. La búsqueda conserva su comportamiento original.

`menuFavorites.js` usa este esquema local de la extensión:

- ID: `org.gnome.shell.extensions.zorin-menu.favorites`
- Ruta dconf: `/org/gnome/shell/extensions/zorin-menu/favorites/`
- `apps`: lista de IDs `.desktop` del inicio.
- `initialized`: marca que impide volver a importar favoritos, incluso si la lista queda vacía.

La primera carga copia una sola vez `org.gnome.shell favorite-apps`. El menú usa después exclusivamente su lista. `widgets/secondaryMenu.js` oculta la acción heredada que modifica el dash y añade la acción del inicio. Los cambios refrescan la sección mediante un callback idle; los callbacks se cancelan al destruirla.

Los favoritos de la barra continúan en `org.gnome.shell favorite-apps`. No se cambió ese formato ni se distribuyen valores personales.

## Barra: estados y detección

`compactFavorites.js` se conecta a puntos concretos de `taskbar.js`:

1. `filterInfos`: oculta lanzadores sin ventanas mientras no se esté mostrando la lista completa.
2. Un temporizador cada **100 ms** comprueba el puntero. La superficie vacía de la barra activa la revelación; botones, iconos de aplicaciones y grupos de controles se excluyen.
3. `allocationMap` permite descartar grupos enteros: inicio, mostrar aplicaciones, reloj, indicadores y mostrar escritorio, incluidos sus espacios internos. El grupo `taskbar` no se excluye en bloque.
4. Una vez revelados, los favoritos permanecen mientras se use la barra. Tras salir se esperan **400 ms** antes de ocultarlos. Menús de aplicación, previews y arrastre posponen el ocultamiento.
5. Con ventanas abiertas, los iconos de esas ventanas permanecen tras ocultar favoritos. Minimizar no equivale a cerrar.

No hay botón `+`, panel flotante ni sincronización de favoritos con el menú de inicio.

### Animación y tamaño final

Entrada: duración **180 ms**, desplazamiento vertical **8 px**, opacidad de 0 a 255 y retraso de **28 ms** entre iconos, limitado a diez pasos. No se usa una reducción de escala para la entrada.

Tras la redistribución, un asentamiento a **700 ms** restablece `childScale = 1`, `childOpacity = 255`, escala y opacidad del actor, desplazamiento cero y textura al tamaño final de la barra. Esto corrige la interacción con las animaciones originales de Dash y el ajuste del tamaño de iconos.

Los temporizadores se eliminan al destruir la barra. Los parámetros están en `components/taskbar/compactFavorites.js`. Cambiarlos requiere volver a preparar, instalar y entrar a la sesión.

## Wallpaper y bloqueo

La pantalla de bloqueo pertenece a la sesión del usuario. El inicio de sesión de GDM es otra sesión: cambiar uno no configura automáticamente el otro.

`render_blur.py` abre un GNOME Shell **headless, temporal y separado**, aplica `Shell.BlurEffect` al fondo y guarda un PNG. Los valores de referencia se leyeron del `unlockDialog.js` de GNOME Shell 46 instalado: brillo 0,65 y radio 90 por factor de escala.

El entorno XDG y la dirección de D-Bus se aíslan **antes de lanzar el daemon**. Aislar solo el proceso hijo no basta para garantizar que los servicios activados por D-Bus escriban en el perfil de prueba.

`wallpaper.py` extrae todos los recursos del tema activo, reemplaza únicamente la imagen del fondo, recompila y compara cada recurso. Solo acepta la estructura comprobada de Zorin. `apply` registra una alternativa propia; `restore` vuelve a la alternativa anterior.

El PNG no ejecuta desenfoque en vivo. Es una captura del fondo ya renderizado; cambiar la resolución o el wallpaper requiere regenerarlo.

## Posición centrada del inicio

Desde v1.1.0, `menu.js` ajusta el origen de la asignación de BoxPointer en cada redistribución, después del cálculo original de GNOME. El centro se calcula con el monitor que contiene el botón de inicio, solo en el eje horizontal; se conserva el anclaje vertical nativo a la barra; se limita al área de trabajo cuando el tamaño del menú no permite un centrado completo. No se usa la posición horizontal del botón para ubicar el menú. Cambiar la búsqueda, el contenido o los iconos de la barra provoca un cálculo nuevo.
