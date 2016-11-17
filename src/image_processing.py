from scipy import ndimage
from scipy import misc
import matplotlib.pyplot as plt
import numpy as np


#open image
face = misc.face()
misc.imsave('face.png', face) # uses the Image module (PIL)
plt.imshow(face)
plt.show()

#creating a numpy array so it is intercahangable with the gdal files

misc.imsave('face.png', face) # First we need to create the PNG file

face = misc.imread('face.png')
type(face)

face.shape, face.dtype
f = misc.face(gray=True) # greyscale



#http://www.scipy-lectures.org/advanced/image_processing/

#sobel filter (gradient/edge detector)

sx = ndimage.sobel(face, axis=0, mode='constant')
sy = ndimage.sobel(face, axis=1, mode='constant')
sob = np.hypot(sx, sy)

plt.imshow(sob)
plt.show()


#postprocess:
# Remove small white regions
open_img = ndimage.binary_opening(binary_img)
# Remove small black hole
close_img = ndimage.binary_closing(open_img)