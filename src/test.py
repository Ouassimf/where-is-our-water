from descartes import PolygonPatch
from matplotlib import path
from shapely import geos
from shapely import wkt

import class_wow_imagery
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import xml.etree.ElementTree as ETree


loc = [[16.0, 48.0], [16.5, 48.0], [16.5, 47.5], [16.0, 47.5], [16.0, 48.0]]
loc_2 = [[2, 49], [2.5, 49], [2.5, 48], [2, 48], [2, 49]]
loc_3 = [[-5, 49], [-4, 49], [-4, 48.5], [-5, 48.5], [-5, 49]]
loc_4 = [[103.6, 12.5], [104.5, 12.5], [104.5, 13], [103.6, 13], [103.6, 12.5]]
# Lake in the moutain without shadow
loc_5 = [[12.33, 47.97], [12.56, 47.97], [12.56, 47.8], [12.33, 47.8], [12.33, 47.97]]
loc_6 = [[12.33, 47.97], [13.56, 47.97], [13.56, 49.8], [12.33, 49.8], [12.33, 47.97]]

img = class_wow_imagery.WowImagery(loc_6, '15_08_2016')

img.generate_from_coordinates()
