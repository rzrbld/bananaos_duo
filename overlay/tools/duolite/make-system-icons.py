#!/usr/bin/env python3
"""Original 32px console sprites for the Duo's existing pixel-icon system."""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[2]/'ui/assets/rnds/icons'
OUT.mkdir(parents=True, exist_ok=True)
INK='#17151c'; DARK='#30313c'; MID='#727882'; LIGHT='#cdd1d8'; WHITE='#eff1f2'

def canvas():
    im=Image.new('RGBA',(32,32));return im,ImageDraw.Draw(im)
def rect(d,box,fill,outline=None):d.rectangle(box,fill=fill,outline=outline)
def poly(d,points,fill,outline=INK):d.polygon(points,fill=fill,outline=outline)
def save(name,im):im.save(OUT/(name+'.png'),optimize=True)

# Nintendo 3DS: open clamshell, wide upper display and lower touch panel.
im,d=canvas()
poly(d,[(6,2),(25,2),(27,4),(27,14),(4,14),(4,4)],'#46506c')
rect(d,(6,4,25,12),DARK);rect(d,(8,5,23,11),'#799ba0');rect(d,(9,5,22,5),'#b6cfd1')
rect(d,(7,14,24,15),'#9ba2b3',INK)
poly(d,[(4,16),(27,16),(30,28),(28,30),(3,30),(1,28)],'#7f8aaf')
poly(d,[(5,17),(26,17),(28,26),(3,26)],'#9ca9ca',None)
rect(d,(11,18,21,26),INK);rect(d,(12,19,20,25),'#9bb9bb')
d.ellipse((4,18,8,22),fill='#d5dce9',outline=DARK)
rect(d,(5,24,7,28),DARK);rect(d,(4,25,8,26),DARK)
for x,y in [(25,20),(23,22),(27,22),(25,24)]:rect(d,(x,y,x,y),'#252e4c')
rect(d,(24,28,25,28),'#6de074');save('3ds',im)

# Sony PSP: rounded black handheld, widescreen and silver control rings.
im,d=canvas()
poly(d,[(4,8),(27,8),(30,11),(31,22),(28,26),(3,26),(0,22),(1,12)],DARK)
poly(d,[(4,9),(27,9),(29,12),(29,22),(27,24),(4,24),(2,22),(2,12)],'#555762',None)
rect(d,(8,10,23,23),INK);rect(d,(9,11,22,21),'#568d98');rect(d,(10,12,21,13),'#83b2b4')
rect(d,(3,13,6,18),LIGHT);rect(d,(2,15,7,16),LIGHT);rect(d,(4,14,5,17),DARK)
d.ellipse((3,20,6,23),fill=INK,outline=LIGHT)
for x,y in [(27,13),(25,16),(29,16),(27,19)]:rect(d,(x,y,x,y),LIGHT)
rect(d,(12,24,20,24),MID);save('psp',im)

# Dreamcast: pale square shell, round disc lid and four front controller ports.
im,d=canvas()
poly(d,[(5,5),(25,5),(29,10),(28,26),(3,26),(2,10)],'#a3a8b1')
poly(d,[(5,6),(24,6),(27,10),(26,21),(5,21),(4,10)],WHITE)
d.ellipse((7,7,24,21),fill='#d6dae1',outline='#8f96a0')
d.arc((11,10,20,18),30,330,fill='#df6b35',width=1);d.arc((13,12,18,16),30,330,fill='#df6b35',width=1)
rect(d,(3,22,28,25),'#747b87');rect(d,(6,23,9,24),INK);rect(d,(11,23,14,24),INK)
rect(d,(16,23,19,24),INK);rect(d,(21,23,24,24),INK)
rect(d,(6,19,8,20),'#e29854');save('dreamcast',im)

# Master System: black/red angular console and its squared two-button pad.
im,d=canvas()
poly(d,[(4,5),(27,5),(30,9),(29,20),(2,20),(1,9)],DARK)
poly(d,[(5,6),(26,6),(28,9),(3,9)],'#7c7c83',None)
rect(d,(3,10,28,11),'#ba343b');rect(d,(11,6,22,8),INK)
rect(d,(4,13,17,17),INK);rect(d,(6,14,14,14),'#676770');rect(d,(21,14,25,16),'#a73c42')
d.line([(24,20),(25,23),(20,24)],fill=INK)
rect(d,(4,23,22,30),INK);rect(d,(5,24,21,29),'#6c6c74')
rect(d,(8,24,10,29),DARK);rect(d,(6,26,12,27),DARK)
rect(d,(16,26,17,27),'#bd3b42');rect(d,(19,26,20,27),'#bd3b42');save('mastersystem',im)

# MAME: cabinet with a lit marquee, CRT, joystick and coin door.
im,d=canvas()
poly(d,[(9,1),(24,1),(27,5),(26,13),(24,18),(28,22),(26,30),(8,30),(5,25),(6,19),(8,15),(7,5)],'#a23d34')
poly(d,[(10,2),(23,2),(25,5),(8,5)],'#f1bd43',None)
rect(d,(10,3,22,4),'#fff0a5')
rect(d,(9,6,24,16),INK);rect(d,(11,7,22,14),'#456d89');rect(d,(12,8,20,9),'#88b4c5')
poly(d,[(9,17),(23,17),(26,21),(7,21)],'#df8750')
rect(d,(12,16,13,19),INK);rect(d,(11,16,14,17),'#cf3444')
for x in (19,22):rect(d,(x,19,x+1,19),'#f6cf5c')
rect(d,(9,23,24,28),DARK);rect(d,(14,24,19,28),INK);rect(d,(16,25,17,26),MID)
rect(d,(7,29,26,30),INK);save('mame',im)

# Amstrad CPC: integrated black keyboard, tape deck and monitor with colour keys.
im,d=canvas()
rect(d,(5,2,26,19),INK);rect(d,(6,3,25,17),'#8e9293');rect(d,(8,4,23,15),DARK)
rect(d,(9,5,22,14),'#305f61');rect(d,(10,6,20,7),'#70a4a0');rect(d,(14,18,18,20),MID)
poly(d,[(4,21),(26,21),(30,29),(1,29)],'#5d6269')
poly(d,[(5,22),(20,22),(23,27),(3,27)],INK,None)
for y in (23,25):
 for x in range(5,19,3):rect(d,(x,y,x+1,y),'#b3b5b7')
rect(d,(7,27,18,27),LIGHT)
rect(d,(22,22,26,26),DARK);rect(d,(23,23,25,24),'#9aa6ae')
for x,c in [(20,'#d43b43'),(22,'#49a36b'),(24,'#537bb0')]:rect(d,(x,28,x+1,28),c)
save('amstradcpc',im)

# Wii: vertical white console, blue disc slot and its white remote.
im,d=canvas()
poly(d,[(8,2),(20,1),(22,27),(8,28),(6,25)],'#a4aab3')
poly(d,[(9,3),(18,2),(20,25),(9,26)],WHITE,None)
rect(d,(11,6,12,19),'#6cb8d7');rect(d,(12,6,12,19),'#344b61')
rect(d,(16,4,17,5),MID);rect(d,(16,22,17,23),'#9da7b1')
poly(d,[(7,27),(22,26),(25,29),(4,30)],'#818b98')
rect(d,(24,8,29,27),INK);rect(d,(25,9,28,26),WHITE)
rect(d,(26,11,27,14),DARK);rect(d,(25,12,28,13),DARK)
rect(d,(26,17,27,18),'#8a929c');rect(d,(26,22,27,23),'#6795bf')
save('wii',im)
print('Wrote seven original transparent 32×32 console sprites')
