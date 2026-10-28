import os
from pathlib import Path
import shutil
import subprocess
import unittest

class KineticTests(unittest.TestCase):
    def test_absolute_time_and_geometry_invariants(self):
        node=os.environ.get('NODE_BINARY') or shutil.which('node')
        if not node:self.skipTest('Node is required for optional Canvas motion checks')
        result=subprocess.run([node,str(Path(__file__).with_name('kinetic_geometry.cjs'))],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_cli_help_and_unknown_flags(self):
        node=os.environ.get('NODE_BINARY') or shutil.which('node')
        if not node:self.skipTest('Node unavailable')
        script=Path(__file__).resolve().parents[1]/'skills/animated-logos/scripts/kinetic_demo.cjs'
        help_result=subprocess.run([node,str(script),'--help'],text=True,capture_output=True)
        self.assertEqual(help_result.returncode,0)
        self.assertIn('init',help_result.stdout)
        invalid=subprocess.run([node,str(script),'init','--project','unused','--unknown','value'],text=True,capture_output=True)
        self.assertNotEqual(invalid.returncode,0)
        self.assertIn('Unknown option',invalid.stderr)

    def test_invalid_plan_and_missing_font_leave_no_project(self):
        import json,tempfile
        node=os.environ.get('NODE_BINARY') or shutil.which('node')
        if not node:self.skipTest('Node unavailable')
        script=Path(__file__).resolve().parents[1]/'skills/animated-logos/scripts/kinetic_demo.cjs'
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);plan=root/'bad.json';plan.write_text(json.dumps({'duration':30}));project=root/'project'
            base=[node,str(script),'init','--project',str(project),'--font',str(root/'missing.woff2'),'--font-license',str(root/'missing-license.txt')]
            invalid=subprocess.run([*base,'--plan',str(plan)],text=True,capture_output=True)
            self.assertNotEqual(invalid.returncode,0)
            self.assertIn('six 3-second scenes',invalid.stderr)
            self.assertFalse(project.exists())
            missing=subprocess.run(base,text=True,capture_output=True)
            self.assertNotEqual(missing.returncode,0)
            self.assertFalse(project.exists())

    def test_preflight_reports_missing_tools_as_json(self):
        import json,sys,tempfile
        script=Path(__file__).resolve().parents[1]/'skills/animated-logos/scripts/preflight.py'
        with tempfile.TemporaryDirectory() as temp:
            result=subprocess.run([sys.executable,str(script),'--pipeline','canvas','--node',str(Path(temp)/'missing-node')],text=True,capture_output=True,timeout=30)
            self.assertEqual(result.returncode,2)
            report=json.loads(result.stdout)
            self.assertFalse(report['ready'])
            self.assertIn('node',report['missing'])
