from utils import getCollectionPhotos, getPoints, calculateReprojectionError, loadPLY
from utils import prepareImagePoints, prepareObjectPoints, pointsToCorner, draw3DAxisLines
import cv2
import numpy as np


def calibrateCamera(objPoints, imgPoints, imgShape):
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, (imgShape[0], imgShape[1]), None, None)
    
    return ret, mtx, dist, rvecs, tvecs


def drawAxis(img, corners, rvecs, tvecs, mtx, dist, scale=1):
    axis = np.float32([[1, 0, 0], [0, 1, 0], [0, 0, -1]])
    
    axis = axis * scale
    
    imgpts, _jac = cv2.projectPoints(axis, np.array(rvecs), np.array(tvecs), mtx, dist)
    img = draw3DAxisLines(img, corners[0], imgpts)


def main():
    COLLECTION_NUM = 8
    IMAGE_NUM = 2  # 1, 2 or 3
    
    M = 8  # 8
    N = 7  # 7
    
    SCALE = 20
    
    imgs = getCollectionPhotos(COLLECTION_NUM, scale_down_factor=5)
    img = imgs[IMAGE_NUM - 1]
    
    done, points = getPoints(img, COLLECTION_NUM, IMAGE_NUM, M, N)
    
    if done:
        if len(points) != M * N:
            print 'Not enough points'
            print 'We need %d x %d = %d points' % (M, N, M * N)
            print 'Run again and complete it'
        else:
            corners = pointsToCorner(points)
            imgPoints = prepareImagePoints(corners)
            objPoints = prepareObjectPoints(M, N, SCALE)
            
            _ret, mtx, dist, rvecs, tvecs = calibrateCamera(objPoints, imgPoints, img.shape)
            calculateReprojectionError(objPoints, imgPoints, rvecs, tvecs, mtx, dist)
            
            imgAxis = img.copy()
            
            drawAxis(imgAxis, corners, rvecs, tvecs, mtx, dist, SCALE)
            cv2.imshow("original image with 3D axis", imgAxis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            vertices, faces = loadPLY()
            
            means = vertices.mean(axis = 0)
            vertices = vertices - means
            vertices[:, [0, 1, 2]] = vertices[:, [2, 1, 0]]
            vertices = vertices + means
            
            
            vertices[:, 0] = vertices[:, 0] - vertices[:, 0].min()
            vertices[:, 1] = vertices[:, 1] - vertices[:, 1].min()
            vertices[:, 2] = vertices[:, 2] - vertices[:, 2].min()
            vertices = vertices / 2
            
            vertices[:, 2] = vertices[:, 2] / 3

            shadowPoints = vertices.copy()
            shadowPoints[:, 2] = 0
            
            objetImagePoints, _jac = cv2.projectPoints(vertices, np.array(rvecs), np.array(tvecs), mtx, dist)
            shadowImagePoints, _jac = cv2.projectPoints(shadowPoints, np.array(rvecs), np.array(tvecs), mtx, dist)

            imgShape = np.zeros_like(img, np.uint8)
            
            for p in shadowImagePoints:
                cv2.circle(imgAxis, (p[0][0], p[0][1]), 1, (0, 0, 0), -1)

            for p in objetImagePoints:
                cv2.circle(imgAxis, (p[0][0], p[0][1]), 1, (255, 255, 255), -1)

            cv2.imshow("with axis and object", imgAxis)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
