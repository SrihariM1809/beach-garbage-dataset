#!/usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.colors
from pycocotools.coco import COCO
import numpy as np
import skimage.io as sio
from tqdm import tqdm
from PIL import Image

filecoco = "annotations_coco.json"
coco = COCO(filecoco)

catIDs = coco.getCatIds()
cats = coco.loadCats(catIDs)
nms = [cat["name"] for cat in cats]
filterClasses = nms
catIds = coco.getCatIds(1)
imgIds = coco.getImgIds(catIds=catIds)

print("No of images: ", len(imgIds))

cmp = matplotlib.colors.ListedColormap(
    ["tan", "cyan", "pink", "forestgreen", "blue", "purple", "crimson"]
)


def getClassName(classID, cats):
    for i in range(len(cats)):
        if cats[i]["id"] == classID:
            return cats[i]["name"]
    return None


def mask_generator(img_id):
    img = coco.loadImgs(img_id)[0]
    mask = np.zeros((img["height"], img["width"]))
    annIds = coco.getAnnIds(imgIds=img["id"], catIds=catIds)
    anns = coco.loadAnns(annIds)
    for i in range(len(anns)):
        className = getClassName(anns[i]["category_id"], cats)
        pixel_value = filterClasses.index(className) + 1
        mask = np.maximum(coco.annToMask(anns[i]) * pixel_value, mask)
    int_mask = mask.astype(np.uint8)
    int_mask[int_mask == 0] = 1
    # np.savetxt(img["file_name"][:-5] + "_gt.csv", int_mask, fmt="%d", delimiter=",")
    filename = img["file_name"].split("/")[-1]
    rgb_filename = "rgb_labels/" + filename[:-5] + ".png"
    label_filename = "labels/" + filename[:-5] + ".png"
    Image.fromarray(int_mask).save(label_filename)
    plt.imsave(rgb_filename, int_mask, vmin=1, vmax=7, cmap=cmp)


print(f"\nCreating RGB and Ground truth labels for {len(imgIds)} images")
for img_id in tqdm(imgIds):
    mask_generator(img_id)
print("Done")