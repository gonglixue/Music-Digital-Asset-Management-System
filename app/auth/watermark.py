from PIL import Image
from PIL import ImageEnhance
import os
POSITION = ('LEFTTOP','RIGHTTOP','CENTER','LEFTBOTTOM','RIGHTBOTTOM',"title","scale")
PADDING = 10
MARKIMAGE = os.path.join('app/static','logo.PNG')

def reduce_opacity(im,opacity):
    assert opacity >= 0 and opacity <=1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im=im.copy()
    alpha=im.split()[3]
    alpha=ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im
	
def water_mark(imagefile,markfile,position=POSITION[4],opacity=0.1):
    im=Image.open(imagefile)
    mark=Image.open(markfile)
    if opacity < 1:
        mark=reduce_opacity(mark,opacity)
    if im.mode != 'RGBA':
        im=im.convert('RGBA')
    layer=Image.new('RGBA',im.size,(0,0,0,0))
    if position == 'title':
        for y in range(0,im.size[1],mark.size[1]):
            for x in range(0,im.size[0],mark.size[0]):
                layer.paste(mark,(x,y))
    elif position == 'scale':
        ratio=min(float(im.size[0])/mark.size[0],float(im.size[1])/mark.size[1])
        w = int(mark.size[0]*ratio)
        h = int(mark.size[1]*ratio)
        mark=mark.resize((w,h))
        layer.paste(mark,((im.size[0]-w)/2,(im.size[1]-h)/2))
    elif position == POSITION[0]:
        position=(PADDING,PADDING)
        layer.paste(mark,position)
    elif position==POSITION[1]:
        position = (im.size[0] - mark.size[0]-PADDING, PADDING)
        layer.paste(mark,position)
    elif position == POSITION[2]:
        position = ( int((im.size[0] - mark.size[0])/2), int((im.size[1] - mark.size[1])/2))
        layer.paste(mark,position)
    elif position == POSITION[3]:
        position = ((im.size[0] - mark.size[0])/2,(im.size[1] - mark.size[1])/2)
        layer.paste(mark,position)
    else:
        position = ((im.size[0] - mark.size[0])/2,(im.size[1] - mark.size[1])/2)
        layer.paste(mark,position)
    return Image.composite(layer,im,layer)
