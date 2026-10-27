"""Run inside Blender after opening a relocated demo .blend."""
import bpy,json
from pathlib import Path
root=Path(bpy.data.filepath).parent
plan=json.loads((root/'plan.json').read_text())
s=bpy.context.scene;editor=s.sequence_editor
strips=getattr(editor,'strips',None)
if strips is None:strips=editor.sequences
assert len(strips)==len(plan['layers'])
for strip in strips:
    assert strip.type=='IMAGE'
    assert strip.directory.startswith('//')
    path=Path(bpy.path.abspath(strip.directory))/strip.elements[0].filename
    assert path.is_file(),path.name
assert s.frame_start==1 and s.frame_end==round(plan['duration']*plan['fps'])
print('RELOCATED_PROJECT_OK',len(strips),s.frame_end,flush=True)
