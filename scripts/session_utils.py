"""Temporary graphical session storage, with explicit FUSE mount cleanup."""
import contextlib,os,shutil,subprocess,tempfile
from pathlib import Path
@contextlib.contextmanager
def isolated_workspace(prefix):
    root=Path(tempfile.mkdtemp(prefix=prefix))
    try:
        yield root
    finally:
        for name in ['gvfs','doc']:
            mount=root/'runtime'/name
            if os.path.ismount(mount) and shutil.which('fusermount3'):
                subprocess.run(['fusermount3','-u',str(mount)],capture_output=True,timeout=8)
        if any(os.path.ismount(root/'runtime'/name) for name in ['gvfs','doc']):
            print('La sesión terminó; queda un montaje temporal para desmontar:',root)
        else:
            shutil.rmtree(root,ignore_errors=True)
