import cv2
import os
import glob
import numpy as np

CURRENT_FILE = os.path.realpath(__file__)
SRC_FOLDER = os.path.dirname(CURRENT_FILE)
ROOT_FOLDER = os.path.dirname(SRC_FOLDER)
DATA_FOLDER_NAME = 'data'
POINTS_FOLDER_NAME = 'points'
DATA_FOLDER = os.path.join(ROOT_FOLDER, DATA_FOLDER_NAME)
POINTS_FOLDER = os.path.join(ROOT_FOLDER, POINTS_FOLDER_NAME)
IMG_FILE_EXTENSION = '.JPG'
PTS_FILE_EXTENSION = '.pts.npy'

M = 8
N = 7

assert N <= 7

color1 = (0, 0, 255)
color2 = (55, 160, 255)
color3 = (70, 225, 255)
color4 = (0, 255, 0)
color5 = (255, 0, 0)
color6 = (225, 70, 255)
color7 = (160, 255, 55)

COLOR = [color1, color2, color3, color4, color5, color6, color7, color1, color2, color3]
assert len(COLOR) >= N

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

global points


def pointsToCorner(points):
    corner = np.zeros((len(points), 1, 2), dtype=np.float32)

    for p, i in zip(points, range(len(points))):
        corner[i, 0, :] = [p[0], p[1]]

    return corner


def cornerToPoints(corner):
    points = []

    for i in range(corner.shape[0]):
        points.append((corner[i, 0, 0], corner[i, 0, 1]))

    return points


def refinePoints(gray, points):
    if len(points) == 9:
        return points
    corner = pointsToCorner(points)
    cv2.cornerSubPix(gray, corner, (11, 11), (-1, -1), criteria)
    points = cornerToPoints(corner)
    return points


def getPoints(img, COLLECTION_NUM, IMAGE_NUM):
    global points

    imgO = img
    gray = cv2.cvtColor(imgO, cv2.COLOR_BGR2GRAY)

    PTS_COLLECTION_PATH = os.path.join(POINTS_FOLDER, str(COLLECTION_NUM))
    pts_file_name = os.path.join(PTS_COLLECTION_PATH, str(IMAGE_NUM) + PTS_FILE_EXTENSION)
    files = glob.glob(pts_file_name)

    WINDOW_NAME = "get points"
    points = []

    def draw_points(imgO, radius=4, thickness=2):
        global points

        imgD = np.copy(imgO)
        i = 0
        for point in points:
            cv2.circle(imgD, tuple(point), radius, COLOR[i/M], thickness)
            i += 1
        return imgD

    def onMouse(event, x, y, _, D):
        global points

        if event == cv2.EVENT_LBUTTONDOWN:
            if len(points) == M * N:
                print('\a')
                print 'FULL'
                return
            points.append((x, y))
            points = refinePoints(gray, points)
            imgD = draw_points(imgO)
            cv2.imshow(WINDOW_NAME, imgD)

    def GUI():
        global points

        done = False
        while(True):
            points = refinePoints(gray, points)
            imgD = draw_points(imgO)
            cv2.imshow(WINDOW_NAME, imgD)
            cv2.setMouseCallback(WINDOW_NAME, onMouse)
            pressedChar = cv2.waitKey(0)
            if pressedChar == 27:
                # pressed ESC
                break
            elif pressedChar == 13:
                # pressed ENTER
                done = True
                break
            elif pressedChar == 117:
                # pressed U
                if len(points) > 0:
                    points.pop()

            else:
                print 'Press one of these:'
                print '\tESC:\t\t to exit'
                print '\tENTER:\t\t to proceed'
                print '\tU:\t\t to remove poins'
        return done

    if len(files) == 1:
        # if file exists load from it
        pts = np.load(files[0])
        points = pts.tolist()

    # show the gui and let the user edit the points
    done = GUI()
    if done:
        # save points
        pts = np.array(points)
        np.save(pts_file_name, pts)
    
    cv2.destroyWindow(WINDOW_NAME)
    return done, points


def getCollectionPhotos(collectionNum, scale_down_factor=1):
    COLLECTION_PATH = os.path.join(DATA_FOLDER, str(collectionNum))
    wildcard = os.path.join(COLLECTION_PATH, '*' + IMG_FILE_EXTENSION)
    files = glob.glob(wildcard)
    imgs = []

    for f in files:
        cimg = cv2.imread(f)
        h, w, _ = cimg.shape
        cimg = cv2.resize(cimg, (w/scale_down_factor, h/scale_down_factor))
        imgs.append(cimg)

    return imgs


def prepareObjectPoints():
    objp = np.zeros((M*N, 3), np.float32)
    objp[:, :2] = np.mgrid[0:M, 0:N].T.reshape(-1, 2)
    
    objPoints = []
    objPoints.append(objp)
    return objPoints


def prepareImagePoints(corners):
    imgPoints = []
    imgPoints.append(corners)
    return imgPoints


def calculateReprojectionError(objPoints, imgPoints, rvecs, tvecs, mtx, dist):
    mean_error = 0
    for i in xrange(len(objPoints)):
        imgpoints2, _ = cv2.projectPoints(objPoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgPoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        mean_error += error
    
    print "total error: ", mean_error / len(objPoints)


def draw3DAxis(img, corners, imgPoints):
    corner = tuple(corners[0].ravel())
    cv2.line(img, corner, tuple(imgPoints[0].ravel()), (255, 0, 0), 5)
    cv2.line(img, corner, tuple(imgPoints[1].ravel()), (0, 255, 0), 5)
    cv2.line(img, corner, tuple(imgPoints[2].ravel()), (0, 0, 255), 5)
    return img
    

if __name__ == '__main__':
    img1, img2, img3 = getCollectionPhotos(100)
