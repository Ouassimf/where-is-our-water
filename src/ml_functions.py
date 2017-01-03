import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from osgeo import gdal
from sklearn import metrics
import _compat_pickle
from scipy import misc
from skimage import exposure

def image_posp_proc(array):

    #Tweaking possibility
    th=0.98  # value between 0 and 1. How close has the average to be to a initial water guess (1) to be still considered as water?

    proc1=feature_gen(array)  #averaging to reduce the noise
    #now the file is not binary anymore

    bool2 = (proc1>th)
    output = bool2.astype(int)

    return output



def feature_gen(img_as_array):

    #creature the second feature for the classifier. The average of the surrounding pixels

    xsize=img_as_array.shape[0]
    ysize=img_as_array.shape[1]
    new_file=np.zeros((xsize, ysize))

    #kernel size (1=3x3, 2=5x5, 3=7x7
    sz=3

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
    a.set_title("training file")
    #plt.imshow(first, cmap="Greys", vmin=0, vmax=255)
    plt.imshow(first, cmap="Greys")


    a=fig.add_subplot(222)
    a.set_title("test file")
    plt.imshow(second, cmap="Greys")

    a=fig.add_subplot(223)
    a.set_title("prediction NN")
    plt.imshow(third, cmap="Greys")

    a=fig.add_subplot(224)
    a.set_title("prediction NN")
    plt.imshow(fourth, cmap="Greys")
    plt.show()

def show_on_same_image2(first, second, third, fourth, l1, l2, l3, l4):

    #function that shows multiple images at once for simle debugging.
    #NOT USED


    fig = plt.figure()
    a=fig.add_subplot(221)
    a.set_title(l1)
    #plt.imshow(first, cmap="Greys", vmin=0, vmax=255)
    plt.imshow(first, cmap="Greys")


    a=fig.add_subplot(222)
    a.set_title(l2)
    plt.imshow(second, cmap="Greys")

    a=fig.add_subplot(223)
    a.set_title(l3)
    plt.imshow(third, cmap="Greys")

    a=fig.add_subplot(224)
    a.set_title(l4)
    plt.imshow(fourth, cmap="Greys")
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
    print (str(percentage) + "% of all pixels in the image are water. From " + str(sep) + " till " + str(till) + ". So " + str(till-sep) + " in total!")

def sobel(file):
    sx = ndimage.sobel(file, axis=0, mode='constant')
    sy = ndimage.sobel(file, axis=1, mode='constant')
    sob = np.hypot(sx, sy)


    #es warn 235 und 250
    sob = split_histogram(sob, 50000, 80000)



    sx2 = ndimage.sobel(sob, axis=0, mode='constant')
    sy2 = ndimage.sobel(sob, axis=1, mode='constant')
    sob2 = np.hypot(sx2, sy2)


    #sob2 = split_histogram(sob2, 0, 200)



    return sob2

def visualize3D(f1,f2,f3, y):

    from mpl_toolkits.mplot3d import Axes3D, axes3d
    figure = plt.figure()
    ax=Axes3D(figure, azim=-26)
    ax.scatter(f3, f2, f1, c=y)
    ax.set_zlabel("raw pixel brightness")
    ax.set_ylabel("[5x5] kernel")
    ax.set_xlabel("double sobel")
    plt.show()

def dasrenntimmer():
    # hardcoded file locations
    raster_data_path = "../raw_data/data.tiff"
    output_fname = "classification.tiff"
    vector_data_path = "../raw_data/label.tiff"
    testfile = "../raw_data/seengruppe.tiff"

    data = open_file(raster_data_path)
    vector = open_file(vector_data_path)
    testdata = open_file(testfile)
    new_file = feature_gen(data)

    # bei 3er Kernel is 75 der splitwert
    feature2 = split_histogram(new_file, 0, 130)

    feauture_sobel = sobel(data)
    feauture_sobel = feauture_sobel.flatten()
    testdata = testdata.flatten()

    # bringing the data in shape for its big moment with the classifier
    data = data.flatten()
    feature2 = feature2.flatten()
    vector = vector.flatten()
    X = merge_layers(feauture_sobel, feature2)
    vector[vector <= 200] = 0
    vector[vector > 200] = 1

    y = vector

    show_feature(X, y)

    # visualize3D(split_histogram(data, 0, 400), feature2, feauture_sobel, y)

    # show_feature(X,y)
    X = X.T
    # pick classifier of choice (SVW is too comp expensivefor my pc)
    classifier = classify_knn(X, y)
    # classifier=classify_NN(A.T,y)
    # classifier=classify_SVM(X,y)
    # there are still isues to save and load it
    # save_classifier(classifier)
    # classifier=load_classifier()
    print("hier bin ich")
    oo = open_file(testfile)
    f2 = feature_gen(oo)
    f2 = split_histogram(f2, 0, 130)
    f2 = f2.flatten()
    f3 = sobel(oo)
    f3 = f3.flatten()
    F = merge_layers(f3, f2)
    m = open_file(testfile)

    # y_pred=evaluate(classifier, XX,y)
    #
    #
    y_pred = classifier.predict(F)

    predicted = y_pred.reshape(m.shape)
    #
    plt.imshow(predicted)
    plt.title("KNN classifier, trained on Neusiedlersee, n=5")
    plt.show()

