"""Run with Blender --background --python THIS -- --project PROJECT [--render]."""
import argparse
import math
import sys
from pathlib import Path
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from motionlib import load_project, sample, local_file

parser=argparse.ArgumentParser()
parser.add_argument('--project',required=True)
parser.add_argument('--render',action='store_true')
parser.add_argument('--scale',type=int,default=100)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if not 1<=args.scale<=100:parser.error('--scale must be in 1..100')
root=Path(args.project).resolve();plan=load_project(root);timeline=sample(plan)
for layer in timeline['layers']:
    if not local_file(root,layer['png']).is_file():raise FileNotFoundError('Rasterize PNG assets first')
project=root/'logo-motion.blend'
if project.exists():raise FileExistsError('Use a new project version; logo-motion.blend exists')
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.sequence_editor_create();editor=scene.sequence_editor
scene.render.resolution_x=plan['width'];scene.render.resolution_y=plan['height']
scene.render.resolution_percentage=100;scene.render.fps=plan['fps']
scene.frame_start=1;scene.frame_end=round(plan['duration']*plan['fps'])
scene.render.use_sequencer=True;scene.view_settings.view_transform='Standard'
scene.sequencer_colorspace_settings.name='sRGB'
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA' if plan.get('transparent') else 'RGB'
scene.render.image_settings.compression=15
def key(obj,prop,value,frame):
    setattr(obj,prop,value);obj.keyframe_insert(data_path=prop,frame=frame)
strips=getattr(editor,'strips',None)
if strips is None:strips=editor.sequences
for channel,layer in enumerate(timeline['layers'],1):
    strip=strips.new_image(layer['name'],str(local_file(root,layer['png'])),channel,layer['start_frame'])
    strip.frame_final_duration=layer['end_frame']-layer['start_frame']
    strip.blend_type='ALPHA_OVER';strip.alpha_mode='STRAIGHT'
    strip.transform.origin=(layer['pivot'][0]/plan['width'],1-layer['pivot'][1]/plan['height'])
    for frame,alpha,dx,dy,sx,sy,rotation in layer['samples']:
        key(strip,'blend_alpha',alpha,frame)
        key(strip.transform,'offset_x',dx,frame);key(strip.transform,'offset_y',-dy,frame)
        key(strip.transform,'scale_x',sx,frame);key(strip.transform,'scale_y',sy,frame)
        key(strip.transform,'rotation',-math.radians(rotation),frame)
    for frame,right in layer.get('crop_samples',[]):key(strip.crop,'max_x',right,frame)
scene['Project']=plan['title'];scene['Motion profile']=plan['profile']
scene['Symbol family']=plan.get('family','assembly');scene['Wordmark family']=plan.get('wordmark','default')
scene['Sampling']='Integer frame timeline; positive image y maps to negative Blender offset_y'
scene['Assets']='Original demo or user-provided project layers; relative paths'
scene.frame_set(scene.frame_end)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(project))
for strip in strips:
    strip.directory='//'+str(Path(plan['layers'][strip.channel-1]['png']).parent).replace('\\','/')+'/'
bpy.ops.wm.save_as_mainfile(filepath=str(project))
if args.render:
    frames=root/'frames';frames.mkdir(exist_ok=True)
    if any(frames.glob('frame-*.png')):raise FileExistsError('Frame cache exists; use a new project version')
    scene.render.resolution_percentage=args.scale
    scene.render.filepath=str(frames/'frame-')
    bpy.ops.render.render(animation=True)
print('ANIMATED_LOGOS_OK',len(timeline['layers']),scene.frame_end,bpy.app.version_string,flush=True)
