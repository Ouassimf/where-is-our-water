import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ETree

from class_provider_imagery import ProviderImagery


class WowImagery:
    def __init__(self, coordinates, file=None):
        self.coordinates = coordinates
        self.file = file

    def generate_from_coordinates(self, date):
        product_list = self.get_product_list_by_time_location(date)
        contained_list = self.fully_contained_in_product(product_list)
        if contained_list:
            image = ProviderImagery('C', contained_list[0])
            image.download_tiff('vv')
            self.file = image.tiff_files[0]
            self.crop()

        else:
            # TODO : Merger
            covers = []
            leftovers = 0
            while leftovers:
                covers = self.find_maximum_container(product_list)
                leftovers = self.compute_leftovers(covers)
            print("I will merge")

    def split_in_tiles(self):
        pass

    def classify(self):
        pass

    def get_product_list_by_time_location(self, date):
        url = "https://scihub.copernicus.eu/dhus/search?start=0&rows=100&q="
        location_filter = 'footprint:"Intersects(%s)"' % self.coordinates
        type_filter = "producttype:GRD"
        # TODO : Implement date in filter
        date_filter = "beginposition:[NOW-1MONTHS TO NOW] AND endposition:[NOW-1MONTHS TO NOW]"
        filter = location_filter + " AND " + type_filter + " AND " + date_filter
        url += filter
        print(url)
        response = requests.get(url, auth=HTTPBasicAuth('ouassim', '747400Co'))
        print(response.text)
        return response.text

    def fully_contained_in_product(self, product_list):
        tree = ETree.ElementTree(ETree.fromstring(product_list))
        root = tree.getroot()
        i = 1
        container_list = []
        for node in root.findall('{http://www.w3.org/2005/Atom}entry'):
            uuid = node.find('{http://www.w3.org/2005/Atom}id').text
            print(i)
            i += 1
            print(uuid)
            footprint = node.find('{http://www.w3.org/2005/Atom}str[@name="gmlfootprint"]').text
            self.test_footprint(footprint)
        return container_list

    def test_footprint(self, footprint):
        print(footprint)
        pass

    def crop(self):
        self.file = ''
        return 1

    def find_maximum_container(self, product_list):
        return

    def compute_leftovers(self, covers):
        return
