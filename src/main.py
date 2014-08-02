from utils import getCollectionPhotos, getPoints
import cv2

def main():
    COLLECTION_NUM = 4
    IMAGE_NUM = 1 # 1, 2 or 3
    
    imgs = getCollectionPhotos(COLLECTION_NUM, scale_down_factor=5)
    img = imgs[IMAGE_NUM - 1]
    
    done, points = getPoints(img, COLLECTION_NUM, IMAGE_NUM)
    
    print done
    print len(points)

if __name__ == '__main__':
    main()