import cv2
import os, glob
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

M = 6
N = 5

color1 = (0, 0, 255)
color2 = (55, 160, 255)
color3 = (70, 225, 255)
color4 = (0, 255, 0)
color5 = (255, 0, 0)
COLOR = [color1, color2, color3, color4, color5]
assert len(COLOR) == N

def getPoints(img, COLLECTION_NUM, IMAGE_NUM):
    imgO = img
    
    PTS_COLLECTION_PATH = os.path.join(POINTS_FOLDER, str(COLLECTION_NUM))
    pts_file_name = os.path.join(PTS_COLLECTION_PATH, str(IMAGE_NUM) + PTS_FILE_EXTENSION)
    files = glob.glob(pts_file_name)

    points = []
    WINDOW_NAME = "get points"
    
    def draw_points(imgO, points, radius=4, thickness=2):
        imgD = np.copy(imgO)
        i = 0
        for point in points:
            cv2.circle(imgD, tuple(point), radius, COLOR[i/M], thickness)
            i += 1
        return imgD
    
    def onMouse(event, x, y, _, D):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(points) == M * N:
                print 'FULL'
                return
            points.append((x, y))
            imgD = draw_points(imgO, points)
            cv2.imshow(WINDOW_NAME, imgD)
    
    def GUI(points):
        done = False
        while(True):
            imgD = draw_points(imgO, points)
            cv2.imshow(WINDOW_NAME, imgD)
            cv2.setMouseCallback(WINDOW_NAME, onMouse)
            pressedChar = cv2.waitKey(0)
            if pressedChar == 27:
                #pressed ESC
                break
            elif pressedChar == 13:
                #pressed ENTER
                done = True
                break
            elif pressedChar == 117:
                #pressed U
                if len(points) > 0:
                    points.pop()
            else:
                print 'Press these:'
                print '\tESC:\t\t to exit'
                print '\tENTER:\t\t to proceed'
                print '\tU:\t\t to remove poins'
        return done
    
    if len(files) == 0:
        #try to get the points from user GUI.
        done = GUI(points)
        
        if done:
            #save points
            pts = np.array(points)
            np.save(pts_file_name, pts)
        
        return done, points
                
    else:
        pts = np.load(files[0])
        points = pts.tolist()
        done = GUI(points)
        
        if done:
            pts = np.array(points)
            np.save(pts_file_name, pts)
        
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

def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
    cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
    cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
    return img
    

def findChessBoardPoints(img):
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    M, N = 6, 7
    
    objp = np.zeros((M*N, 3), np.float32)
    objp[:, :2] = np.mgrid[0:N, 0:M].T.reshape(-1, 2)
    
    axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]])
    #axis = axis.reshape(-1, 3)
    
    objpoints = []
    imgpoints = []
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    ret, corners = cv2.findChessboardCorners(gray, (N, M), None, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FILTER_QUADS)
    
    print ret
    
    if ret == True:
        objpoints.append(objp)
        cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners)
        
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        
        rvecs2, tvecs2, inliers = cv2.solvePnPRansac(objp, corners, mtx, dist)
        
        imgpts, jac = cv2.projectPoints(axis, np.array(rvecs), np.array(tvecs), mtx, dist)
        
        img = draw(img, corners, imgpts)
        
        cv2.imshow('img', img)
        cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    img1, img2, img3 = getCollectionPhotos(100)
    findChessBoardPoints(img2)