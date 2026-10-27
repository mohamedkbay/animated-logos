from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from install import install,target_dir,GLOBAL,hashes

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.source=Path(__file__).resolve().parents[1]/'skills/animated-logos'
    def tearDown(self):self.temp.cleanup()

    def test_all_global_targets_receive_same_portable_skill(self):
        home=self.root/'user'
        locations=set()
        for agent in GLOBAL:
            dest=target_dir(agent,home=home);locations.add(dest)
            self.assertEqual(install(self.source,dest),'Installed')
            self.assertTrue((dest/'SKILL.md').is_file())
            self.assertTrue((dest/'LICENSE').is_file())
            self.assertEqual(hashes(self.source),hashes(dest))
        self.assertEqual(len(locations),5)

    def test_workspace_targets_share_documented_agents_directory(self):
        project=self.root/'project'
        paths={a:target_dir(a,project=project) for a in GLOBAL}
        self.assertEqual(paths['codex'],paths['antigravity'])
        self.assertEqual(paths['codex'],paths['antigravity-cli'])
        self.assertEqual(len(set(paths.values())),3)
        for dest in paths.values():install(self.source,dest)

    def test_update_is_idempotent_and_preserves_changed_installation(self):
        dest=target_dir('claude',home=self.root/'user')
        install(self.source,dest)
        self.assertEqual(install(self.source,dest),'Already current')
        (dest/'local-note.txt').write_text('retain this')
        with self.assertRaises(ValueError):install(self.source,dest)
        install(self.source,dest,update=True)
        backups=list((dest.parent.parent/'skill-backups').glob('animated-logos-*'))
        self.assertEqual(len(backups),1)
        self.assertEqual((backups[0]/'local-note.txt').read_text(),'retain this')
        self.assertEqual(hashes(dest),hashes(self.source))

    def test_refuses_to_replace_a_symlink(self):
        dest=self.root/'skill';elsewhere=self.root/'elsewhere';elsewhere.mkdir()
        try:dest.symlink_to(elsewhere,target_is_directory=True)
        except OSError:self.skipTest('Symlinks unavailable')
        with self.assertRaises(ValueError):install(self.source,dest,update=True)
        self.assertTrue(dest.is_symlink())

if __name__=='__main__':unittest.main()
