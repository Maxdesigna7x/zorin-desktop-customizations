#!/usr/bin/env python3
"""Render a wallpaper with the actual GNOME Shell lock-screen blur effect."""
import argparse, json, os, shutil, subprocess, tempfile
from pathlib import Path
from session_utils import isolated_workspace

def render(image, output, width=1920, height=1080, radius=90, brightness=0.65):
    if not image.is_file(): raise RuntimeError('No existe la imagen: ' + str(image))
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists(): raise RuntimeError('El resultado ya existe; usa otro nombre: ' + str(output))
    with isolated_workspace('zorin-blur-') as directory:
        root = Path(directory)
        extension = root / 'data/gnome-shell/extensions/render-blur@local'
        extension.mkdir(parents=True)
        (root / 'config').mkdir()
        (root / 'runtime').mkdir(mode=0o700)
        (extension / 'metadata.json').write_text(json.dumps({'uuid':'render-blur@local','name':'Wallpaper renderer','description':'Isolated background rendering','shell-version':['46']}))
        shutil.copyfile(Path(__file__).with_name('blur-renderer.js'), extension / 'extension.js')
        env = os.environ.copy()
        env["GVFS_DISABLE_FUSE"] = "1"
        env.update(XDG_CONFIG_HOME=str(root/'config'), XDG_DATA_HOME=str(root/'data'), XDG_RUNTIME_DIR=str(root/'runtime'),
                   GNOME_SHELL_SESSION_MODE='user', XDG_CURRENT_DESKTOP='GNOME',
                   BLUR_OUTPUT=str(output), BLUR_REPORT=str(root/'report'), BLUR_IMAGE=image.resolve().as_uri(),
                   BLUR_WIDTH=str(width), BLUR_HEIGHT=str(height), BLUR_RADIUS=str(radius), BLUR_BRIGHTNESS=str(brightness))
        # Environment must be isolated BEFORE starting the D-Bus daemon, not just its child shell.
        code = '''
import os,subprocess,time
from pathlib import Path
for schema,key,value in [
('org.gnome.shell','enabled-extensions',"['render-blur@local']"),
('org.gnome.shell','disable-user-extensions','false'),
('org.gnome.desktop.background','picture-uri',os.environ['BLUR_IMAGE']),
('org.gnome.desktop.background','picture-uri-dark',os.environ['BLUR_IMAGE']),
('org.gnome.desktop.background','picture-options','zoom'),
('org.gnome.desktop.interface','scaling-factor','1')]:
 subprocess.run(['gsettings','set',schema,key,value],check=True)
p=subprocess.Popen(['gnome-shell','--headless','--wayland','--no-x11','--virtual-monitor',os.environ['BLUR_WIDTH']+'x'+os.environ['BLUR_HEIGHT']])
try:
 for attempt in range(45):
  report=Path(os.environ['BLUR_REPORT'])
  if report.exists():
   text=report.read_text()
   if text!='PASS':raise RuntimeError(text)
   break
  if p.poll() is not None:raise RuntimeError('GNOME Shell terminó antes de renderizar')
  time.sleep(1)
 else:raise RuntimeError('Tiempo de renderizado agotado')
finally:
 p.terminate()
 try:p.wait(timeout=8)
 except subprocess.TimeoutExpired:p.kill();p.wait()
'''
        log = output.with_suffix('.render.log')
        with log.open('w') as stream:
            subprocess.run(['dbus-run-session','--','/usr/bin/python3','-c',code],env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
    print('Fondo renderizado con GNOME:', output)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--width',type=int,default=1920)
    parser.add_argument('--height',type=int,default=1080)
    parser.add_argument('--radius',type=float,default=90)
    parser.add_argument('--brightness',type=float,default=0.65)
    args=parser.parse_args()
    if os.geteuid()==0:parser.error('Renderiza como usuario normal, sin sudo.')
    if args.width<320 or args.height<240 or not 0<=args.brightness<=1 or args.radius<0:parser.error('Parámetros no válidos.')
    render(args.image,args.output,args.width,args.height,args.radius,args.brightness)
