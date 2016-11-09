import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage as ndi

import math
import gdal

import skimage
import skimage.io
import skimage.transform
import wow_get_imagery

import xml.etree.ElementTree as ET


def build_dataset_from_location(north_west_corner, south_east_corner):
    """Create a labeled dataset suitable for ML algoritjm from geo-coordinates"""

    # Retrieve latest Sentinel 1 / Landsat 8 imagery for the specified location
    dataset_raster = get_image_from_location(north_west_corner, south_east_corner)

    # Retrieve latest OSM(Open Street Map) Water Vector Map for specified location
    dataset_label = get_osm_water_vector_from_location(north_west_corner, south_east_corner)

    x_dataset, y_dataset = build_dataset_from_raster(dataset_label, dataset_raster, north_west_corner,
                                                     south_east_corner)
    return x_dataset, y_dataset


def get_corner_from_tiff(raster_image, corner_number):
    from osgeo import gdal
    ds = gdal.Open(raster_image)
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width * gt[4] + height * gt[5]
    maxx = gt[0] + width * gt[1] + height * gt[2]
    maxy = gt[3]
    if corner_number == 1:
        corner_coordinates = [maxy, minx]
    elif corner_number == 3:
        corner_coordinates = [miny, maxx]
    else:
        print("Unknown corner request. Only 1 and 3 acceptable")
        corner_coordinates = [0, 0]
    return corner_coordinates


def build_dataset_from_images(data_image, label_image):
    """Create a labeled dataset suitable for ML algoritjm from geo-coordinates"""

    # Retrieve data raster from file
    dataset_raster = get_array_from_tiff(data_image)

    # Retrieve label raster from file
    dataset_label = get_array_from_tiff(label_image)

    north_west_corner = get_corner_from_tiff(data_image, 1)
    south_east_corner = get_corner_from_tiff(data_image, 3)

    x_dataset, y_dataset = build_dataset_from_raster(dataset_label, dataset_raster, north_west_corner,
                                                     south_east_corner)
    return x_dataset, y_dataset


def build_dataset_from_raster(dataset_label, dataset_raster, north_west_corner, south_east_corner):
    # X Values of the dataset
    x_dataset = prepare_raster(dataset_raster)
    # Correct label values (usually 0 and 8200 but sometimes intermediary values appears)
    dataset_label[dataset_label <= 200] = 0
    dataset_label[dataset_label > 200] = 1
    # Y Values of the dataset
    # Flatten to rows the label
    y_dataset = dataset_label.flatten()
    # Cast from float to int
    y_dataset = y_dataset.astype(int)
    dataset_filename = '../datasets/dataset_' + str(north_west_corner) + '_' + str(south_east_corner) + '.out'
    dataset_full = np.column_stack((x_dataset, y_dataset))
    print("Saving dataset in " + dataset_filename)
    np.savetxt(dataset_filename, dataset_full, fmt='%1.0d', delimiter=',', newline='\n')
    print("done")
    return x_dataset, y_dataset


def add_sliding_windows_features(stack, edge):
    # Measure depth of stack
    depth = stack.shape[2]
    buff = math.floor(edge / 2)
    pad_width = ((buff, buff), (buff, buff), (0, 0))
    # Add edge/2 pixels on each side
    stack_paded = np.pad(stack, pad_width, mode='minimum')
    # Create an array with the sliding window features
    stack_window = skimage.util.view_as_windows(stack_paded, window_shape=(edge, edge, depth), step=1)
    return stack_window


def get_image_from_location(north_west_corner, south_east_corner):
    c_1 = str(north_west_corner[1]) + ' ' + str(north_west_corner[0])
    c_2 = str(south_east_corner[1]) + ' ' + str(north_west_corner[0])
    c_3 = str(south_east_corner[1]) + ' ' + str(south_east_corner[0])
    c_4 = str(north_west_corner[1]) + ' ' + str(south_east_corner[0])
    c_5 = c_1
    polygon = "POLYGON((" + c_1 + ',' + c_2 + ',' + c_3 + ',' + c_4 + ',' + c_5 + '))'
    print(polygon)
    print(wow_get_imagery.loc)
    product_list = wow_get_imagery.get_product_list_by_time_location('1', polygon)
    # print(product_list)
    tree = ET.ElementTree(ET.fromstring(product_list))
    root = tree.getroot()
    node = root.find('{http://www.w3.org/2005/Atom}entry')
    uuid = node.find('{http://www.w3.org/2005/Atom}id').text
    print(uuid)
    wow_get_imagery.download_product_quick_look(uuid)
    wow_get_imagery.download_product_tiff(uuid)
    return get_array_from_tiff('data_1000.tiff')


def get_osm_water_vector_from_location(north_west_corner, edge_size, target_resolution):
    return get_array_from_tiff('lab_1000.tiff')


def predict_classification(image_array, classifier):
    print('Will predict')
    predictions = classifier.predict(prepare_raster(image_array))
    labels_predicted = predictions.reshape(image_array.shape)
    return labels_predicted


def get_gaussian_contour(dataset_raster):
    sigma = 20
    dog = dataset_raster - ndi.gaussian_filter(dataset_raster, sigma)

    return dog


def prepare_raster(dataset_raster):
    # Create a Gradient Contouring Image from the raster
    dataset_raster_dog = get_gaussian_contour(dataset_raster)

    # Stack the original raster with gradient contour raster. This adds one more feature to each pixel
    dataset_stack = np.dstack((dataset_raster, dataset_raster_dog))

    # Adding for each pixel the surrounding n pixel's information as features through a sliding windows.
    window_edge = 3
    stack_window = add_sliding_windows_features(dataset_stack, window_edge)

    # Flatten raster stack to a n*features matrix with n being the amount of pixels
    depth = dataset_stack.shape[2]
    stack_flat = stack_window.reshape(-1, window_edge * window_edge * depth)
    return stack_flat


def get_array_from_tiff(filename):
    gdal.AllRegister()
    file = filename
    ds = gdal.Open(file)
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()
    return data


def classify_and_display_raster(raster_file, rf):
    fig = plt.figure()
    data = get_array_from_tiff(raster_file)
    fig.add_subplot(2, 1, 1)
    plt.imshow(data, cmap='hot')
    fig.add_subplot(2, 1, 2)
    plt.imshow(predict_classification(data, rf), cmap='hot')
    plt.show()
    plt.pause(0.0001)
