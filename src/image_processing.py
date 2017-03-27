import ml_functions as ml
import numpy as np
import matplotlib.pyplot as plt
import time
from skimage import data, img_as_float
from skimage import exposure
from sklearn import metrics
from sklearn import preprocessing
from skimage import morphology
from skimage.morphology import disk
#necessary to tell the amounts of lakes:
from scipy import ndimage


#
# this file is still under construction, but cleans the image from dust and determines the number of connected water bodies in the image
#
#
#
# only value to modify is the minimum lake saze (how many pixels a lake has to have at least to be classified as one). This allows to remove the dust and all small water bodies
# For the Ballaton picture a value of 1500 results in a classification close to the one I would take naturally. Everything above 10 000 leaves only the biggest lakes
minlakepixel=1500



def cleanup(boolimage, minsize): #cleans the image from noise and too small water areas
    no_small = morphology.remove_small_objects(boolimage, min_size=minsize)
    cleanimage=morphology.binary_closing(no_small,disk(3))
    return cleanimage

def lakeamount(boolimage):   #measures the amount of lakes and their respective pixelnumber
    label_im, nb_labels = ndimage.label(boolimage)
    sizes = ndimage.sum(boolimage, label_im, range(nb_labels+1)) #Calculate the sum of the values of the array. If water has the value 1 it is also the nr of pixels

    return label_im, nb_labels, sizes #a numpy array with the labels of each lake, the number of labels and the amount of pixels of each


raster_data_path = "../raw_data/ballaton.tiff"
testfile = "../raw_data/seengruppesehrklein.tiff"
data=ml.open_file(raster_data_path)

dataeq=exposure.equalize_hist(data)


#turnes it into a boolean file
dataeq[dataeq <= 0.15] = 0
dataeq[dataeq > 0.15] = 1

bool = (dataeq<0.15)
file = bool.astype(int)

plt.figure(1)
plt.imshow(file, cmap="Greys")



bereinigt = cleanup(bool, minlakepixel)

plt.figure(2)
plt.imshow(bereinigt, cmap="Greys")





bool2 = (bereinigt>0.5)


labelimage, nroflakes, size = lakeamount(bool2)



sizes = ndimage.sum(bereinigt, labelimage, range(nroflakes+1))
print("Lakesizes:")
print(sizes)




cog = ndimage.measurements.center_of_mass(bool2, labelimage, (range(1, nroflakes+1)))
print(cog)
#plt.figure(4)
#plt.imshow(lbl2)


print("Es gibt so viele Seen: " + str(nroflakes))
plt.figure(3)
plt.imshow(labelimage)
for x in range(0,int(nroflakes)):
    plt.text(int(cog[x][1]), int(cog[x][0]), str(sizes[x+1]) + "px" ,  color='green', fontsize=12)


plt.show()
















