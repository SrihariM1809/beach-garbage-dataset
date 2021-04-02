#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import io
import shutil
import matplotlib.pyplot as plt

data = json.load(io.open("annotations.json", "r", encoding="utf-8-sig"))

# ADD path here
PATH = ""

filelist = []
for dataset_json in data["DataSets"]:
    for image_json in dataset_json["Images"]:
        image_filename = image_json["ImageName"]
        filelist.append(image_filename)

for item in filelist:
    sourcename = PATH + "all/" + item
    destname = PATH + "reviewed_images/" + item
    shutil.copy(sourcename, destname)