import ml_functions as ml
import numpy as np
import matplotlib.pyplot as plt
import time

from skimage import data, img_as_float
from skimage import exposure

from sklearn import metrics


from sklearn import preprocessing
#Die brauch ich zum saubermachen und einstellen wie klein die kleinsten seen sein sollen
from skimage import morphology
from skimage.morphology import disk

#Seenanzahl bestimmen:
from scipy import ndimage



def cleanup(boolimage, minsize): #cleans the image from noise and too small water areas
    no_small = morphology.remove_small_objects(boolimage, min_size=minsize)
    cleanimage=morphology.binary_closing(no_small,disk(3))
    return cleanimage

def lakeamount(boolimage):
    label_im, nb_labels = ndimage.label(boolimage)
    sizes = ndimage.sum(boolimage, label_im, range(nb_labels+1)) #Calculate the sum of the values of the array. If water has the value 1 it is also the nr of pixels

    return label_im, nb_labels, sizes #a numpy array with the labels of each lake, the number of labels and the amount of pixels of each








raster_data_path = "../raw_data/ballaton.tiff"
testfile = "../raw_data/seengruppesehrklein.tiff"
testlabel = "../raw_data/ballabelV3.tif"
data=ml.open_file(raster_data_path)
label=ml.open_file(testlabel)


dataeq=exposure.equalize_hist(data)



dataeq[dataeq <= 0.15] = 0
dataeq[dataeq > 0.15] = 1

bool = (dataeq<0.15)
file = bool.astype(int)

plt.figure(1)
plt.imshow(file, cmap="Greys")



bereinigt = cleanup(bool, 1500)

#plt.figure(2)
#plt.imshow(bereinigt, cmap="Greys")





bool2 = (bereinigt>0.5)


labelimage, nroflakes, size = lakeamount(bool2)



sizes = ndimage.sum(bool2, labelimage, range(nroflakes+1))
print("hier kommen die Seegröß:!")
print(sizes)




cog = ndimage.measurements.center_of_mass(bool2, labelimage, (1,2,3,4,5,6,7,8,9,10,11,12))
print(cog)
#plt.figure(4)
#plt.imshow(lbl2)


print("Es gibt so viele Seen: " + str(nroflakes))
plt.figure(3)
plt.imshow(labelimage)
for x in range(0,12):               #change range to number of labels
    plt.text(int(cog[x][1]), int(cog[x][0]), str(sizes[x+1]) + "px" ,  color='green', fontsize=12)


plt.show()
















