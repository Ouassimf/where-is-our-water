from matplotlib import path
import class_wow_imagery
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

loc = [[16.0, 48.0], [16.5, 48.0], [16.5, 47.5], [16.0, 47.5], [16.0, 48.0]]
loc_2 = [[2, 49], [2.5, 49], [2.5, 48], [2, 48], [2, 49]]
loc_3 = [[-5, 49], [-4, 49], [-4, 48.5], [-5, 48.5], [-5, 49]]

img = class_wow_imagery.WowImagery(loc)
# img.generate_from_coordinates(1)
img.crop()
