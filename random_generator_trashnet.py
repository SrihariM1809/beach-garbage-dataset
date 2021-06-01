#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import random
from typing import Counter
import numpy as np
from PIL import Image
from tqdm import tqdm
import skimage.transform as transform
import matplotlib.colors
import matplotlib.pyplot as plt

cmp = matplotlib.colors.ListedColormap(
    ["tan", "cyan", "pink", "forestgreen", "blue", "purple"]
)


def foregroundAug(foreground):
    # Random rotation, zoom, translation
    angle = np.random.randint(-10, 10) * (np.pi / 180.0)  # Convert to radians
    zoom = np.random.random() * 0.4 + 0.1  # Zoom in range [0.8,1.2)
    t_x = np.random.randint(0, int(foreground.shape[1] / 3))
    t_y = np.random.randint(0, int(foreground.shape[0] / 3))

    tform = transform.AffineTransform(
        scale=(zoom, zoom), rotation=angle, translation=(t_x, t_y)
    )
    foreground = transform.warp(foreground, tform.inverse)
    # Random horizontal flip with 0.5 probability
    if np.random.randint(0, 100) >= 50:
        foreground = foreground[:, ::-1]
    return foreground


def compose(index, foregrounds, background):
    background = Image.fromarray(background)
    bg_w, bg_h = background.size
    
    # Offset list
    t_x_list = []
    t_y_list = []
    for i in range(len(foregrounds)):
        current_foreground = Image.fromarray((foregrounds[i] * 255).astype(np.uint8))
        img_w, img_h = current_foreground.size

        # Random Offsets
        t_x = np.random.randint(int(-bg_w / 1.5), int(bg_w / 1.5))
        t_y = np.random.randint(int(-bg_h / 8), int(bg_h / 1.5))

        t_x_list.append(t_x)
        t_y_list.append(t_y)
        

        offset = ((bg_w - img_w + t_x) // 2, (bg_h - img_h + t_y) // 2)
        background.paste(current_foreground, offset, current_foreground.convert("RGBA")) #RGBA == RGB alpha channel

    return background, t_x_list, t_y_list


def getForegroundMask(
    index, foregrounds, background, background_mask, classes_list, t_x_list, t_y_list
):

    background = Image.fromarray(background)
    bg_w, bg_h = background.size

    # 2D mask
    mask_new = background_mask.astype(np.uint8)
    for i in range(len(foregrounds)):
        foregrounds[i] = foregrounds[i] * 255 # Scaling

        # Get current foreground mask
        current_foreground = (
            1 - np.uint8(np.all(foregrounds[i][:, :, :3] == 0, axis=2))
        ) * classes_list[i]

        img_w, img_h = current_foreground.shape
        offset = ((bg_w - img_h + t_x_list[i]) // 2, (bg_h - img_w + t_y_list[i]) // 2)

        # Paste current foreground mask over previous mask
        mask_new[
            offset[1] : offset[1] + img_w, offset[0] : offset[0] + img_h
        ] = np.maximum(
            mask_new[offset[1] : offset[1] + img_w, offset[0] : offset[0] + img_h],
            current_foreground,
        )
    

    return mask_new


def generator(index, background, background_mask, foreground_full_list):

    # Cluster limits
    cluster_low_limit = 7
    cluster_high_limit = 13
    foreground_list = random.sample(foreground_full_list, random.randint(cluster_low_limit, cluster_high_limit))
    classes_list = [x.rsplit("/", 2)[-2][-1] for x in foreground_list]
    classes_list = [int(i) for i in classes_list]
    f = Counter(classes_list)
    return 1, f

    foregrounds = []
    for i in foreground_list:
        foregrounds.append(np.asarray(Image.open(i)))

    for i in range(len(foregrounds)):
        foregrounds[i] = foregroundAug(foregrounds[i])

    try:
        final_background, t_x_list, t_y_list = compose(index, foregrounds, background)
        mask_new = getForegroundMask(
            index,
            foregrounds,
            background,
            background_mask,
            classes_list,
            t_x_list,
            t_y_list,
        )
        mask_new_pil = Image.fromarray(mask_new)
        final_background.save(f"./synth_images/img_{index}.jpeg")
        mask_new_pil.save(f"./synth_labels/img_{index}.png")
        plt.imsave(
            f"./synth_rgb_labels/img_{index}.png",
            np.asarray(mask_new),
            vmin=1,
            vmax=7,
            cmap=cmp,
        )
        return 1, f
    except:
        return 0, f


background_list = sorted(glob.glob(os.getcwd() + "/backgrounds-only/*"))
background_labels_list = sorted(glob.glob(os.getcwd() + "/beach_labels/*"))

# N = 1 => IMGs == 31
# N = 2 => IMGs == 62

N = 20
background_list *= N
background_labels_list *= N

assert len(background_list) == len(background_labels_list)

foreground_full_list = []
folders_list = glob.glob(os.getcwd() + "/trashnet-pngs/*")
for folder in folders_list:
    foreground_full_list.extend(glob.glob(folder + "/*"))


# Progress bar stuff

pbar = tqdm(range(len(background_list)), desc="description")
count = 0
dist = Counter()

for index in pbar:
    background = np.asarray(Image.open(background_list[index]))
    background_mask = np.asarray(Image.open(background_labels_list[index]))
    curr_count, curr_dist = generator(index, background, background_mask, foreground_full_list)
    count += curr_count
    dist += curr_dist
    pbar.set_description("Generated: %d" % count)
print(dist)