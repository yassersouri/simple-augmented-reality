from utils import getCollectionPhotos, findChessBoardPoints
import cv2

def main():
    img1, img2, img3 = getCollectionPhotos(4)

    findChessBoardPoints(img1)

if __name__ == '__main__':
    main()
    