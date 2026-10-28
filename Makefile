.PHONY: check doctor prepare
check:
	python3 -m unittest discover -s tests -v
	python3 -m compileall -q scripts tests
	bash -n scripts/setup.sh
	@for file in components/menu/menuFavorites.js components/taskbar/compactFavorites.js scripts/blur-renderer.js scripts/demo-extension.js scripts/demo-window.js; do node --check "$$file"; done
	glib-compile-schemas --strict --dry-run components/menu/schemas
doctor:
	python3 scripts/customize.py doctor
prepare:
	python3 scripts/customize.py prepare --components menu taskbar
