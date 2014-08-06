import cv2
import os
import glob
import numpy as np
import geomhelper

CURRENT_FILE = os.path.realpath(__file__)
SRC_FOLDER = os.path.dirname(CURRENT_FILE)
ROOT_FOLDER = os.path.dirname(SRC_FOLDER)
DATA_FOLDER_NAME = 'data'
POINTS_FOLDER_NAME = 'points'
RESULTS_FOLDER_NAME = 'results'
DATA_FOLDER = os.path.join(ROOT_FOLDER, DATA_FOLDER_NAME)
POINTS_FOLDER = os.path.join(ROOT_FOLDER, POINTS_FOLDER_NAME)
RESULTS_FOLDER = os.path.join(ROOT_FOLDER, RESULTS_FOLDER_NAME)
IMG_FILE_EXTENSION = '.JPG'
PTS_FILE_EXTENSION = '.pts.npy'

color1 = (0, 0, 255)
color2 = (55, 160, 255)
color3 = (70, 225, 255)
color4 = (0, 255, 0)
color5 = (255, 0, 0)
color6 = (225, 70, 255)
color7 = (160, 255, 55)

COLOR = [color1, color2, color3, color4, color5, color6, color7]

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

global points


def get_save_address(COLLECTION_NUM, IMAGE_NUM, DO_COLOR, SMOOTHING):
    collection_results_folder = os.path.join(RESULTS_FOLDER, str(COLLECTION_NUM));
    if not os.path.exists(collection_results_folder):
        os.makedirs(collection_results_folder)
    
    name = "%d-color:%s-smoothing:%s%s" % (IMAGE_NUM, str(DO_COLOR), str(SMOOTHING), IMG_FILE_EXTENSION)
    
    return os.path.join(collection_results_folder, name)


def loadPLY(fileAddress=None):
    if fileAddress is None:
        fileAddress = os.path.join(DATA_FOLDER, "parasaurolophus_high.ply")

    vertices = 0
    faces = 0

    vertex_len = 0
    face_len = 0

    vertex_ind = 0
    face_ind = 0

    mode = 'h'  # h: parsing headers, v: vertex list, f: face list

    with open(fileAddress, 'r') as infile:
        for line in infile:
            parts = line.split(' ')
            if mode == 'h':
                if len(parts) == 3:
                    if parts[0] == "element":
                        if parts[1] == "vertex":
                            vertex_len = int(parts[2])
                        if parts[1] == "face":
                            face_len = int(parts[2])
                    continue
                if len(parts) == 1:
                    if parts[0].strip() == "end_header":
                        mode = 'v'
                        # initialize vertices with empty arrays
                        vertices = np.zeros((vertex_len, 3), dtype=np.float32)
                        faces = [[] for x in xrange(vertex_len)]
                        continue
            if mode == 'v':
                if vertex_ind == vertex_len:
                    mode = 'f'
                else:
                    # parse vertex
                    x = float(parts[0])
                    y = float(parts[1])
                    z = float(parts[2])
                    vertices[vertex_ind] = [x, y, z]
                    vertex_ind += 1
            if mode == 'f':
                if face_ind == face_len:
                    print 'What is wrong?'
                else:
                    # parse face
                    _1 = int(parts[1])
                    _2 = int(parts[2])
                    _3 = int(parts[3])

                    tu = (_1, _2, _3)

                    faces[_1].append(tu)
                    faces[_2].append(tu)
                    faces[_3].append(tu)

                    face_ind += 1

    return vertices, faces

def refine_vertices(vertices, z_scale):
    means = vertices.mean(axis = 0)
    vertices = vertices - means
    vertices[:, [0, 1, 2]] = vertices[:, [2, 1, 0]]
    vertices = vertices + means
    
    vertices[:, 0] = vertices[:, 0] - vertices[:, 0].min()
    vertices[:, 1] = vertices[:, 1] - vertices[:, 1].min()
    vertices[:, 2] = vertices[:, 2] - vertices[:, 2].min()
    vertices = vertices / 2
    
    vertices[:, 2] = vertices[:, 2] / z_scale
    
    return vertices

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


def getPoints(img, COLLECTION_NUM, IMAGE_NUM, M, N):
    global points

    imgO = img
    gray = cv2.cvtColor(imgO, cv2.COLOR_BGR2GRAY)

    PTS_COLLECTION_PATH = os.path.join(POINTS_FOLDER, str(COLLECTION_NUM))
    
    # create directory if not exists
    if not os.path.exists(PTS_COLLECTION_PATH):
        os.makedirs(PTS_COLLECTION_PATH)
    pts_file_name = os.path.join(PTS_COLLECTION_PATH, str(IMAGE_NUM) + PTS_FILE_EXTENSION)
    files = glob.glob(pts_file_name)

    WINDOW_NAME = "get points"
    points = []

    def draw_points(imgO, radius=4, thickness=2):
        global points

        imgD = np.copy(imgO)
        i = 0
        for point in points:
            cv2.circle(imgD, tuple(point), radius, COLOR[(i/M) % len(COLOR)], thickness)
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


def prepareObjectPoints(M, N, scale=1):
    objp = np.zeros((M*N, 3), np.float32)
    objp[:, :2] = np.mgrid[0:M, 0:N].T.reshape(-1, 2)
    
    objp = objp * scale
    
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


def draw3DAxisLines(img, origin, imgPoints):
    corner = tuple(origin.ravel())
    cv2.line(img, corner, tuple(imgPoints[0].ravel()), (255, 0, 0), 5)
    cv2.line(img, corner, tuple(imgPoints[1].ravel()), (0, 255, 0), 5)
    cv2.line(img, corner, tuple(imgPoints[2].ravel()), (0, 0, 255), 5)
    return img


def calculate_shadow(vertices, l, do_shadow=True):
    ground_plane = geomhelper.Plane([0, 0, 1], 0)
    shadow_points = np.zeros_like(vertices, np.float32)
    
    if not do_shadow:
        return shadow_points
    
    for v_num in range(vertices.shape[0]):
        l0 = vertices[v_num].tolist()
        line = geomhelper.Line(l0, l)
        shadow_points[v_num] = ground_plane.interset_line(line)
    
    return shadow_points


def calculate_colors(vertices, faces, l, do_colors=True, smoothing=False):
    objectColors = np.ones(vertices.shape[0], dtype=np.uint8) * 255
    
    if not do_colors:
        return objectColors
    
    for v_ind in range(vertices.shape[0]):
        current_faces = faces[v_ind]
        face = current_faces[0]
        a = vertices[face[0], :]
        b = vertices[face[1], :]
        c = vertices[face[2], :]
        n_mean = geomhelper.Plane.plane_normal_from_three_points(a, b, c)
        
        objectColors[v_ind] = 255 * (-1 * geomhelper.dot(n_mean, l) + 1)
    
    # now lets do smoothing
    if smoothing:
        for v_ind in range(vertices.shape[0]):
            current_faces = faces[v_ind]
            color_sum = 0
            for face in current_faces:
                color_sum += objectColors[list(face)].mean()
            objectColors[v_ind] = int(float(color_sum)/len(current_faces))

    return objectColors


if __name__ == '__main__':
    vertices, faces = loadPLY()
    print "finished"
