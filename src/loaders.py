import cv2
import os, sys, glob

CURRENT_FILE = os.path.realpath(__file__)
SRC_FOLDER = os.path.dirname(CURRENT_FILE)
ROOT_FOLDER = os.path.dirname(SRC_FOLDER)
DATA_FOLDER_NAME = 'data'
DATA_FOLDER = os.path.join(ROOT_FOLDER, DATA_FOLDER_NAME)
IMG_FILE_EXTENSIONS = '.JPG'
SCALE_DOWN_FACTOR = 5


def getCollectionPhotos(collectionNum):
    COLLECTION_PATH = os.path.join(DATA_FOLDER, str(collectionNum))
    wildcard = os.path.join(COLLECTION_PATH, '*' + IMG_FILE_EXTENSIONS)
    files = glob.glob(wildcard)
    imgs = []
    
    for f in files:
        cimg = cv2.imread(f)
        h, w, _ = cimg.shape
        cimg = cv2.resize(cimg, (w/SCALE_DOWN_FACTOR, h/SCALE_DOWN_FACTOR))
        imgs.append(cimg)
    
    return imgs[0], imgs[1], imgs[2]
    