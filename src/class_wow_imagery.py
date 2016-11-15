import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ETree
from matplotlib.path import Path
from matplotlib import path
import matplotlib.patches as patches
from class_provider_imagery import ProviderImagery
import matplotlib.pyplot as plt
import settings
from osgeo import gdal, gdalnumeric, ogr
from PIL import Image, ImageDraw
import os
import numpy as np


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
        # self.plot_polygons(candidate_polygon, target_polygon)
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
        gdal.AllRegister()
        # file = self.file[0]
        file = '../raw_data/2a97b055-3dc7-4a94-864e-0979ddee9412/s1b-iw-grd-vv-20161114t050057-20161114t050122-002950-00501f-001.tiff'
        ds = gdal.Open(file)
        band = ds.GetRasterBand(1)
        data = band.ReadAsArray()
        clipper = settings.WORKING_DIRECTORY + self.generate_shapefile_from_extent()
        clipped = self.clip_raster(data, clipper)
        return 1

    def generate_shapefile_from_extent(self):
        from osgeo import ogr
        import os

        # Create a Polygon from the coordinates
        ring = ogr.Geometry(ogr.wkbLinearRing)
        filename = 'clipper'
        for point in self.coordinates:
            print(point)
            ring.AddPoint(point[0], point[1])
            filename += '_' + str(point[0]) + '_' + str(point[1])
        filename += '.shp'
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        # Save extent to a new Shapefile
        out_shapefile = settings.WORKING_DIRECTORY + filename

        out_driver = ogr.GetDriverByName("ESRI Shapefile")

        # Remove output shapefile if it already exists
        if os.path.exists(out_shapefile):
            out_driver.DeleteDataSource(out_shapefile)

        # Create the output shapefile
        out_data_source = out_driver.CreateDataSource(out_shapefile)
        out_layer = out_data_source.CreateLayer("states_extent", geom_type=ogr.wkbPolygon)

        # Add an ID field
        id_field = ogr.FieldDefn("id", ogr.OFTInteger)
        out_layer.CreateField(id_field)

        # Create the feature and set values
        feature_def = out_layer.GetLayerDefn()
        feature = ogr.Feature(feature_def)
        feature.SetGeometry(poly)
        feature.SetField("id", 1)
        out_layer.CreateFeature(feature)

        # Close DataSource
        out_data_source.Destroy()
        return filename

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

    @staticmethod
    def clip_raster(rast, features_path, gt=None, nodata=-9999):
        """
        Clips a raster (given as either a gdal.Dataset or as a numpy.array
        instance) to a polygon layer provided by a Shapefile (or other vector
        layer). If a numpy.array is given, a "GeoTransform" must be provided
        (via dataset.GetGeoTransform() in GDAL). Returns an array. Clip features
        must be a dissolved, single-part geometry (not multi-part). Modified from:

        http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
        #clip-a-geotiff-with-shapefile

        Arguments:
            rast            A gdal.Dataset or a NumPy array
            features_path   The path to the clipping features
            gt              An optional GDAL GeoTransform to use instead
            nodata          The NoData value; defaults to -9999.
        """
        print(features_path)

        def array_to_image(a):
            """
            Converts a gdalnumeric array to a Python Imaging Library (PIL) Image.
            """
            i = Image.fromstring('L', (a.shape[1], a.shape[0]),
                                 (a.astype('b')).tostring())
            return i

        def image_to_array(i):
            """
            Converts a Python Imaging Library (PIL) array to a gdalnumeric image.
            """
            a = gdalnumeric.fromstring(i.tobytes(), 'b')
            a.shape = i.im.size[1], i.im.size[0]
            return a

        def world_to_pixel(geo_matrix, x, y):
            """
            Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
            the pixel location of a geospatial coordinate; from:
            http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#clip-a-geotiff-with-shapefile
            """
            ul_x = geo_matrix[0]
            ul_y = geo_matrix[3]
            xDist = geo_matrix[1]
            yDist = geo_matrix[5]
            rtnX = geo_matrix[2]
            rtnY = geo_matrix[4]
            pixel = int((x - ul_x) / xDist)
            line = int((ul_y - y) / xDist)
            return pixel, line

        # Can accept either a gdal.Dataset or numpy.array instance
        if not isinstance(rast, np.ndarray):
            gt = rast.GetGeoTransform()
            rast = rast.ReadAsArray()

        # Create an OGR layer from a boundary shapefile
        features = ogr.Open(features_path)
        if features.GetDriver().GetName() == 'ESRI Shapefile':
            lyr = features.GetLayer(os.path.split(os.path.splitext(features_path)[0])[1])

        else:
            lyr = features.GetLayer()

        # Get the first feature
        poly = lyr.GetNextFeature()

        # Convert the layer extent to image pixel coordinates
        minX, maxX, minY, maxY = lyr.GetExtent()
        ulX, ulY = world_to_pixel(gt, minX, maxY)
        lrX, lrY = world_to_pixel(gt, maxX, minY)

        # Calculate the pixel size of the new image
        pxWidth = int(lrX - ulX)
        pxHeight = int(lrY - ulY)

        # If the clipping features extend out-of-bounds and ABOVE the raster...
        if gt[3] < maxY:
            # In such a case... ulY ends up being negative--can't have that!
            iY = ulY
            ulY = 0

        # Multi-band image?
        try:
            clip = rast[:, ulY:lrY, ulX:lrX]

        except IndexError:
            clip = rast[ulY:lrY, ulX:lrX]

        # Create a new geomatrix for the image
        gt2 = list(gt)
        gt2[0] = minX
        gt2[3] = maxY

        # Map points to pixels for drawing the boundary on a blank 8-bit,
        #   black and white, mask image.
        points = []
        pixels = []
        geom = poly.GetGeometryRef()
        pts = geom.GetGeometryRef(0)

        for p in range(pts.GetPointCount()):
            points.append((pts.GetX(p), pts.GetY(p)))

        for p in points:
            pixels.append(world_to_pixel(gt2, p[0], p[1]))

        raster_poly = Image.new('L', (pxWidth, pxHeight), 1)
        rasterize = ImageDraw.Draw(raster_poly)
        rasterize.polygon(pixels, 0)  # Fill with zeroes

        # If the clipping features extend out-of-bounds and ABOVE the raster...
        if gt[3] < maxY:
            # The clip features were "pushed down" to match the bounds of the
            #   raster; this step "pulls" them back up
            premask = image_to_array(raster_poly)
            # We slice out the piece of our clip features that are "off the map"
            mask = np.ndarray((premask.shape[-2] - abs(iY), premask.shape[-1]), premask.dtype)
            mask[:] = premask[abs(iY):, :]
            mask.resize(premask.shape)  # Then fill in from the bottom

            # Most importantly, push the clipped piece down
            gt2[3] = maxY - (maxY - gt[3])

        else:
            mask = image_to_array(raster_poly)

        # Clip the image using the mask
        try:
            clip = gdalnumeric.choose(mask, (clip, nodata))

        # If the clipping features extend out-of-bounds and BELOW the raster...
        except ValueError:
            # We have to cut the clipping features to the raster!
            rshp = list(mask.shape)
            if mask.shape[-2] != clip.shape[-2]:
                rshp[0] = clip.shape[-2]

            if mask.shape[-1] != clip.shape[-1]:
                rshp[1] = clip.shape[-1]

            mask.resize(*rshp, refcheck=False)

            clip = gdalnumeric.choose(mask, (clip, nodata))

        return (clip, ulX, ulY, gt2)
