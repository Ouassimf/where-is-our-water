import ml_functions as ml
import time
import numpy as np
from sklearn import metrics
#for the histogram equalisation:
from skimage import exposure

start_time=time.time()
gesamt=start_time



#raster_data_path = "../raw_data/data.tiff"
#vector_data_path="../raw_data/label.tiff"
#testfile= "../raw_data/seengruppeklein.tiff"
#testfile = "../raw_data/ballaton.tiff"
#label = "../raw_data/labelballaton.tiff"
#label2 = "../raw_data/labellballatonopenstreetmap.tif"
#see= "../raw_data/seengruppesehrklein.tiff"


A=2 #one states that NS is the training data   at each swich change the file in the multiplier and the range for the layer
if A==1:
    print("Neusiedlersee is Training data")
    raster_data_path = "../raw_data/data.tiff"
    vector_data_path= "../raw_data/label.tiff"
    testfile = "../raw_data/ballaton.tiff"
    testlabel = "../raw_data/ballabelV3.tif"
else:
    print("Balaton is Training data")
    raster_data_path = "../raw_data/ballaton.tiff"
    vector_data_path= "../raw_data/ballabelV3.tif"
    testfile = "../raw_data/data.tiff"
    testlabel = "../raw_data/label.tiff"



data=ml.open_file(raster_data_path)
vector=ml.open_file(vector_data_path)
testdata1=ml.open_file(testfile)
testvector=ml.open_file(testlabel)
print("Opening took " + str((time.time()-start_time)) + " seconds")
start_time=time.time()


#histogram equalization:
testdata = exposure.equalize_hist(testdata1)
testdata=np.multiply(testdata,10000)
data = exposure.equalize_hist(data)
data=np.multiply(data,10000)



#second feature is generated (each pixel value is the average of its surrounding) (smaller kernel makes it much faster)
#kernel size  ksize (1=3x3, 2=5x5, 3=7x7)
ksize=1
new_file=ml.feature_gen(data, ksize)

print("featuregeneration takes " + str((time.time()-start_time)) + " seconds")
start_time=time.time()


#preparing files for the classifier
dd=new_file.flatten()
datas=data.flatten()
tdata=testdata.flatten()
vector = vector.flatten()

#creating a boolean vector file
vector[vector <= 200] = 0
vector[vector > 200] = 1
y=(vector>0.5).astype(int)


X = ml.merge_layers(datas, dd)
X=X.T
print("classifier begins, " + str((time.time()-start_time)) + " seconds")
start_time=time.time()


#various classification processes can be tried here, knn shows the best results
classifier=ml.classify_knn(X,y)
print("Classifier ends after, " + str((time.time()-start_time)) + " seconds")
start_time=time.time()

#y_pred = classifier.predict(X)                      #the training file gets predicted (should be close to 100%)

print("prediction1 done after, " + str((time.time()-start_time)) + " seconds")
start_time=time.time()


#predicted = y_pred.reshape(data.shape)



tdata2=ml.feature_gen(testdata, ksize)
print("feature generation took " + str((time.time()-start_time)) + " seconds")
start_time=time.time()

tdata2=tdata2.flatten()
Z=ml.merge_layers(tdata, tdata2)
Z=Z.T


y_pred = classifier.predict(Z)                      #the testfile gets predicted
print("prediction 2 took " + str((time.time()-start_time)) + " seconds")


#reshape the prediction into the image shape
predicted2 = y_pred.reshape(testdata.shape)

#postprocessing the image to reduce artifacts (dust)
postproc = ml.image_posp_proc(predicted2)


f1=data
f2=testdata


print("Total time:")
print(time.time()-gesamt)


#prediction metrics
dump2=testvector.flatten()
print(metrics.accuracy_score(dump2, y_pred))
print(metrics.classification_report(dump2, y_pred))

#prediction metrics after post processing the image

print("After postprocessing:")
ypredpro=postproc.flatten()

print(metrics.accuracy_score(dump2, ypredpro))
print(metrics.classification_report(dump2, ypredpro))


ml.show_on_same_image2(f1, f2, predicted2, postproc, "testdata", "trainingdata", "KNN predicted", "postprocessed")















