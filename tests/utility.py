# Copyright (C) 2020-2021  Burak Martin (see 'AUTHOR' for full notice)
import requests
from zipfile import ZipFile
from PyQt5.QtCore import QFileInfo, QDir
from model.misc.project import Project
from model.misc.image import Image
from model.util import trimapToRgba

import qimage2ndarray

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

import numpy as np

imagesFolderName = "test_images"
imageName = "GT15.png"

canvasOutputFolder = "canvas"
gtAlphaOutputFolder = "alpha"
trimapOutputFolder = ""
input_training_lowres = (
    "http://www.alphamatting.com/datasets/zip/input_training_lowres.zip"
)
gt_training_lowres = "http://www.alphamatting.com/datasets/zip/gt_training_lowres.zip"
trimap_training_lowres = (
    "http://www.alphamatting.com/datasets/zip/trimap_training_lowres.zip"
)
urls = [input_training_lowres, gt_training_lowres, trimap_training_lowres]
zip_names = [
    "input_training_lowres.zip",
    "gt_training_lowres.zip",
    "trimap_training_lowres.zip",
]


def setupImages():
    a = downloadAlphaMattinComImages()
    b = makeRandomImage()
    return a and b


def makeRandomImage():
    outputPath = QFileInfo(__file__).dir()
    outputPath.mkdir(imagesFolderName)
    if outputPath.cd(imagesFolderName):
        if not QFileInfo(outputPath.filePath("random.png")).exists():
            randomArray = (np.random.rand(100, 100, 3) * 255.0).astype(np.int)
            image = qimage2ndarray.array2qimage(randomArray)
            image.save(outputPath.filePath("random.png"), quality=100)
            print("Random image created")
        else:
            print("Random image already exists.")
        return True
    else:
        return False


def downloadAlphaMattinComImages():
    outputPath = QFileInfo(__file__).dir()
    try:
        if outputPath.mkdir(imagesFolderName) or QFileInfo.exists(
            outputPath.filePath(imagesFolderName)
        ):
            outputPath.cd(imagesFolderName)

            if (
                QFileInfo(
                    QDir(outputPath.filePath(canvasOutputFolder)).filePath(imageName)
                ).exists()
                and QFileInfo(
                    QDir(outputPath.filePath(gtAlphaOutputFolder)).filePath(imageName)
                ).exists()
                and QFileInfo(
                    QDir(outputPath.filePath("Trimap1")).filePath(imageName)
                ).exists()
            ):
                print("All images have been downloaded and extracted already.")
                return True

            for url, zip_name in zip(urls, zip_names):
                print("Downloading...", zip_name, sep="")
                response = requests.get(url)
                if response.status_code == 200:
                    with open(outputPath.filePath(zip_name), "wb") as file:
                        file.write(response.content)
                else:
                    print("Maybe the files have been moved to another url?")

            with ZipFile(outputPath.filePath(zip_names[0]), "r") as file:
                file.extractall(outputPath.filePath(canvasOutputFolder))
            with ZipFile(outputPath.filePath(zip_names[1]), "r") as file:
                file.extractall(outputPath.filePath(gtAlphaOutputFolder))
            with ZipFile(outputPath.filePath(zip_names[2]), "r") as file:
                file.extractall(outputPath.filePath(trimapOutputFolder))
            print("---Successful---")
            return True
        else:
            print("Could not create the output folder")
            return False
    except:
        print("---Failed---")
        print("Please check your internet connection.")
        return False


def makeProject(imageName, newBackground=False):
    imagesPath = QFileInfo(__file__).dir()
    imagesPath.cd("test_images")
    alphaMattePath = QDir(imagesPath.filePath("alpha")).filePath(f"{imageName}.png")
    canvasPath = QDir(imagesPath.filePath("canvas")).filePath(f"{imageName}.png")
    trimapPath = QDir(imagesPath.filePath("Trimap1")).filePath(f"{imageName}.png")

    alphaMatte = Image(alphaMattePath)
    trimapPreview = trimapToRgba(Image(trimapPath))
    canvas = Image(canvasPath)
    canvas = canvas.convertToFormat(Image.Format_ARGB32)
    alphaMatte = alphaMatte.convertToFormat(Image.Format_Grayscale8)
    return (
        Project(canvas, alphaMatte, trimapPreview, openRandomImage())
        if newBackground
        else Project(canvas, alphaMatte, trimapPreview)
    )


def openCanvas(fileName):
    return __openImage(fileName, 1)


def openAlphaMatte(fileName):
    return __openImage(fileName, 2)


def openTrimap(fileName):
    return __openImage(fileName, 3)


def openTrimapPreview(fileName):
    return trimapToRgba(__openImage(fileName, 3))


def openRandomImage():
    return __openImage("random", 4)


def __openImage(fileName, type: int):
    outputPath = QFileInfo(__file__).dir()
    outputPath.cd(imagesFolderName)
    fileName = f"{fileName}.png"

    if type == 1:
        outputPath.cd("canvas")
        format = Image.Format_ARGB32
    elif type == 2:
        outputPath.cd("alpha")
        format = Image.Format_Grayscale8
    elif type == 3:
        outputPath.cd("Trimap1")
        format = Image.Format_Grayscale8
    elif type == 4:
        format = Image.Format_ARGB32
    else:
        raise Exception()
    image = Image(outputPath.filePath(fileName))
    image = image.convertToFormat(format)
    return image


def guitest(setupFunc, testFunc, destroyFunc):
    def setup():
        return setupFunc()

    def testAndDestroy(setupResult):
        testResults = testFunc(setupResult)
        destroyFunc(setupResult, testResults)

    app = qtw.QApplication([])
    timer = qtc.QTimer()
    timer.setSingleShot(True)
    timer.setInterval(2000)
    timer.timeout.connect(app.exit)
    setupResult = setup()
    timer.timeout.connect(lambda: testAndDestroy(setupResult))
    timer.start()
    app.exec_()
