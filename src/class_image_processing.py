from skimage import morphology
from skimage.morphology import disk
from scipy import ndimage


class Image_Processing:
# this class cleans the image from dust and determines the number of connected water bodies in the image


    def cleanup(boolimage, minsize):
        #cleans the image from noise and too small water areas
        #minsize is the amount of pixels, the smalles lake should have
        no_small = morphology.remove_small_objects(boolimage, min_size=minsize)
        cleanimage=morphology.binary_closing(no_small,disk(3))
        return cleanimage

    def lakeamount(boolimage):   #measures the amount of lakes and their respective pixelnumber
        label_im, nb_labels = ndimage.label(boolimage)
        sizes = ndimage.sum(boolimage, label_im, range(nb_labels+1)) #Calculate the sum of the values of the array. If water has the value 1 it is also the nr of pixels

        return label_im, nb_labels, sizes #returns a numpy array with the labels of each lake, the number of labels and the amount of pixels of each












