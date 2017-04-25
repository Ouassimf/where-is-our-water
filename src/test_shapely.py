from shapely.geometry import Polygon
from matplotlib import pyplot as plt

poly = Polygon([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
poly2 = Polygon([[0, 0], [0, 1], [1, 1], [0, 0]])
poly3 = Polygon([[0.25, 0.25], [0.25, 1.75], [0.75, 1.75], [0.75, 0.25], [0.25, 0.25]])
print(poly.wkt)

x, y = poly.exterior.xy
fig = plt.figure(1, figsize=(5, 5), dpi=90)
ax = fig.add_subplot(111)
ax.plot(x, y, color='#6699cc', alpha=0.7,
        linewidth=3, solid_capstyle='round', zorder=2)

x, y = poly3.exterior.xy
fig = plt.figure(1, figsize=(5, 5), dpi=90)
ax = fig.add_subplot(111)
ax.plot(x, y, color='#6699cc', alpha=0.7,
        linewidth=3, solid_capstyle='round', zorder=2)

inter = poly3.intersection(poly)
print(inter.area)
x, y = poly2.exterior.xy
ax.plot(x, y, color='#6699cc', alpha=0.7,
        linewidth=3, solid_capstyle='round', zorder=2)

diff = poly.symmetric_difference(poly3)
print(diff.area)
x, y = diff.exterior.xy
ax.plot(x, y, color='red', alpha=0.7,
        linewidth=3, solid_capstyle='round', zorder=2)
ax.set_title('Polygon')
plt.show()
