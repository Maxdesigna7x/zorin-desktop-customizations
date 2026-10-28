#!/usr/bin/env python3
"""Prepare/apply/restore a wallpaper in Zorin's GDM theme; no desktop changes."""
import argparse,hashlib,json,os,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from customize import atomic_copy
REPO=Path(__file__).resolve().parents[1]
OUTPUT=REPO/'generated/wallpaper'
SYSTEM=Path('/usr/local/share/zorin-desktop-customizations')
CUSTOM=SYSTEM/'gdm-theme.gresource'
STATE=SYSTEM/'gdm-state.json'
ALTERNATIVE='gdm-theme.gresource'
def run(*args):return subprocess.check_output(args,text=True)
def alternative():
    header=run('update-alternatives','--query',ALTERNATIVE).split('\n\n')[0]
    return dict(line.split(': ',1) for line in header.splitlines() if ': ' in line)
def prepare(image):
    if os.geteuid()==0:raise RuntimeError('prepare se ejecuta sin sudo.')
    if not image.is_file():raise RuntimeError('No existe la imagen.')
    if not image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):raise RuntimeError('prepare espera una imagen PNG.')
    current=Path('/usr/share/gnome-shell/gdm-theme.gresource')
    paths=run('gresource','list',str(current)).splitlines()
    asset='/org/gnome/shell/theme/assets/login-background.png'
    if asset not in paths:raise RuntimeError('El tema no contiene el recurso de Zorin esperado. Requiere adaptación; no se modificó GDM.')
    css=subprocess.check_output(['gresource','extract',str(current),'/org/gnome/shell/theme/gdm.css'])
    if b'login-background.png' not in css:raise RuntimeError('CSS del tema no compatible.')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    stage=OUTPUT/'source';stage.mkdir(exist_ok=True)
    xml=ET.Element('gresources');group=ET.SubElement(xml,'gresource',prefix='/org/gnome/shell/theme')
    for resource in paths:
        prefix='/org/gnome/shell/theme/'
        if not resource.startswith(prefix):raise RuntimeError('Prefijo de recurso inesperado.')
        name=resource[len(prefix):]
        if '..' in Path(name).parts:raise RuntimeError('Nombre de recurso inválido.')
        p=stage/name;p.parent.mkdir(parents=True,exist_ok=True)
        content=image.read_bytes() if resource==asset else subprocess.check_output(['gresource','extract',str(current),resource])
        p.write_bytes(content);ET.SubElement(group,'file').text=name
    manifest=stage/'theme.xml';ET.ElementTree(xml).write(manifest)
    theme=OUTPUT/'theme.gresource'
    subprocess.run(['glib-compile-resources',str(manifest),'--sourcedir',str(stage),'--target',str(theme)],check=True)
    if run('gresource','list',str(theme)).splitlines()!=paths:raise RuntimeError('El recurso compilado no coincide.')
    for resource in paths:
        content=subprocess.check_output(['gresource','extract',str(theme),resource])
        expected=image.read_bytes() if resource==asset else subprocess.check_output(['gresource','extract',str(current),resource])
        if content!=expected:raise RuntimeError('Falló la verificación de recursos.')
    (OUTPUT/'plan.json').write_text(json.dumps({'sha256':hashlib.sha256(theme.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),'previous':alternative()},indent=2))
    print('Preparado y verificado:',theme,'\nAplicar: sudo python3 scripts/wallpaper.py apply')
def apply():
    if os.geteuid()!=0:raise RuntimeError('apply requiere sudo.')
    plan=json.loads((OUTPUT/'plan.json').read_text());theme=OUTPUT/'theme.gresource'
    if hashlib.sha256(theme.read_bytes()).hexdigest()!=plan['sha256']:raise RuntimeError('El archivo preparado cambió.')
    if alternative()['Value']!=plan['previous']['Value']:raise RuntimeError('El tema activo cambió desde prepare.')
    if hashlib.sha256(Path('/usr/share/gnome-shell/gdm-theme.gresource').read_bytes()).hexdigest()!=plan['source_sha256']:raise RuntimeError('El contenido del tema activo cambió desde prepare.')
    SYSTEM.mkdir(parents=True,exist_ok=True)
    if not STATE.exists():
        if plan['previous']['Value']==str(CUSTOM):raise RuntimeError('Falta el estado original para restaurar.')
        STATE.write_text(json.dumps(plan['previous'],indent=2))
    atomic_copy(theme,CUSTOM)
    subprocess.run(['update-alternatives','--install','/usr/share/gnome-shell/gdm-theme.gresource',ALTERNATIVE,str(CUSTOM),'30'],check=True)
    subprocess.run(['update-alternatives','--set',ALTERNATIVE,str(CUSTOM)],check=True)
    print('Fondo instalado. Se verá al cerrar sesión o reiniciar. No se reinició GDM.')
def restore():
    if os.geteuid()!=0:raise RuntimeError('restore requiere sudo.')
    state=json.loads(STATE.read_text())
    subprocess.run(['update-alternatives','--set',ALTERNATIVE,state['Value']],check=True)
    subprocess.run(['update-alternatives','--remove',ALTERNATIVE,str(CUSTOM)],check=True)
    if state['Status']=='auto':subprocess.run(['update-alternatives','--auto',ALTERNATIVE],check=True)
    STATE.rename(STATE.with_name('gdm-state-restored.json'))
    print('Tema previo restaurado; visible en el próximo inicio de sesión.')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','apply','restore']);p.add_argument('--image',type=Path);args=p.parse_args()
    try:
        if args.action=='prepare':
            if args.image is None:p.error('prepare requiere --image (PNG).')
            prepare(args.image)
        else:{'apply':apply,'restore':restore}[args.action]()
    except (RuntimeError,OSError,subprocess.CalledProcessError) as e:p.exit(1,'Error: '+str(e)+'\n')
