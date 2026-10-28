#!/usr/bin/env python3
"""Capture installed customizations in an isolated GNOME test session."""
import json,os,shutil,subprocess,tempfile
from pathlib import Path
from session_utils import isolated_workspace
REPO=Path(__file__).resolve().parents[1]
def main():
    if os.geteuid()==0:raise SystemExit('Ejecuta sin sudo.')
    output=REPO/'docs/images';output.mkdir(exist_ok=True)
    with isolated_workspace('zorin-demo-') as directory:
        root=Path(directory);ext=root/'data/gnome-shell/extensions/desktop-demo@local';ext.mkdir(parents=True)
        (root/'config').mkdir();(root/'runtime').mkdir(mode=0o700)
        (root/'config/user-dirs.dirs').write_text('XDG_DESKTOP_DIR="'+str(root)+'"\n')
        (ext/'metadata.json').write_text(json.dumps({'uuid':'desktop-demo@local','name':'Documentation demo','description':'Isolated screenshots','shell-version':['46']}))
        shutil.copyfile(REPO/'scripts/demo-extension.js',ext/'extension.js')
        apps=root/'data/applications';apps.mkdir()
        (apps/'org.codex.DesktopDemo.desktop').write_text('[Desktop Entry]\nType=Application\nName=Ventana de prueba\nExec=/usr/bin/gjs '+str(REPO/'scripts/demo-window.js')+'\nIcon=utilities-terminal\nStartupWMClass=org.codex.DesktopDemo\n')
        env=os.environ.copy();env["GVFS_DISABLE_FUSE"]="1";env.update(XDG_CONFIG_HOME=str(root/'config'),XDG_DATA_HOME=str(root/'data'),XDG_RUNTIME_DIR=str(root/'runtime'),GNOME_SHELL_SESSION_MODE='user',XDG_CURRENT_DESKTOP='GNOME',LANG='es_MX.UTF-8',GTK_A11Y='none',NO_AT_BRIDGE='1',GDK_BACKEND='wayland',GIO_USE_VFS='local',GTK_USE_PORTAL='0',DEMO_OUTPUT=str(output),DEMO_REPORT=str(root/'report'),DEMO_WINDOW=str(REPO/'scripts/demo-window.js'))
        code='''
import os,subprocess,time
from pathlib import Path
settings=[('org.gnome.shell','enabled-extensions',"['zorin-taskbar@zorinos.com','zorin-menu@zorinos.com','desktop-demo@local']"),('org.gnome.shell','disable-user-extensions','false'),('org.gnome.shell','favorite-apps',"['org.gnome.Nautilus.desktop','org.gnome.Terminal.desktop','org.gnome.Calculator.desktop','org.gnome.Software.desktop']"),('org.gnome.shell.extensions.zorin-menu','layout','APP_GRID'),('org.gnome.desktop.background','picture-uri',"''"),('org.gnome.desktop.background','picture-uri-dark',"''"),('org.gnome.desktop.background','primary-color','#202635'),('org.gnome.desktop.background','color-shading-type','solid')]
for schema,key,value in settings:subprocess.run(['gsettings','set',schema,key,value],check=True)
p=subprocess.Popen(['gnome-shell','--headless','--wayland','--no-x11','--virtual-monitor','1600x900'])
try:
 for i in range(50):
  report=Path(os.environ['DEMO_REPORT'])
  if report.exists():
   message=report.read_text();print(message,flush=True)
   if not message.startswith('PASS'):raise RuntimeError(message)
   break
  if p.poll() is not None:raise RuntimeError('La sesión terminó prematuramente')
  time.sleep(1)
 else:raise RuntimeError('Tiempo de captura agotado')
finally:
 p.terminate()
 try:p.wait(timeout=8)
 except subprocess.TimeoutExpired:p.kill();p.wait()
'''
        with (REPO/'generated/demo-capture.log').open('w') as log:
            subprocess.run(['dbus-run-session','--','/usr/bin/python3','-c',code],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    print('Capturas:',output)
if __name__=='__main__':
    (REPO/'generated').mkdir(exist_ok=True)
    main()
