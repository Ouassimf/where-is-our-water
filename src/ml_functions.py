import numpy as np

import matplotlib.pyplot as plt

from osgeo import gdal
from sklearn import metrics


def feature_gen(img_as_array):

    #creature the second feature for the classifier. The average of the surrounding pixels

    xsize=img_as_array.shape[0]
    ysize=img_as_array.shape[1]
    new_file=np.zeros((xsize, ysize))

    for x in range (1,xsize-1):
        for y in range (1,ysize-1):
            buffer=0
            for i in range (-1,2):
                for j in range (-1,2):
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

#hardcoded file locations
raster_data_path = "../raw_data/data.tiff"
output_fname = "classification.tiff"
vector_data_path="../raw_data/label.tiff"


data=open_file(raster_data_path)
vector=open_file(vector_data_path)


new_file=feature_gen(data)
feature2 = split_histogram(new_file, 0, 70)

#bringing the data in shape for its big moment with the classifier
new_file=new_file.flatten()
feature2=feature2.flatten()
vector=vector.flatten()
X= merge_layers(new_file, feature2)
vector[vector <= 200] = 0
vector[vector > 200] = 1
X=X.T
y=vector

#pick classifier of choice
#classifier=classify_knn(X,y)
#classifier=classify_NN(X,y)
classifier=classify_SVM(X,y)

y_pred=evaluate(classifier, X,y)




predicted = y_pred.reshape(data.shape)

plt.imshow(predicted)
plt.show()
