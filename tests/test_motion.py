import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS=Path(__file__).resolve().parents[1]/'skills/animated-logos/scripts'
sys.path.insert(0,str(SCRIPTS))
from motionlib import validate,pose,sample,frame_range,local_file,PROFILES,FAMILIES,WORDMARKS,right_crop
from animated_logos import demo
from argparse import Namespace

class MotionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)/'project'
        demo(Namespace(project=str(self.root),profile='clean',width=1920,height=1080,fps=30,transparent=False))
        self.plan=json.loads((self.root/'plan.json').read_text())

    def tearDown(self):self.temp.cleanup()

    def test_profiles_are_deterministic_finite_and_restore_master(self):
        for name in PROFILES:
            plan=copy.deepcopy(self.plan);plan['profile']=name
            self.assertEqual(sample(plan),sample(plan))
            final=round(plan['duration']*plan['fps'])
            for layer in plan['layers']:
                if layer['role'] in ('whole','letter'):
                    self.assertEqual(pose(plan,layer,final),(1.,0.,0.,1.,1.,0.))
                start,end=frame_range(plan,layer)
                for frame in range(start,end):
                    values=pose(plan,layer,frame)
                    self.assertTrue(all(math.isfinite(v) for v in values))
                    self.assertTrue(0<=values[0]<=1)
                    self.assertGreater(values[3],0);self.assertGreater(values[4],0)

    def test_handoff_has_no_gap_and_uses_shared_transform(self):
        for fps in (24,30,60):
            plan=copy.deepcopy(self.plan);plan['fps']=fps
            hand=round(plan['timing']['handoff']*fps)+1
            whole=next(l for l in plan['layers'] if l['role']=='whole')
            parts=[l for l in plan['layers'] if l['role']=='part']
            self.assertEqual(pose(plan,whole,hand-1)[0],0)
            self.assertEqual(pose(plan,whole,hand)[0],1)
            for part in parts:
                self.assertEqual(pose(plan,part,hand-1)[0],1)
                self.assertEqual(pose(plan,part,hand)[0],0)
                extended=copy.deepcopy(part);extended['end']=plan['duration']
                self.assertEqual(pose(plan,extended,hand)[1:],pose(plan,whole,hand)[1:])

    def test_letters_start_after_symbol_reaches_lockup(self):
        plan=self.plan
        for layer in plan['layers']:
            if layer['role']=='letter':
                self.assertGreaterEqual(layer['start'],plan['timing']['move_end'])
        bad=copy.deepcopy(plan)
        next(l for l in bad['layers'] if l['role']=='letter')['start']=1.0
        with self.assertRaises(ValueError):validate(bad)

    def test_invalid_timeline_and_duplicate_names_fail(self):
        for mutation in ('duration','duplicate','zero','handoff'):
            plan=copy.deepcopy(self.plan)
            if mutation=='duration':plan['duration']=float('nan')
            elif mutation=='duplicate':plan['layers'][1]['name']=plan['layers'][0]['name']
            elif mutation=='zero':plan['layers'][1]['end']=plan['layers'][1]['start']
            else:plan['layers'][1]['end']+=.2
            with self.assertRaises(ValueError):validate(plan)

    def test_assets_stay_inside_project_including_symlinks(self):
        with self.assertRaises(ValueError):local_file(self.root,'../escape')
        outside=Path(self.temp.name)/'outside';outside.mkdir()
        try:(self.root/'escape').symlink_to(outside,target_is_directory=True)
        except OSError:self.skipTest('Symlinks unavailable')
        with self.assertRaises(ValueError):local_file(self.root,'escape/logo.png')

    def test_fresh_project_does_not_overwrite_existing_plan(self):
        with self.assertRaises(ValueError):demo(Namespace(project=str(self.root)))

    def test_all_families_and_wordmark_mixes_restore_identity(self):
        for name in FAMILIES:
            for letters in WORDMARKS:
                plan=copy.deepcopy(self.plan);plan.update(family=name,wordmark=letters)
                validate(plan);final=round(plan['duration']*plan['fps'])
                for layer in plan['layers']:
                    start,end=frame_range(plan,layer)
                    for frame in range(start,end):
                        p=pose(plan,layer,frame)
                        self.assertTrue(all(math.isfinite(v) for v in p))
                        self.assertTrue(0<=p[0]<=1 and p[3]>0 and p[4]>0)
                    if layer['role'] in ('letter','whole'):
                        self.assertEqual(pose(plan,layer,final),(1.,0.,0.,1.,1.,0.))
                        self.assertEqual(right_crop(plan,layer,final),0)

    def test_wipe_progress_is_bounded_monotone_and_finishes_open(self):
        plan=copy.deepcopy(self.plan);plan.update(family='wipe',wordmark='wipe')
        for layer in plan['layers']:
            if layer['role'] not in ('part','letter'):continue
            start,end=frame_range(plan,layer)
            cuts=[right_crop(plan,layer,f) for f in range(start,end)]
            self.assertGreater(cuts[0],0)
            self.assertEqual(cuts[-1],0)
            self.assertEqual(cuts,sorted(cuts,reverse=True))
            self.assertTrue(all(0<=c<=plan['width'] for c in cuts))

    def test_jitter_is_repeatable_when_frames_are_requested_out_of_order(self):
        plan=copy.deepcopy(self.plan);plan.update(family='glitch',wordmark='glitch')
        layer=next(l for l in plan['layers'] if l['role']=='part')
        frames=list(range(6,24));expected={f:pose(plan,layer,f) for f in frames}
        self.assertEqual(expected,{f:pose(plan,layer,f) for f in reversed(frames)})
        other=copy.deepcopy(plan);other['family']='pop'
        self.assertNotEqual([expected[f] for f in frames],[pose(other,layer,f) for f in frames])

    def test_invalid_family_or_reveal_bounds_are_rejected(self):
        for change in ('family','wordmark','bounds'):
            plan=copy.deepcopy(self.plan)
            if change=='bounds':plan['layers'][1]['bounds_x']=[500,100]
            else:plan[change]='unknown'
            with self.assertRaises(ValueError):validate(plan)

if __name__=='__main__':unittest.main()
