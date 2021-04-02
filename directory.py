import os


def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
    return allFiles


def getImageFiles(imageDirName):
    filesList = getListOfFiles(imageDirName)
    imageFileList = list()
    for filePath in filesList:
        fileName = filePath.split("/")[-1]
        ext = fileName.split(".")[-1]
        if ext == "JPEG" or ext == "jpeg":
            imageFileList.append(filePath)
    return imageFileList
