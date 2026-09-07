"""Draw the course favicon: BYU navy disc with a gold ring (the medallion colors) and a white
three-layer GIS stack. Writes docs/assets/favicon.png (512 px)."""
from PIL import Image, ImageDraw
S=512; SS=4; N=S*SS
NAVY=(0,46,93,255); GOLD=(197,175,125,255); WHITE=(255,255,255,255); BLUE=(90,155,216,255)
im=Image.new('RGBA',(N,N),(0,0,0,0)); d=ImageDraw.Draw(im)
d.ellipse([0,0,N-1,N-1],fill=GOLD)
r=int(N*0.045); d.ellipse([r,r,N-1-r,N-1-r],fill=NAVY)
def layer(cy, color, w=0.58, h=0.19):
    cx=N/2; hw=N*w/2; hh=N*h/2
    d.polygon([(cx,cy-hh),(cx+hw,cy),(cx,cy+hh),(cx-hw,cy)],fill=color)
# three offset rhombi, top one bright
layer(N*0.62, (255,255,255,140))
layer(N*0.50, BLUE)
layer(N*0.38, WHITE)
im=im.resize((S,S),Image.LANCZOS)
im.save('docs/assets/favicon.png')
print('favicon written')
