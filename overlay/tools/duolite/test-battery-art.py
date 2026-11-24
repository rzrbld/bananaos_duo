#!/usr/bin/env python3
"""Render real status bars: the full fill must fit its frame at every scale."""
import argparse,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageChops
p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('assets',type=Path);a=p.parse_args()
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);(root/'data').mkdir();(root/'roms').mkdir()
 (root/'systems.conf').write_text('[nds]\nname=Nintendo DS\nfolder=nds\next=nds\nalways=yes\nrun=test %ROM%\n')
 for theme in ('dark','light'):
  (root/'data/settings.conf').write_text('theme='+theme+'\nbattery=icon\n')
  for scale in (1,1.6,2):
   prefix=str(root/(theme+str(scale)+'-'))
   subprocess.run([str(a.binary.resolve()),'--headless',prefix,'--size',f'{round(640*scale)}x{round(480*scale)}','--top-width',str(round(960*scale)),'--assets',str(a.assets.resolve()),'--systems',str(root/'systems.conf'),'--roms',str(root/'roms'),'--data',str(root/'data'),'--script','home 0; wait 2400; battery 0; shot empty; battery 100; shot full; battery 66; shot partial; battery 25; shot quarter'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   box=(round(44*scale),round(25*scale),round(44*scale)+round(26*scale),round(25*scale)+round(14*scale))
   def crop(name):return Image.open(prefix+name+'-top.png').convert('RGB').crop(box)
   empty=crop('empty');full=crop('full');mask=ImageChops.difference(empty,full).convert('L')
   assert mask.getbbox()==(round(3*scale),round(3*scale),round(3*scale)+round(16*scale),round(3*scale)+round(8*scale)),(theme,scale,mask.getbbox())
   count=lambda im:sum(v!=0 for v in im.tobytes())
   maximum=count(mask)
   for name,fraction in [('partial',.66),('quarter',.25)]:
    part=ImageChops.difference(empty,crop(name)).convert('L')
    assert abs(count(part)/maximum-fraction)<.04,(theme,scale,name)
   # On the body's top border, its two-pixel frame spans 22 logical pixels.
   row=round(scale/2)
   frame=[empty.getpixel((x,row)) for x in range(round(22*scale))]
   assert max(max(c)-min(c) for c in frame)<20
print('PASS: real dark/light battery frames and 25/66/100% fills at 1x, 1.6x and 2x')
