from random import random

import time
from shapely.geometry import Polygon
from shapely.ops import cascaded_union
from matplotlib import pyplot as plt
from descartes import PolygonPatch

target_poly = Polygon([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])
leftover_poly = Polygon([[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]])

poly_list = []

while len(poly_list) < 50:
    x = random()
    y = random()
    dx = random()
    dy = random()
    poly_list.append([[x, y], [x, y + dy], [x + dx, y + dy], [x + dx, y], [x, y]])
print(poly_list)

fig = plt.figure(1, figsize=(5, 5), dpi=90)


def plot_basics():
    axes = plt.gca()
    axes.set_xlim([0, 2])
    axes.set_ylim([0, 2])

    ring_patch = PolygonPatch(target_poly, fc='blue', ec='black', alpha=0.5, hatch='*')
    ax.add_patch(ring_patch)
    ring_patch = PolygonPatch(leftover_poly, fc='yellow', ec='black', alpha=0.7, hatch='/')
    ax.add_patch(ring_patch)


plt.ion()

union_polygon_list = []
for x in range(1, 10):
    ax = fig.add_subplot(111)
    plot_basics()
    print("ITERATION : " + str(x))
    print("Candidates Polygons  : " + str(len(poly_list)))
    maximum_container = 0
    for idx, item in enumerate(poly_list):
        poly = Polygon(item)
        x, y = poly.exterior.xy
        tmp = ax.plot(x, y, color='#6699cc', alpha=0.7,
                      linewidth=3, solid_capstyle='round', zorder=2)
        if poly.intersection(leftover_poly).area > maximum_container:
            maximum_container = poly.intersection(leftover_poly).area
            maximum_container_id = idx

        plt.show()
        fig.canvas.draw()
        time.sleep(.0200)
    if maximum_container != 0:
        poly = Polygon(poly_list[maximum_container_id])
        x, y = poly.exterior.xy
        ax.plot(x, y, color='gold', alpha=0.7,
                linewidth=3, solid_capstyle='round', zorder=2)
        plt.show()
        fig.canvas.draw()
        time.sleep(.5)
        print(maximum_container)
        union_polygon_list.append(Polygon(poly_list[maximum_container_id]))
        union_polygon = cascaded_union(union_polygon_list)
        poly_list.pop(maximum_container_id)
        leftover_poly = target_poly.difference(union_polygon)

    fig.clear()
    plt.show()
    fig.canvas.draw()

print(len(union_polygon_list))

# print(len(ax.lines))
# for x in range(1, 10):
#     ax.lines.pop(1)
#     fig.canvas.draw()
#     plt.show()
#     time.sleep(.15)
#
# time.sleep(15)
