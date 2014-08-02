from utils import getCollectionPhotos, getPoints, M, N, calculateReprojectionError
from utils import prepareImagePoints, prepareObjectPoints
import cv2

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
            imgPoints = prepareImagePoints(points)
            objPoints = prepareObjectPoints()
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, (img.shape[0], img.shape[1]), None, None)
            calculateReprojectionError(objPoints, imgPoints, rvecs, tvecs, mtx, dist)
            
            
            

if __name__ == '__main__':
    main()