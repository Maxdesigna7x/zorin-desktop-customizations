#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
if [ "$EUID" -eq 0 ]; then echo 'Ejecuta setup.sh como usuario normal, sin sudo.'; exit 1; fi
if [ "$#" -eq 0 ]; then set -- menu taskbar; fi
python3 scripts/customize.py doctor
python3 scripts/customize.py prepare --components "$@"
sudo python3 scripts/customize.py install
