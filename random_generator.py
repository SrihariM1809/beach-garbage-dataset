#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import random
import numpy as np
from PIL import Image
from tqdm import tqdm
import skimage.transform as transform
import matplotlib.colors
import matplotlib.pyplot as plt

cmp = matplotlib.colors.ListedColormap(
    ["tan", "cyan", "pink", "forestgreen", "blue", "purple", "crimson"]
)


def foregroundAug(foreground):
    # Random rotation, zoom, translation
    angle = np.random.randint(-10, 10) * (np.pi / 180.0)  # Convert to radians
    zoom = np.random.random() * 0.4 + 0.8  # Zoom in range [0.8,1.2)
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
    t_x_list = []
    t_y_list = []
    for i in range(len(foregrounds)):
        current_foreground = Image.fromarray((foregrounds[i] * 255).astype(np.uint8))
        img_w, img_h = current_foreground.size
        t_x = np.random.randint(int(-bg_w / 1.5), int(bg_w / 1.5))
        t_y = np.random.randint(int(-bg_h / 8), int(bg_h / 1.5))

        t_x_list.append(t_x)
        t_y_list.append(t_y)

        offset = ((bg_w - img_w + t_x) // 2, (bg_h - img_h + t_y) // 2)
        background.paste(current_foreground, offset, current_foreground.convert("RGBA"))

    return background, t_x_list, t_y_list


def compose2(index, foregrounds, background):
    bg_w, bg_h = background.shape[:2]
    t_x_list = []
    t_y_list = []

    for i in range(len(foregrounds)):
        # current_foreground = (foregrounds[i] * 255).astype(np.uint8)
        current_foreground = np.uint8(foregrounds[i] * 255)
        img_w, img_h = current_foreground.shape[:2]
        t_x = np.random.randint(0, int(bg_w / 2))
        t_y = np.random.randint(0, int(bg_h / 2))

        t_x_list.append(t_x)
        t_y_list.append(t_y)
        alpha_s = current_foreground[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        composed_background = np.copy(background)

        for c in range(0, 3):
            composed_background[t_y : t_y + img_w, t_x : t_x + img_h, c] = (
                alpha_s * current_foreground[:, :, c]
                + alpha_l * background[t_y : t_y + img_w, t_x : t_x + img_h, c]
            )
    background_pil = Image.fromarray(background)
    background_pil.save(f"./synth_images/img_{index}.jpeg")
    return t_x_list, t_y_list


def getForegroundMask(
    index, foregrounds, background, background_mask, classes_list, t_x_list, t_y_list
):

    background = Image.fromarray(background)
    bg_w, bg_h = background.size
    # mask_new = Image.new("L", (bg_w, bg_h))
    mask_new = background_mask.astype(np.uint8)
    for i in range(len(foregrounds)):
        foregrounds[i] = foregrounds[i] * 255
        current_foreground = (
            1 - np.uint8(np.all(foregrounds[i][:, :, :3] == 0, axis=2))
        ) * classes_list[i]
        # current_foreground = Image.fromarray(foregrounds[i])
        img_w, img_h = current_foreground.shape
        offset = ((bg_w - img_h + t_x_list[i]) // 2, (bg_h - img_w + t_y_list[i]) // 2)
        mask_new[
            offset[1] : offset[1] + img_w, offset[0] : offset[0] + img_h
        ] = np.maximum(
            mask_new[offset[1] : offset[1] + img_w, offset[0] : offset[0] + img_h],
            current_foreground,
        )
    # mask_new.paste(current_foreground, offset)

    return mask_new


def generator(index, background, background_mask, foreground_full_list):
    foreground_list = random.sample(foreground_full_list, random.randint(4, 9))
    classes_list = [x.rsplit("/", 2)[-2][-1] for x in foreground_list]
    classes_list = results = [int(i) for i in classes_list]

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
        return 1
    except:
        return 0


background_list = sorted(glob.glob(os.getcwd() + "/backgrounds-only/*"))
background_labels_list = sorted(glob.glob(os.getcwd() + "/beach_labels/*"))

# N = 1 => IMGs == 31

N = 5
background_list *= N
background_labels_list *= N

assert len(background_list) == len(background_labels_list)

foreground_full_list = []
folders_list = glob.glob(os.getcwd() + "/pngs/*")
for folder in folders_list:
    foreground_full_list.extend(glob.glob(folder + "/*"))

pbar = tqdm(range(len(background_list)), desc="description")
count = 0
for index in pbar:
    background = np.asarray(Image.open(background_list[index]))
    background_mask = np.asarray(Image.open(background_labels_list[index]))
    count += generator(index, background, background_mask, foreground_full_list)
    pbar.set_description("Generated: %d" % count)
