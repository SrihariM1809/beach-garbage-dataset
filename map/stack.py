#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PIL import Image
import os

def stacker(imgs, horizontal):
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    if horizontal:
        imgs_comb = np.hstack( [np.asarray( i.resize(min_shape) ) for i in imgs ] )
        imgs_comb = Image.fromarray(imgs_comb)  

    else:
        imgs_comb = np.vstack( [np.asarray( i.resize(min_shape) ) for i in imgs ] )
        imgs_comb = Image.fromarray(imgs_comb)
    
    return imgs_comb

horizontal = False
vert = 4

filelist = [file for file in os.listdir('./maps') if file.startswith('rgb') ]
assert len(filelist) % vert == 0

stacks = []

for i in range(0, len(filelist), vert):
    stack_imgs = [ Image.open(x) for x in filelist]
    stacks.append(stacker(stack_imgs[i:i+vert], False))

final = stacker(stacks, True)
final.save(f'stack_image.png')