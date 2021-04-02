from PIL import Image, ImageChops
import glob
from tqdm import tqdm
import concurrent.futures
import os

for i in range(3, 8):
    os.mkdir("pngs/cropped_" + str(i))


def cropper(filename):
    img = Image.open(filename)
    pixels = img.load()
    xlist = []
    ylist = []
    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            if pixels[x, y] != (0, 0, 0, 0):
                xlist.append(x)
                ylist.append(y)
    try:
        left = min(xlist)
    except ValueError:
        print(filename + " is probably empty. Skipping!")
        return False

    right = max(xlist)
    top = min(ylist)
    bottom = max(ylist)

    img = img.crop((left - 10, top - 10, right + 10, bottom + 10))
    splitname = filename.rsplit("/", 2)
    savename = splitname[0] + "/cropped_" + splitname[2][6] + "/" + splitname[2]
    img.save(savename)
    return True


if __name__ == "__main__":
    folders_list = glob.glob(os.getcwd() + "/pngs/*")
    images_list = []
    for folder in folders_list:
        images_list.extend(glob.glob(folder + "/*"))

    # print(len(images_list))
    # print("\nStarting process ...")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        _ = list(tqdm(executor.map(cropper, images_list), total=len(images_list)))
    print("Done.")
