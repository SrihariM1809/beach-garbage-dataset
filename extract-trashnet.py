import sys
import json
from tqdm import tqdm
import numpy as np
import pandas as pd
from PIL import Image
from pycocotools.coco import COCO

import sys, os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, "w")


# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

from directory import *

# for i in range(3, 7):
#     os.mkdir("trashnet-pngs/" + str(i))

dataset_path = "all_trashnet"
anns_file_path = sys.argv[1]

with open(anns_file_path, "r") as f:
    dataset = json.loads(f.read())

categories = dataset["categories"]
anns = dataset["annotations"]
imgs = dataset["images"]
nr_cats = len(categories)
nr_annotations = len(anns)
nr_images = len(imgs)

cat_names = []
super_cat_names = []
super_cat_ids = {}
super_cat_last_name = ""
nr_super_cats = 0


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
print("Extracting trash pngs ...\n")
imagePathList = getImageFiles(dataset_path)
for count, path in enumerate(tqdm(imagePathList)):
    blockPrint()
    image_filepath = path
    # # pylab.rcParams['figure.figsize'] = (28,28)
    # # for orientation in ExifTags.TAGS.keys():
    # #     if ExifTags.TAGS[orientation] == "Orientation":
    # #         break

    # # Loads dataset as a coco object
    coco = COCO(anns_file_path)

    # # Find image id
    img_id = -1
    for img in imgs:
        if img["file_name"] == image_filepath:
            img_id = img["id"]
            break
    # Show image and corresponding annotations
    if img_id == -1:
        # print("\nIncorrect file name\n")
        continue
    else:
        # print("\nFile found\n")
        # Load image
        # print(image_filepath)
        I = Image.open(image_filepath)

        # Load mask ids
        annIds = coco.getAnnIds(imgIds=img_id, catIds=[], iscrowd=None)
        anns_sel = coco.loadAnns(annIds)

        # Show annotations
        for i in range(len(anns_sel)):
            entity_id = anns_sel[i]["category_id"]
            entity = coco.loadCats(entity_id)[0]["name"]
            # print("{}: {}".format(i, entity_id))
            if entity_id in [3, 4, 5, 6, 7]:
                # color = colorsys.hsv_to_rgb(np.random.random(),1,1)
                mask = np.zeros((img["height"], img["width"]))
                mask = np.maximum(coco.annToMask(anns_sel[i]), mask)
                maskPIL = Image.fromarray(np.uint8(255 * mask))
                black = Image.new("RGBA", I.size, 0)
                foreground = Image.composite(I, black, maskPIL)
                pngfilename = (
                    f"trashnet-pngs/{entity_id}/class_{entity_id}_trash_{i}_image_{count}.png"
                )
                foreground.save(pngfilename, "PNG")
                mask = np.zeros((img["height"], img["width"]))
    enablePrint()