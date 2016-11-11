import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ETree
from matplotlib.path import Path
from matplotlib import path
import matplotlib.patches as patches
from class_provider_imagery import ProviderImagery
import matplotlib.pyplot as plt


class WowImagery:
    def __init__(self, coordinates, file=None):
        self.coordinates = coordinates
        self.file = file

    def generate_from_coordinates(self, date):
        product_list = self.get_product_list_by_time_location(date)
        contained_list = self.fully_contained_in_product(product_list)
        if contained_list:
            image = ProviderImagery('C', contained_list[0])
            image.download_quicklook()
            # image.download_tiff('vv')
            # self.file = image.tiff_files[0]
            # self.crop()

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
        coordinates = ",".join(" ".join(map(str, l)) for l in self.coordinates)
        coordinates = 'POLYGON((' + coordinates + '))'
        location_filter = 'footprint:"Intersects(%s)"' % coordinates
        type_filter = "producttype:GRD"
        # TODO : Implement date in filter
        date_filter = "beginposition:[NOW-1MONTHS TO NOW] AND endposition:[NOW-1MONTHS TO NOW]"
        filter_tag = location_filter + " AND " + type_filter + " AND " + date_filter
        url += filter_tag
        print(url)
        response = requests.get(url, auth=HTTPBasicAuth('ouassim', '747400Co'))
        print(response.text)
        return response.text

    def fully_contained_in_product(self, product_list):
        tree = ETree.ElementTree(ETree.fromstring(product_list))
        root = tree.getroot()
        container_list = []
        for node in root.findall('{http://www.w3.org/2005/Atom}entry'):
            uuid = node.find('{http://www.w3.org/2005/Atom}id').text
            footprint = node.find('{http://www.w3.org/2005/Atom}str[@name="footprint"]').text
            footprint = footprint[footprint.find("(") + 2:footprint.find(")")]
            footprint = self.process_footprint_string(footprint)
            is_contained = self.test_footprint(footprint)
            if is_contained:
                container_list.append(uuid)

        return container_list

    def test_footprint(self, footprint):
        # Footprint in the form of [[16.75, 47.40], ... , [16.70, 47.40]]
        target_polygon = path.Path(self.coordinates)
        candidate_polygon = path.Path(footprint)
        self.plot_polygons(candidate_polygon, target_polygon)
        is_contained = candidate_polygon.contains_path(target_polygon)
        print(is_contained)
        return is_contained

    def plot_polygons(self, candidate_polygon, target_polygon):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        patch = patches.PathPatch(target_polygon, facecolor='orange', lw=2)
        patch2 = patches.PathPatch(candidate_polygon, facecolor='blue', lw=2)
        ax.add_patch(patch2)
        ax.add_patch(patch)
        ax.autoscale(True)
        plt.show()

    def crop(self):
        self.file = ''
        return 1

    def find_maximum_container(self, product_list):
        return

    def compute_leftovers(self, covers):
        return

    @staticmethod
    def process_footprint_string(footprint):
        list_raw = footprint.split(",")
        list_separated = []
        for item in list_raw:
            item_list = item.split(" ")
            list_separated.append(item_list)
        list_separated = [[float(j) for j in i] for i in list_separated]
        return list_separated
