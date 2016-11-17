import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from osgeo import gdal
from sklearn import metrics
import _compat_pickle
from scipy import misc


def feature_gen(img_as_array):

    #creature the second feature for the classifier. The average of the surrounding pixels

    xsize=img_as_array.shape[0]
    ysize=img_as_array.shape[1]
    new_file=np.zeros((xsize, ysize))

    #kernel size (1=3x3, 2=5x5, 3=7x7
    sz=2

    for x in range (sz,xsize-sz):
        for y in range (sz,ysize-sz):
            buffer=0
            for i in range (-sz,sz+1):
                for j in range (-sz,sz+1):
                    buffer+=img_as_array[x+i,y+j]
            new_file[x,y] = buffer/9


    return new_file

def show_on_same_image(first, second, third, fourth):

    #function that shows multiple images at once for simle debugging.
    #NOT USED

    fig = plt.figure()
    a=fig.add_subplot(221)
    a.set_title("original")
    plt.hist(first)


    a=fig.add_subplot(222)
    a.set_title("averaged")
    plt.imshow(second)

    a=fig.add_subplot(223)
    a.set_title("first threshold")
    plt.imshow(third)

    a=fig.add_subplot(224)
    a.set_title("second threshold")
    plt.imshow(fourth)

    plt.show()

def split_histogram(input, thresholdlower, thresholdupper):
    #deleting the brighnessvalues outside of a specified scope
    array=np.copy(input)
    array[array < thresholdlower] = 0
    array[array > thresholdupper] = 0
    return array

def open_file(file):
    #opens geotiffs
    gdal.AllRegister()
    ds = gdal.Open(file)
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()
    return data

def merge_layers(l1, l2):
    #idk why I made a function out of this command^^
    X= np.vstack((l1,l2))
    return X

def classify_knn(X,y):
    from sklearn.neighbors import KNeighborsClassifier

    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X, y)
    return knn

def classify_NN(X,y):
    from sklearn.neural_network import MLPClassifier

    NN = MLPClassifier(alpha=1)
    NN.fit(X, y)
    return NN

def classify_SVM(X,y):
    from sklearn.svm import SVC

    svm = SVC(gamma=2, C=1)
    svm.fit(X, y)
    return svm


def evaluate (classifier, X, y):
    y_pred = classifier.predict(X)
    print(metrics.accuracy_score(y, y_pred))
    print(metrics.classification_report(y, y_pred))
    #will be extended with  confusion matrix, AUC and so on
    return y_pred

def save_classifier(cf):
    #should be extended with classifiername
    with open('classifier.pkl', 'wb') as fid:
        _compat_pickle.dump(gnb, fid)

def load_classifier():
    #should be extended with classifiername
    with open('classifier.pkl', 'wb') as fid:
        gnb_loaded = _compat_pickle.load(fid)
    return gnb_loaded

def show_feature(X,y):
    Z = merge_layers(X, y)
    # Ugly way to sort the Array by the label -.-
    F = np.argsort(Z[2, :])
    Y = Z[:, F]
    till=Y.shape[1]
    sep = np.asarray(np.nonzero(Y[2, :]))[0, 1]
    #Actually the naming is exactly wrong
    Water = Y[:, 0:sep - 1]
    Now = Y[:, sep:till]
    plt.plot(Water[0], Water[1], 'rx', Now[0], Now[1], 'b^')
    plt.xlabel('feature 1 - [5x5] Kernel')
    plt.ylabel('feature 2 - sobel edge detector')
    plt.xlim(0, 600)
    red_patch = mpatches.Patch(color='red', label='Land')
    blue_patch = mpatches.Patch(color='blue', label='Water')
    plt.legend(handles=[blue_patch, red_patch])
    plt.show()
    percentage=100-((sep/till)*100)
    print (str(percentage) + "% of all pixels in the image are water. starting from" + str(sep))


#hardcoded file locations
raster_data_path = "../raw_data/data.tiff"
output_fname = "classification.tiff"
vector_data_path="../raw_data/label.tiff"


data=open_file(raster_data_path)
vector=open_file(vector_data_path)
new_file=feature_gen(data)

plt.hist(new_file)
plt.show()

#bei 3er Kernel is 75 der splitwert
feature2 = split_histogram(new_file, 0, 130)

plt.imshow(feature2)
plt.show()

#bringing the data in shape for its big moment with the classifier
data=data.flatten()
feature2=feature2.flatten()
vector=vector.flatten()
X= merge_layers(data, feature2)
vector[vector <= 200] = 0
vector[vector > 200] = 1
#X=X.T
y=vector

sx = ndimage.sobel(new_file, axis=0, mode='constant')
sy = ndimage.sobel(new_file, axis=1, mode='constant')
sob = np.hypot(sx, sy)


sob2=split_histogram(sob, 0, 235)

sx = ndimage.sobel(sob2, axis=0, mode='constant')
sy = ndimage.sobel(sob2, axis=1, mode='constant')
sob3 = np.hypot(sx, sy)

sob3=split_histogram(sob3, 0, 250)


sob3=sob3.flatten()
Z=merge_layers(feature2, sob3)
show_feature(Z,y)


#show_feature(X,y)

#pick classifier of choice (SVW is too comp expensivefor my pc)
#classifier=classify_knn(X,y)
#classifier=classify_NN(X,y)
#classifier=classify_SVM(X,y)
#save_classifier(classifier)
#classifier=load_classifier()
# y_pred=evaluate(classifier, X,y)
#
#
# predicted = y_pred.reshape(data.shape)
#
# plt.imshow(predicted)
# plt.show()
