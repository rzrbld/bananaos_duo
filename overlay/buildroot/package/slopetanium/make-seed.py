#!/usr/bin/env python3
"""Pack the original upstream layout for first-run copying to writable storage."""
from pathlib import Path
import sys
import zipfile
source=Path(sys.argv[1]); output=Path(sys.argv[2]); output.parent.mkdir(parents=True,exist_ok=True)
files=[(source/'port/Slopetanium.sh','Slopetanium.sh')]
base=source/'port/slopetanium'
for folder in ('app','web','assets'):
    files += [(p,'slopetanium/'+str(p.relative_to(base))) for p in sorted((base/folder).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
for name in ('port.json','gameinfo.xml','README.md','LICENSE','screenshot.png'):
    if (base/name).is_file(): files.append((base/name,'slopetanium/'+name))
files += [(source/'ui/slopetanium-ui','slopetanium/slopetanium-ui.aarch64')]
for name in ('LICENSE.BananaLinux','README.md'):
    files.append((source/'ui/third_party'/name,'slopetanium/licenses/'+name))
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for path,name in files:
        entry=zipfile.ZipInfo(name,date_time=(2020,1,1,0,0,0));entry.external_attr=(path.stat().st_mode & 0xffff)<<16
        z.writestr(entry,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED)
