#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, json, os, datetime
from PIL import Image
from dateutil import parser
from osgeo import ogr


def COCOInfoFrom(zillin_json, dataset_name):
    date = parser.isoparse(zillin_json["VersionGenerated"])
    return {
        "year": date.year,
        "version": zillin_json["Version"],
        "description": dataset_name,
        "contributor": "zillin.io",
        "url": "https://zillin.io",
        "date_created": date.strftime("%Y-%m-%d"),
    }


def COCOImagesFrom(zillin_images_json, image_path):
    image_ids = {}
    coco_images = []
    for image_json in zillin_images_json:
        image_filename = os.path.join(image_path, image_json["ImageName"])
        print("Processing image: {}".format(image_filename))
        try:
            with Image.open(image_filename) as image:
                width, height = image.size
                date_captured = datetime.datetime.fromtimestamp(
                    os.stat(image_filename).st_mtime
                )
                image_ids[image_json["ImageId"]] = image_ids.get(
                    image_json["ImageId"], len(image_ids) + 1
                )
                coco_images.append(
                    {
                        "id": image_ids[image_json["ImageId"]],
                        "width": width,
                        "height": height,
                        "file_name": image_filename,
                        "license": 1,
                        "coco_url": "",
                        "date_captured": date_captured.strftime("%Y-%m-%d"),
                    }
                )
        except Exception as x:
            print("\tFailed: {}".format(x))
    return coco_images, image_ids


def getPolygons(geometry):
    polygons = []
    type = geometry.GetGeometryType()
    if type == 3:  # POLYGON
        polygons = [geometry]
    elif type == 6:  # MULTIPOLYGON
        polygons = [
            geometry.GetGeometryRef(i) for i in range(0, geometry.GetGeometryCount())
        ]
    return polygons


def processGeometry(wkt):
    annotations = []
    geometry = ogr.CreateGeometryFromWkt(wkt)
    for poly in getPolygons(geometry):
        area = poly.GetArea()
        xmin, xmax, ymin, ymax = poly.GetEnvelope()
        bounding_box = [xmin, ymin, xmax - xmin, ymax - ymin]  # x,y,width,height
        segmentation = []
        for i in range(0, poly.GetGeometryCount()):
            g = poly.GetGeometryRef(i)
            points = []
            for j in range(0, g.GetPointCount()):
                point = g.GetPoint(j)
                points.append(point[0])
                points.append(point[1])
            segmentation.append(points)
        annotations.append((segmentation, area, bounding_box))
    return annotations


def COCOAnnotationsFrom(zillin_images_json, image_ids):
    coco_annotations = []
    category_ids = {
        "Beach": 1,
        "Wood and Plants": 3,
        "Plastic and Polymer": 4,
        "Other background": 2,
        "Foam": 5,
        "Clothes": 6,
        "Other garbage": 7,
    }

    for image_json in zillin_images_json:
        image_id = image_ids.get(image_json["ImageId"])
        if image_id:
            for annotation_json in image_json["Annotations"]:
                for segmentation_json in annotation_json["Segmentation"]:
                    # category_ids[segmentation_json["ClassName"]] = category_ids.get(
                    #     segmentation_json["ClassName"], len(category_ids) + 1
                    # )
                    # print(category_ids)
                    processed_geometry = processGeometry(segmentation_json["Selection"])
                    for (segmentation, area, bounding_box) in processed_geometry:
                        annotation_id = len(coco_annotations) + 1
                        coco_annotations.append(
                            {
                                "id": annotation_id,
                                "image_id": image_id,
                                "category_id": category_ids[
                                    segmentation_json["ClassName"]
                                ],
                                "segmentation": segmentation,
                                "area": area,
                                "bbox": bounding_box,
                                "iscrowd": 0,
                            }
                        )
    return coco_annotations, category_ids


def COCOCategoriesFrom(category_ids):
    coco_categories = []
    for name, id in category_ids.items():
        coco_categories.append({"id": id, "name": name, "supercategory": "zillin"})
    return coco_categories


argparser = argparse.ArgumentParser()
argparser.add_argument("-i", "--img_path", type=str, default="")
argparser.add_argument(
    "zillin_json_file", type=argparse.FileType("r", encoding="utf-8-sig")
)  # mind the encoding!
args = argparser.parse_args()

with args.zillin_json_file as j:
    print("Processing Zillin export: {}".format(j.name))
    try:
        zillin_json = json.load(j)
        for dataset_number, dataset_json in enumerate(zillin_json["DataSets"]):
            dataset_name = dataset_json["DataSetName"]
            images_json = dataset_json["Images"]

            print("Processing dataset: {}".format(dataset_name))
            coco = {"info": COCOInfoFrom(zillin_json, dataset_name)}
            coco["images"], image_ids = COCOImagesFrom(
                images_json, args.img_path.strip()
            )
            coco["licenses"] = [
                {"id": 1, "name": "Unknown", "url": ""}
            ]  # not in Zillin
            coco["annotations"], category_ids = COCOAnnotationsFrom(
                images_json, image_ids
            )
            coco["categories"] = COCOCategoriesFrom(category_ids)

            coco_filename = "{}.{}.coco".format(j.name, dataset_number)
            print("Writing COCO JSON file: {}".format(coco_filename))
            with open(coco_filename, "w") as coco_out:
                json.dump(coco, coco_out)

    except Exception as x:
        print("COCO conversion failed: {}".format(x.with_traceback()))
