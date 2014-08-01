from loaders import getCollectionPhotos
import cv2

def main():
    img1, img2, img3 = getCollectionPhotos(4)

    print img1.shape
    
    cv2.imshow('t', img1)
    cv2.waitKey(0)

if __name__ == '__main__':
    main()
    