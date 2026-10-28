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
