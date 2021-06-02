#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

def splitter(filename):
    script_args = ['-b', 'none', '-f', '1', '-u', '3', '-d', '500', filename, filename[:-4] + '-cropped.png']
    subprocess.Popen(['./multicrop2'] + script_args)

def splitter_all(folderlist):
    for folder in folderlist:
        for i in os.listdir(folder):
            splitter(os.path.join(folder, i))

splitter_all(['bezier', 'real', 'random'])