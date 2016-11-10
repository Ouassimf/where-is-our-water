import logging
import os
import requests
import settings as stgs
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ETree


class ProviderImagery:
    """Class for manipulating imagery from Sentinel Sat"""

    def __init__(self, source, uuid, name=None, tiff_files=None):
        # source is either "C" or "L" for respectively Copernicus/Landsat
        self.source = source
        # unique identifier from the imagery provider.
        self.uuid = uuid
        self.name = name
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
        print(url)
        response = requests.get(url, auth=HTTPBasicAuth(stgs.COP_USERNAME, stgs.COP_PASSWORD))
        filename = "../raw_data/" + self.uuid + "/" + self.uuid + ".xml"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as f:
            f.write(response.content)
        return response.content

    def download_tiff(self, polarization=None):
        # Download tiff file, polarization is either vv or vh
        xml = self.download_manifest()
        product_name = self.name + '.SAFE'
        tree = ETree.ElementTree(ETree.fromstring(xml))
        root = tree.getroot()
        self.tiff_files = []
        for element in root.findall(".//dataObject[@repID='s1Level1MeasurementSchema']"):
            full = element.find('byteStream/fileLocation').attrib['href']
            path, file = os.path.split(full)
            self.tiff_files.append(file)
            if polarization in full or polarization is None:
                print("Downloading tiff")
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
                            print(str(i) + "/" + str(int(size / 1048576)))
                return

    def delete_raw_data(self):
        """Delete all data of a product"""
        self.delete_quicklook()
        self.delete_tiff_files()
        self.delete_manifest()

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
