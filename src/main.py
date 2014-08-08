from utils import getCollectionPhotos, getPoints, calculateReprojectionError, loadPLY, refine_vertices
from utils import prepareImagePoints, prepareObjectPoints, pointsToCorner, draw3DAxisLines, calculate_shadow, calculate_colors, get_save_address
import cv2
import numpy as np
from geomhelper import normalize
import math


def calibrateCamera(objPoints, imgPoints, imgShape):
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, (imgShape[0], imgShape[1]), None, None)
    
    return ret, mtx, dist, rvecs, tvecs


def drawAxis(img, corners, rvecs, tvecs, mtx, dist, scale=1):
    axis = np.float32([[1, 0, 0], [0, 1, 0], [0, 0, -1]])
    
    axis = axis * scale
    
    imgpts, _jac = cv2.projectPoints(axis, np.array(rvecs), np.array(tvecs), mtx, dist)
    img = draw3DAxisLines(img, corners[0], imgpts)


def get_z_scales():
    Z_SCALES = np.ones((100, 10)) * -1
    Z_SCALES[3, 3] = 1
    Z_SCALES[8, 2] = 3
    Z_SCALES[8, 3] = 3
    Z_SCALES[4, 1] = -2
    Z_SCALES[4, 2] = -0.5
    Z_SCALES[4, 3] = 1
    Z_SCALES[5, 3] = 2.5
    return Z_SCALES


def main():
    
    Z_SCALES = get_z_scales()
    
    """ What Image to Choose """
    COLLECTION_NUM = 4
    IMAGE_NUM = 3  # 1, 2 or 3
    
    """ Calibration Parameters """
    M = 8  # 8
    N = 7  # 7
    SCALE = 20
    
    """ Shadow Parameter """
    l = [-1 * math.cos(math.radians(60)), 0, math.sin(math.radians(60))]
    l = normalize(l)
    transparency = 0.7
    DO_SHADOW = True
    DO_COLOR = True
    SMOOTHING = True
    
    """ Actual calculations begin """
    imgs = getCollectionPhotos(COLLECTION_NUM, scale_down_factor=5)
    img = imgs[IMAGE_NUM - 1]
    done, points = getPoints(img, COLLECTION_NUM, IMAGE_NUM, M, N)
    SAVE_ADDRESS = get_save_address(COLLECTION_NUM, IMAGE_NUM, DO_COLOR, SMOOTHING)
    
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
            
            imgAxis = img.copy()
            
            drawAxis(imgAxis, corners, rvecs, tvecs, mtx, dist, SCALE)
            cv2.imshow("original image with 3D axis", imgAxis)
            key = cv2.waitKey(0)
            if key == 27:
                exit();
            cv2.destroyAllWindows()
            
            vertices, faces = loadPLY()
            vertices = refine_vertices(vertices, Z_SCALES[COLLECTION_NUM, IMAGE_NUM])
            
            vertices[:, 0] = vertices[:, 0] + 180

            shadowPoints = calculate_shadow(vertices, l, DO_SHADOW)
            objectColors = calculate_colors(vertices, faces, l, DO_COLOR, SMOOTHING)
            
            objectImagePoints, _jac = cv2.projectPoints(vertices, np.array(rvecs), np.array(tvecs), mtx, dist)
            shadowImagePoints, _jac = cv2.projectPoints(shadowPoints, np.array(rvecs), np.array(tvecs), mtx, dist)

            imgShape = img.copy()
            imgShadow = img.copy()
            
            if DO_SHADOW:
                for p in shadowImagePoints:
                    cv2.circle(imgShadow, (p[0][0], p[0][1]), 1, (0, 0, 0), -1)
                imgShape = cv2.addWeighted(imgShape, (1 - transparency), imgShadow, transparency, 0)

            for p_ind in range(objectImagePoints.shape[0]):
                p = objectImagePoints[p_ind]
                p_color = int(objectColors[p_ind])
                cv2.circle(imgShape, (p[0][0], p[0][1]), 1, (p_color, p_color, p_color), -1)

            cv2.imshow("image with object and shadow", imgShape)
            cv2.imwrite(SAVE_ADDRESS, imgShape)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
