import cv2
import os, sys, glob
import numpy as np

CURRENT_FILE = os.path.realpath(__file__)
SRC_FOLDER = os.path.dirname(CURRENT_FILE)
ROOT_FOLDER = os.path.dirname(SRC_FOLDER)
DATA_FOLDER_NAME = 'data'
DATA_FOLDER = os.path.join(ROOT_FOLDER, DATA_FOLDER_NAME)
IMG_FILE_EXTENSIONS = '.JPG'
SCALE_DOWN_FACTOR = 1


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

def findChessBoardPoints(img):
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    M, N = 6, 7
    
    objp = np.zeros((M*N, 3), np.float32)
    objp[:, :2] = np.mgrid[0:N, 0:M].T.reshape(-1, 2)
    
    objpoints = []
    imgpoints = []
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    ret, corners = cv2.findChessboardCorners(gray, (N, M), None, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FILTER_QUADS)
    
    print ret
    
    if ret == True:
        objpoints.append(objp)
        cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)
        
        cv2.drawChessboardCorners(img, (N, M), corners, ret)
        
#         cv2.circle(img, (corners[1, 0, 0], corners[1, 0, 1]), 5, (0, 0, 255))
        
        cv2.imshow('img', img)
        cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    img1, img2, img3 = getCollectionPhotos(100)
    findChessBoardPoints(img3)