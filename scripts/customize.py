#!/usr/bin/env python3
"""Checked, reversible installation of the Zorin Menu/Taskbar customizations."""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, tempfile
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
COMPAT = json.loads((REPO / 'compatibility.json').read_text())
EXTENSIONS = Path('usr/share/gnome-shell/extensions')
BACKUPS = Path('/var/backups/zorin-desktop-customizations')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
def atomic_copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(source.read_bytes())
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)
    finally:
        Path(tmp).unlink(missing_ok=True)
def prepare_component(name, system_root, output):
    info = COMPAT[name]
    source = system_root / EXTENSIONS / info['uuid']
    states = []
    for filename, hashes in info['files'].items():
        actual = digest(source / filename)
        state = 'before' if actual == hashes['before'] else 'after' if actual == hashes['after'] else 'unknown'
        states.append(state)
        if state == 'unknown':
            raise RuntimeError(f'{name}: versión no compatible: {source / filename}. No se modificó el sistema.')
    output.mkdir(parents=True)
    for filename in info['files']:
        target = output / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / filename, target)
    pending = {filename for filename, state in zip(info['files'], states) if state == 'before'}
    if pending:
        sections = re.split(r'(?=^--- a/)', (REPO / 'patches' / (name + '.patch')).read_text(), flags=re.MULTILINE)
        selected = ''.join(section for section in sections if section.startswith('--- a/') and section.splitlines()[0][6:] in pending)
        if not selected:
            raise RuntimeError('No hay parche para los archivos pendientes.')
        subprocess.run(['patch', '--batch', '--fuzz=0', '-p1'], input=selected, text=True, cwd=output, check=True, capture_output=True)
    for filename, hashes in info['files'].items():
        if digest(output / filename) != hashes['after']:
            raise RuntimeError('El parche no produjo el resultado esperado: ' + filename)
    for filename in info['added']:
        target = output / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / 'components' / name / filename, target)
    if name == 'menu':
        subprocess.run(['glib-compile-schemas', '--strict', str(output / 'schemas')], check=True)
    records = []
    for staged in sorted(output.rglob('*')):
        if staged.is_file():
            filename = staged.relative_to(output)
            records.append({'target': str(source / filename), 'staged': str(staged),
                            'before': digest(source / filename), 'after': digest(staged)})
    return records

def prepare(names):
    if os.geteuid() == 0:
        raise RuntimeError('Ejecuta prepare como tu usuario, sin sudo.')
    generated = REPO / 'generated'
    generated.mkdir(exist_ok=True)
    bundle = Path(tempfile.mkdtemp(prefix='bundle-', dir=generated))
    records = []
    for name in names:
        records.extend(prepare_component(name, Path('/'), bundle / name))
    (bundle / 'plan.json').write_text(json.dumps(records, indent=2))
    (generated / 'latest-bundle').write_text(bundle.name)
    print('Preparado y verificado:', bundle)
    print('Aplicar: sudo python3 scripts/customize.py install')

def install():
    if os.geteuid() != 0:
        raise RuntimeError('install requiere sudo.')
    name = (REPO / 'generated/latest-bundle').read_text().strip()
    bundle = (REPO / 'generated' / name).resolve()
    if bundle.parent != (REPO / 'generated').resolve():
        raise RuntimeError('Bundle no válido.')
    records = json.loads((bundle / 'plan.json').read_text())
    for record in records:
        if digest(Path(record['target'])) != record['before'] or digest(Path(record['staged'])) != record['after']:
            raise RuntimeError('Los archivos cambiaron desde prepare. Vuelve a preparar: ' + record['target'])
        if not Path(record['target']).is_relative_to(Path('/usr/share/gnome-shell/extensions')):
            raise RuntimeError('Destino no permitido.')
    backup = BACKUPS / (datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + str(os.getpid()))
    backup.mkdir(parents=True)
    for index, record in enumerate(records):
        record['backup'] = str(backup / str(index))
        if record['before'] is not None:
            shutil.copy2(record['target'], record['backup'])
    (backup / 'plan.json').write_text(json.dumps(records, indent=2))
    try:
        for record in records:
            atomic_copy(Path(record['staged']), Path(record['target']))
    except Exception:
        restore_records(records, check_current=False)
        raise
    (BACKUPS / 'latest').write_text(backup.name)
    print('Instalado. Cierra sesión y vuelve a entrar. Respaldo:', backup)

def restore_records(records, check_current=True):
    for record in records:
        if record['before'] is not None and digest(Path(record['backup'])) != record['before']:
            raise RuntimeError('Respaldo inválido: ' + record['backup'])
        if check_current and digest(Path(record['target'])) != record['after']:
            raise RuntimeError('El sistema cambió tras instalar; no se sobrescribirá: ' + record['target'])
    for record in records:
        target = Path(record['target'])
        if record['before'] is None:
            target.unlink(missing_ok=True)
        else:
            atomic_copy(Path(record['backup']), target)

def restore():
    if os.geteuid() != 0:
        raise RuntimeError('restore requiere sudo.')
    backup = BACKUPS / (BACKUPS / 'latest').read_text().strip()
    restore_records(json.loads((backup / 'plan.json').read_text()))
    print('Restaurado al estado previo a la última instalación. Cierra sesión y vuelve a entrar.')

def doctor():
    print(subprocess.check_output(['gnome-shell', '--version'], text=True).strip())
    for name, info in COMPAT.items():
        source = Path('/') / EXTENSIONS / info['uuid']
        for filename, hashes in info['files'].items():
            actual = digest(source / filename)
            state = 'original compatible' if actual == hashes['before'] else 'personalizado compatible' if actual == hashes['after'] else 'NO COMPATIBLE / ausente'
            print(f'{name}/{filename}: {state}')
    print('Herramientas:', ', '.join(f'{cmd}={shutil.which(cmd) or "FALTA"}' for cmd in ['patch','glib-compile-schemas','gresource','glib-compile-resources','dbus-run-session']))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['doctor','prepare','install','restore'])
    parser.add_argument('--components', nargs='+', choices=list(COMPAT), default=list(COMPAT))
    args = parser.parse_args()
    try:
        if args.action == 'prepare': prepare(args.components)
        else: {'doctor':doctor, 'install':install, 'restore':restore}[args.action]()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, 'Error: ' + str(error) + '\n')
if __name__ == '__main__': main()
