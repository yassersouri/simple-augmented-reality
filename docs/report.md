# ACV Project Report

Yasser Souri - 92204744 - <ysouri@ce.sharif.edu>

## Code

Code is written using `python 2.7` programming language and `opencv 2.4.9` library.

## Steps

In this section I will describe the steps necessary for adding the object virtually to the scene:

__Camera Calibration__: We use one of the chess boards for calibration. User must first select a $M$ by $N$ set of points (usually 8 by 7) in the chessboard. The first point is chosen as origin. And a 

![Example of points selected](/Users/yasser/sharif-repo/sam/docs/assets/points.png)

![Example of world coordinate frame](/Users/yasser/sharif-repo/sam/docs/assets/frame.png)

Camera calibration is done using the opencv's functions. The output of camera calibration is all the intrinsic and extrinsic camera parameters, plus the distortion coefficients.

__Augmented Reality__: We now have the projection matrix. All we need to do is to add the object to the scene. Here we use the values of _vertex_s as world points and by multiplying it with the projection matrix, we can get the image point for that point in the object.

![Object Added as white pixels](/Users/yasser/sharif-repo/sam/docs/assets/white_points.png)

__Adding shadow__: First we define a parametric line $l$ that specifies the direction of light. Then for each object point loaded from _PLY_ file, we pass a line with the same slope from it and find the intersection with the group plane ($z=0$). The intersection of line and plane is the point of shadow. We then use the _faces_ that was included with the _PLY_ file to add small shadow to the body of the object. Each _face_ is a set of 3 vertexes. With 3 vertexes, we can find the normal vector of a plane containing those 3 vertexes. By comparing this normal vector, with the slope vector of the light line, we can find a measure of how light should a pixel be. Then by smoothing these values we can get a better response

![Object added with shadows](/Users/yasser/sharif-repo/sam/docs/assets/shadows.png)

![Another object added with shadows](/Users/yasser/sharif-repo/sam/docs/assets/shadows2.png)

## Automating the point selection

I have not been able to completely do this, but the point selection process is intelligent. It is sufficient to click near a point, not necessarily on it. The program will automatically search nearby area in the image for corner like points. This is actually a lot of help.

## Issues

__Calibration__: The calibration method that I have used is actually very sensitive to noise in points selected in the image. But in the dataset, the chessboard is sometimes not straight, and this causes problem for my method. Specially the chessboard on the ground is very wavy. This is the reason that I've chosen other surfaces some of the times.

__Shadows__: The reasoning about shadow in my program is very naive. For example one must detect if the path of light to a point in the world is blocked by other points. This currently is not implemented.

__Runtime Efficiency__: The algorithm is actually slow. For one thing this is implemented using `python`, but other than that, the algorithm itself might not be the fastest.

## Final Results

Here are a collection of final results. As you might have notices, since the calibration method chosen needs between 30 to 60 points to produce meaningful results, I have not tested on the colored chessboard.

### Dataset 3

![Dataset: 3, Image: 1](/Users/yasser/sharif-repo/sam/results/3/1-color:True-smoothing:True.JPG)

![Dataset: 3, Image: 2](/Users/yasser/sharif-repo/sam/results/3/2-color:True-smoothing:True.JPG)

![Dataset: 3, Image: 3](/Users/yasser/sharif-repo/sam/results/3/3-color:True-smoothing:True.JPG)

\pagebreak

### Dataset 4

![Dataset: 4, Image: 1](/Users/yasser/sharif-repo/sam/results/4/1-color:True-smoothing:True.JPG)

![Dataset: 4, Image: 2](/Users/yasser/sharif-repo/sam/results/4/2-color:True-smoothing:True.JPG)

![Dataset: 4, Image: 3](/Users/yasser/sharif-repo/sam/results/4/3-color:True-smoothing:True.JPG)

\pagebreak

### Dataset 6

![Dataset: 6, Image: 1](/Users/yasser/sharif-repo/sam/results/6/1-color:True-smoothing:True.JPG)

![Dataset: 6, Image: 2](/Users/yasser/sharif-repo/sam/results/6/2-color:True-smoothing:True.JPG)

![Dataset: 6, Image: 3](/Users/yasser/sharif-repo/sam/results/6/3-color:True-smoothing:True.JPG)

\pagebreak

### Dataset 7

![Dataset: 7, Image: 1](/Users/yasser/sharif-repo/sam/results/7/1-color:True-smoothing:True.JPG)

![Dataset: 7, Image: 2](/Users/yasser/sharif-repo/sam/results/7/2-color:True-smoothing:True.JPG)

![Dataset: 7, Image: 3](/Users/yasser/sharif-repo/sam/results/7/3-color:True-smoothing:True.JPG)

\pagebreak