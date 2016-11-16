import logging
import os
import requests
import shutil

import sys

import settings as stgs
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ETree


class ProviderImagery:
    """Class for manipulating imagery from Sentinel Sat"""

    def __init__(self, source, uuid, name=None, acquisition_time=None, gml_coordinates=None, tiff_files=None):
        # source is either "C" or "L" for respectively Copernicus/Landsat
        self.downloaded_files = []
        self.source = source
        # unique identifier from the imagery provider.
        self.uuid = uuid
        self.name = name
        # array of 2 strings start & stop [ 2016-10-20T05:09:39.423958 , 2016-10-20T05:10:04.423161]
        self.acquisition_time = acquisition_time
        self.gml_coordinates = gml_coordinates
        self.tiff_files = tiff_files

    def download_quicklook(self):
        self.set_name()
        product_name = self.name + '.SAFE'
        url = stgs.COP_BASE_URL + "/Products('%s')/Nodes('%s')/Nodes('preview')/Nodes('quick-look.png')/$value" % (
            self.uuid, product_name)
        response = requests.get(url, auth=HTTPBasicAuth(stgs.COP_USERNAME, stgs.COP_PASSWORD))
        filename = "../raw_data/" + self.uuid + "/" + self.uuid + ".png"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(response.content)
        return response

    def download_manifest(self):
        self.set_name()
        product_name = self.name + '.SAFE'
        url = stgs.COP_BASE_URL + "/Products('%s')/Nodes('%s')/Nodes('manifest.safe')/$value" % (
            self.uuid, product_name)
        response = requests.get(url, auth=HTTPBasicAuth(stgs.COP_USERNAME, stgs.COP_PASSWORD))
        filename = "../raw_data/" + self.uuid + "/" + self.uuid + ".xml"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(response.content)

        self.populate_information(response.content)

        return response.content

    def populate_information(self, xml_string):
        tree = ETree.ElementTree(ETree.fromstring(xml_string))
        root = tree.getroot()
        self.tiff_files = []
        self.acquisition_time = []
        for element in root.findall(".//dataObject[@repID='s1Level1MeasurementSchema']"):
            full = element.find('byteStream/fileLocation').attrib['href']
            path, file = os.path.split(full)
            self.tiff_files.append(file)

        for element in tree.iter('{http://www.esa.int/safe/sentinel-1.0}startTime'):
            self.acquisition_time.append(element.text)
        for element in tree.iter('{http://www.esa.int/safe/sentinel-1.0}stopTime'):
            self.acquisition_time.append(element.text)
        for element in tree.iter('{http://www.opengis.net/gml}coordinates'):
            self.gml_coordinates = element.text

    def download_tiff(self, polarization=None):
        # Download tiff file, polarization is either vv or vh and optional
        self.download_manifest()
        product_name = self.name + '.SAFE'
        for count, file in enumerate(self.tiff_files):
            if polarization is None or polarization in file:
                print("Downloading tiff  " + str(count + 1) + '/' + str(len(self.tiff_files)))
                print(file)
                url = stgs.COP_BASE_URL + "/Products('%s')/Nodes('%s')/Nodes('measurement')/Nodes('%s')/$value" % (
                    self.uuid, product_name, file)
                response = requests.get(url, auth=HTTPBasicAuth('ouassim', '747400Co'), stream=True)
                size = int(response.headers.get('content-length', None))
                filename = "../raw_data/" + self.uuid + "/" + file
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'wb') as f:
                    i = 1
                    for chunk in response.iter_content(chunk_size=1048576):
                        i += 1
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            self.print_progress(i, int(size / 1048576), "progress", str(int(size / 1048576)) + "mb")
                self.downloaded_files.append(file)
                return

    def delete_raw_data(self):
        """Delete all data of a product"""
        self.delete_quicklook()
        self.delete_tiff_files()
        self.delete_manifest()
        shutil.rmtree('../raw_data/' + self.uuid)

    def delete_quicklook(self):
        """Delete quicklook of a product"""
        os.remove('../raw_data/' + self.uuid + '/' + self.uuid + '.png')

    def delete_tiff_files(self):
        """Delete tiff files of a product"""
        for file in self.tiff_files:
            os.remove('../raw_data/' + self.uuid + '/' + file)

    def delete_manifest(self):
        """Delete manifest file of a product"""
        os.remove('../raw_data/' + self.uuid + '/' + self.uuid + '.xml')

    def set_name(self):
        if self.name is None:
            print("No name detected for " + self.uuid + ". Getting it from ESA Servers")
            url = stgs.COP_BASE_URL + "/Products('%s')/Name/$value" % self.uuid
            response = requests.get(url, auth=HTTPBasicAuth('ouassim', '747400Co'))
            self.name = response.text
            print("Name is " + self.name)
        else:
            logging.info("Already a name for " + self.uuid)

    # Print iterations progress
    @staticmethod
    def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=50):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            barLength   - Optional  : character length of bar (Int)
        """
        format_str = "{0:." + str(decimals) + "f}"
        percents = format_str.format(100 * (iteration / float(total)))
        filled_length = int(round(bar_length * iteration / float(total)))
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
        if iteration == total:
            sys.stdout.write('\n')
        sys.stdout.flush()
