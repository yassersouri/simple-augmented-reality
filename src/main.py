from utils import getCollectionPhotos, getPoints, M, N, calculateReprojectionError
from utils import prepareImagePoints, prepareObjectPoints, pointsToCorner, draw3DAxis
import cv2
import numpy as np

def main():
    COLLECTION_NUM = 4
    IMAGE_NUM = 1 # 1, 2 or 3
    
    imgs = getCollectionPhotos(COLLECTION_NUM, scale_down_factor=5)
    img = imgs[IMAGE_NUM - 1]
    
    done, points = getPoints(img, COLLECTION_NUM, IMAGE_NUM)
    
    if done:
        if len(points) != M * N:
            print 'Not enough points'
            print 'We need %d x %d = %d points' % (M, N, M * N)
            print 'Run again and complete it'
        else:
            corners = pointsToCorner(points)
            imgPoints = prepareImagePoints(corners)
            objPoints = prepareObjectPoints()
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, (img.shape[0], img.shape[1]), None, None)
            calculateReprojectionError(objPoints, imgPoints, rvecs, tvecs, mtx, dist)
            
            axis = np.float32([[3, 0, 0], [0, 3, 0], [0, 0, -3]])
            
#             rvecs, tvecs, inliers = cv2.solvePnPRansac(objPoints[0], corners, mtx, dist)
            
            imgpts, jac = cv2.projectPoints(axis, np.array(rvecs), np.array(tvecs), mtx, dist)
            
            img = draw3DAxis(img, corners, imgpts)
            cv2.imshow("img", img)
            cv2.waitKey(0)
            

if __name__ == '__main__':
    main()