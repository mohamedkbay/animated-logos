"""Build the editable dimensional assembly. Run inside Blender."""
import bpy,math,json,sys,argparse
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--stills',action='store_true');p.add_argument('--render',action='store_true');p.add_argument('--scale',type=int,default=100);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);R=Path(a.project).resolve();plan=json.loads((R/'plan.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
for name in ['BLENDER_EEVEE_NEXT','BLENDER_EEVEE']:
 try:s.render.engine=name;break
 except TypeError:pass
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=a.scale;s.render.fps=30;s.frame_start=1;s.frame_end=300;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.compression=20;s.view_settings.view_transform='Standard';s.view_settings.exposure=-.3
if hasattr(s,'eevee'):
 for key in ['taa_render_samples','taa_samples']:
  if hasattr(s.eevee,key):setattr(s.eevee,key,48)
world=bpy.data.worlds.new('White studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.82,.89,1,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5;s.world=world
mat=bpy.data.materials.new('Tag Tech — polished blue');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');rgb=[v/255 for v in plan['brandColor']];lin=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
for key,value in [('Base Color',(*lin,1)),('Metallic',.30),('Roughness',.16),('IOR',1.46),('Transmission Weight',.20),('Coat Weight',.7),('Coat Roughness',.1)]:
 if key in bs.inputs:bs.inputs[key].default_value=value
bpy.ops.object.empty_add(type='PLAIN_AXES');stage=bpy.context.object;stage.name='Assembly rig'
def curve(name,points,pivot):
 data=bpy.data.curves.new(name,'CURVE');data.dimensions='2D';data.fill_mode='BOTH';data.resolution_u=24;data.extrude=.085;data.bevel_depth=.019;data.bevel_resolution=4;poly=data.splines.new('POLY');poly.points.add(len(points)-1)
 for v,(x,y) in zip(poly.points,points):v.co=((x-pivot[0])/88.5,(pivot[1]-y)/88.5,0,1)
 poly.use_cyclic_u=True;o=bpy.data.objects.new(name,data);s.collection.objects.link(o);o.data.materials.append(mat);o.parent=stage;return o,((pivot[0]-88.5)/88.5,(88.5-pivot[1])/88.5,0)
def disk(cx,cy,r):return[(cx+r*math.cos(i*2*math.pi/128),cy+r*math.sin(i*2*math.pi/128))for i in range(128)]
nw=[(85+85*math.cos(math.pi+i*math.pi/192),85+85*math.sin(math.pi+i*math.pi/192))for i in range(97)]+[(85,46),(46,46),(46,85)]
se=[(93+85*math.cos(i*math.pi/192),93+85*math.sin(i*math.pi/192))for i in range(97)]+[(93,131),(131,131),(131,93)]
parts=[curve('Disc NE',disk(124,53,40.7),(124,53)),curve('Disc SW',disk(53,124,40.7),(53,124)),curve('Arc NW',nw,(50,50)),curve('Arc SE',se,(128,128))]
def clamp(u):return max(0,min(1,u))
def smooth(u):u=clamp(u);return u*u*u*(u*(u*6-15)+10)
for frame in range(1,301):
 t=(frame-1)/30;u=smooth((t-.8)/3.3);stage.rotation_euler=(math.radians(19)*(1-u),math.radians(-32)*(1-u),math.radians(-10)*(1-u));stage.keyframe_insert('rotation_euler',frame=frame);zoom=.88+.24*smooth(t/2.1)-.12*smooth((t-2.4)/1.7);stage.scale=(zoom,zoom,zoom);stage.keyframe_insert('scale',frame=frame)
 for i,(o,target)in enumerate(parts):
  begin=[.05,.4,.95,1.25][i];end=[1.55,1.95,2.9,3.3][i];q=smooth((t-begin)/(end-begin));theta=[2.8,-.4,-2,1.1][i]+(1-q)*math.pi*.95;radius=[2.0,2.05,2.15,2.15][i]*(1-q);o.location=(target[0]+radius*math.cos(theta),target[1]+radius*math.sin(theta),(.65 if i%2 else -.25)*(1-q));o.rotation_euler=(math.radians([55,-45,70,-65][i])*(1-q),math.radians([-55,65,35,-45][i])*(1-q),math.radians([110,-110,-150,150][i])*(1-q));sc=.6+.4*q;o.scale=(sc,sc,sc)
  o.keyframe_insert('location',frame=frame);o.keyframe_insert('rotation_euler',frame=frame);o.keyframe_insert('scale',frame=frame)
camdata=bpy.data.cameras.new('Orthographic ident camera');cam=bpy.data.objects.new('Orthographic ident camera',camdata);s.collection.objects.link(cam);cam.location=(0,0,9);camdata.type='ORTHO';camdata.ortho_scale=5.7;s.camera=cam;bpy.context.view_layer.update();hi=world_to_camera_view(s,cam,Vector((0,1,0))).y;lo=world_to_camera_view(s,cam,Vector((0,-1,0))).y;camdata.ortho_scale*=((hi-lo)*1080)/380
for name,loc,energy,size,scale in [('Key',(-3,4,5),650,4.5,(1,1,1)),('Rim',(4,1,4),450,3,(.25,1,1)),('Fill',(-1,-4,3),260,4,(1,.35,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='RECTANGLE';d.size=size;d.size_y=size*.45;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler();o.scale=scale
s['Identity designer']='Yasin Alsharif — supplied reference';s['Motion']='Original Tag Tech assembly for animated-logos-skill';s['Stage duration']='Dimensional phase is composited with original 2D artwork by render.cjs';s.frame_set(124);s.render.resolution_percentage=100;s.render.filepath='//cg-frames/frame-';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/'tag-tech-assembly.blend'),compress=True)
if a.stills:
 (R/'stills').mkdir(exist_ok=True)
 for f in [52,100,124]:s.frame_set(f);s.render.resolution_percentage=a.scale;s.render.filepath=str(R/'stills'/f'{f:04}.png');bpy.ops.render.render(write_still=True)
if a.render:
 (R/'cg-frames').mkdir(exist_ok=True);s.frame_end=141;s.render.resolution_percentage=a.scale;s.render.filepath=str(R/'cg-frames/frame-');bpy.ops.render.render(animation=True)
print('TAG_TECH_SCENE_OK',s.render.engine,camdata.ortho_scale,flush=True)
