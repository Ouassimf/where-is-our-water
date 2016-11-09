import glob

import time

import wow_functions as wf
import sys


def get_datasets():
    file_list = glob.glob('../datasets/dataset_*')
    return file_list


def create_dataset_from_images():
    data_image = input("Path of data image\n")
    label_image = input("Path of label image\n")
    wf.build_dataset_from_images(data_image, label_image)


def create_dataset_from_geolocation():
    pass


def get_ml_statistics():
    pass


def create_classifier():
    pass


def train_classifier():
    pass


def compile_all_datasets():
    file_list = get_datasets()
    out_file = '../datasets/compiled_dataset_' + time.strftime("%d_%m_%Y_%H_%M")
    with open(out_file, 'w') as outfile:
        for fname in file_list:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)
    print("Datasets compiled and saved as " + out_file)
    pass


def launch_mode(mode):
    if mode == 1:
        print("Entering dataset creation from images")
        create_dataset_from_images()
    elif mode == 2:
        print("Entering dataset creation from geo-coordinates")
        create_dataset_from_geolocation()
    elif mode == 3:
        print("Compiling...")
        compile_all_datasets()
    elif mode == 4:
        print("Entering classifier training")
        train_classifier()
    elif mode == 5:
        print("Entering classifier creation")
        create_classifier()
    elif mode == 6:
        print("Entering statistics")
        get_ml_statistics()
    elif mode == 9:
        print("Quitting")
        sys.exit()
    else:
        print("Your choice was not recognized.\n Please retry")


def main():
    while True:
        print("*" * 40)
        print(" " * 13 + "TRAINING MODE")
        print("*" * 40)
        print("Currently " + str(len(get_datasets())) + " datasets ready for use")
        print("Please choose an action : ")
        print("1. Generate dataset from raster and label image")
        print("2. Generate dataset from geo-coordinates")
        print("3. Compile all available datasets in one file")
        print("4. Train an existing classifier")
        print("5. Create a new classifier")
        print("6. Get statistics about datasets and classifiers")
        print("9. Quit")
        try:
            exec_mode = int(input("Please choose an action\n"))
            launch_mode(exec_mode)
        except ValueError:
            print("Your choice was not recognized.\n Please retry")
