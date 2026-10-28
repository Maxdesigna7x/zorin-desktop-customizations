import hashlib,importlib.util,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('customize',REPO/'scripts/customize.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class InstallerTests(unittest.TestCase):
    def test_rejects_unknown_source_without_touching_it(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);source=root/module.EXTENSIONS/module.COMPAT['menu']['uuid']/'sections.js'
            source.parent.mkdir(parents=True);source.write_text('unsupported source')
            with self.assertRaises(RuntimeError):module.prepare_component('menu',root,root/'output')
            self.assertEqual(source.read_text(),'unsupported source')
    def test_restore_roundtrip_and_new_file_removal(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);old=root/'old';target=root/'target';backup=root/'backup';new=root/'new'
            old.write_text('original');module.atomic_copy(old,backup);target.write_text('modified');new.write_text('new helper')
            records=[{'target':str(target),'backup':str(backup),'before':module.digest(old),'after':module.digest(target)},
                     {'target':str(new),'backup':str(root/'absent'),'before':None,'after':module.digest(new)}]
            module.restore_records(records)
            self.assertEqual(target.read_text(),'original');self.assertFalse(new.exists())
    def test_restore_refuses_new_package_content(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);backup=root/'backup';target=root/'target'
            backup.write_text('original');target.write_text('package update')
            record={'target':str(target),'backup':str(backup),'before':module.digest(backup),'after':hashlib.sha256(b'modified').hexdigest()}
            with self.assertRaises(RuntimeError):module.restore_records([record])
            self.assertEqual(target.read_text(),'package update')
    def test_manifest_hashes_are_sha256(self):
        for component in module.COMPAT.values():
            for hashes in component['files'].values():
                for value in hashes.values():self.assertRegex(value,r'^[a-f0-9]{64}$')
    def test_no_personal_generated_files_tracked_by_manifest(self):
        for component in module.COMPAT.values():
            self.assertNotIn('/home/',json.dumps(component))
            for path in component['added']:self.assertTrue((REPO/'components'/('menu' if component['uuid'].startswith('zorin-menu') else 'taskbar')/path).is_file())
    @unittest.skipUnless(Path('/usr/share/gnome-shell/extensions/zorin-menu@zorinos.com').exists() and shutil.which('patch'),'Integration requires installed compatible Zorin extensions')
    def test_real_patch_roundtrip_from_original_and_already_patched(self):
        for name,component in module.COMPAT.items():
            with self.subTest(component=name),tempfile.TemporaryDirectory() as root:
                root=Path(root);source=root/module.EXTENSIONS/component['uuid'];source.mkdir(parents=True)
                for path,hashes in component['files'].items():
                    installed=Path('/')/module.EXTENSIONS/component['uuid']/path
                    self.assertIn(module.digest(installed),hashes.values(),'Installed fixture must match a known version')
                    target=source/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(installed,target)
                if all(module.digest(source/path)==hashes['after'] for path,hashes in component['files'].items()):
                    subprocess.run(['patch','--reverse','--batch','--fuzz=0','-p1','-i',str(REPO/'patches'/f'{name}.patch')],cwd=source,check=True,capture_output=True)
                for path,hashes in component['files'].items():self.assertEqual(module.digest(source/path),hashes['before'])
                records=module.prepare_component(name,root,root/'prepared-original')
                self.assertTrue(records)
                for path,hashes in component['files'].items():self.assertEqual(module.digest(root/'prepared-original'/path),hashes['after'])
                # Simulate a fully patched installation, then prepare again without applying the patch twice.
                for path in component['files']:shutil.copyfile(root/'prepared-original'/path,source/path)
                module.prepare_component(name,root,root/'prepared-again')
                for path in component['files']:self.assertEqual(module.digest(root/'prepared-original'/path),module.digest(root/'prepared-again'/path))
if __name__=='__main__':unittest.main()
