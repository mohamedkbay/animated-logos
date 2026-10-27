#!/usr/bin/env python3
"""Copy the portable skill into documented agent discovery directories."""
import argparse,shutil,datetime,tempfile,hashlib
from pathlib import Path

GLOBAL={
    'codex':'.agents/skills',
    'claude':'.claude/skills',
    'antigravity':'.gemini/config/skills',
    'antigravity-cli':'.gemini/antigravity-cli/skills',
    'gemini':'.gemini/skills',
}
PROJECT={'codex':'.agents/skills','claude':'.claude/skills',
         'antigravity':'.agents/skills','antigravity-cli':'.agents/skills','gemini':'.gemini/skills'}

def target_dir(target,home=None,project=None):
    home=Path(home) if home is not None else Path.home()
    return (Path(project)/PROJECT[target] if project is not None else home/GLOBAL[target])/'animated-logos'

def hashes(folder):
    return {str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}

def install(source,dest,update=False):
    source=Path(source);dest=Path(dest)
    if dest.is_symlink():raise ValueError('Existing skill is a symlink; resolve it before installing')
    if dest.exists() and hashes(source)==hashes(dest):return 'Already current'
    if dest.exists() and not update:raise ValueError('Skill exists; --update preserves a backup before replacement')
    dest.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.animated-logos-stage-',dir=dest.parent.parent))
    try:
        shutil.copytree(source,stage,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        if dest.exists():
            backup=dest.parent.parent/'skill-backups'/('animated-logos-'+datetime.datetime.now().strftime('%Y%m%dT%H%M%S%f'))
            backup.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(dest),str(backup))
        stage.rename(dest)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return 'Installed'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',choices=[*GLOBAL,'all'],default='codex')
    scope=p.add_mutually_exclusive_group();scope.add_argument('--skills-dir');scope.add_argument('--project-root')
    p.add_argument('--update',action='store_true');a=p.parse_args()
    if a.skills_dir and a.target=='all':p.error('--skills-dir requires a single target')
    source=Path(__file__).resolve().parents[1]/'skills/animated-logos'
    targets=list(GLOBAL) if a.target=='all' else [a.target]
    seen=set()
    try:
        for target in targets:
            dest=Path(a.skills_dir).expanduser()/'animated-logos' if a.skills_dir else target_dir(target,project=a.project_root)
            dest=dest.expanduser().absolute()
            if dest in seen:continue
            seen.add(dest);print(f'{install(source,dest,a.update)} for {target}: {dest}')
    except ValueError as error:p.exit(2,f'Error: {error}\n')

if __name__=='__main__':main()
