from OSMPythonTools.overpass import Overpass
from OSMPythonTools.overpass import overpassQueryBuilder
from OSMPythonTools.api import Api

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, LineString, Point

plot_enable = False

"""
Author: Kurt Cieslinski
"""


def get_lot(angle, coordinate):
    lat = coordinate[0]
    long = coordinate[1]

    n = 0.0005

    overpass = Overpass()
    api = Api()

    query_buildings = overpassQueryBuilder(bbox=[lat - n, long - n, lat + n, long + n], elementType='way',
                                           selector='"building"',
                                           out='body')
    query_tunnels = overpassQueryBuilder(bbox=[lat - n, long - n, lat + n, long + n], elementType='way',
                                         selector='"tunnel"',
                                         out='body')

    req = overpass.query(query_buildings)
    # req = nominatim.query(47.06314, 15.44599,  reverse=True, zoom=10)
    buildings = req._elements

    req = overpass.query(query_tunnels)
    tunnels = req._elements

    tunnel_nodes = [b._json["nodes"] for b in tunnels]
    tunnel_nodes = [item for sublist in tunnel_nodes for item in sublist]

    building_nodes = [b._json["nodes"] for b in buildings]
    nodes = []
    for b in building_nodes:
        tmp = []
        for x in b:
            if x not in tunnel_nodes and x not in [i[0] for i in tmp]:
                node = api.query('node/' + str(x))
                if node.tag("entrance") is None:
                    tmp.append((x, node.geometry()["coordinates"]))

        nodes.append(tmp)

    angle = -angle
    view_point = Point(long, lat)

    if plot_enable:
        plt.axis('off')
        plt.plot(long, lat, 'ro')
        plt.plot([long, long + np.sin(angle) * n], [lat, lat + np.cos(angle) * n])
        for points in nodes:
            points = [i[1] for i in points]
            l = len(points)
            for i in range(l):
                plt.plot([points[i][0], points[(i + 1) % l][0]],
                         [points[i][1], points[(i + 1) % l][1]])

        plt.show()

    filtered_nodes = []
    view_line = LineString([(long, lat), (long + np.sin(angle), lat + np.cos(angle))])
    for points in nodes:
        points = [i[1] for i in points]
        polygon = Polygon(points)
        if view_line.intersects(polygon):
            dist = polygon.distance(view_point)
            filtered_nodes.append((points, dist))

    if plot_enable:
        plt.axis('off')
        plt.plot(long, lat, 'ro')
        plt.plot([long, long + np.sin(angle) * n], [lat, lat + np.cos(angle) * n])

    dist_min = min([node[1] for node in filtered_nodes])
    nearest_poly = [node for node in filtered_nodes if dist_min == node[1]]

    nearest_poly = nearest_poly[0][0]
    nearest_poly.reverse()

    edges = []
    for p1 in nearest_poly:
        for p2 in nearest_poly:
            if p1 is not p2:
                # plt.plot([p1[0], p2[0]], [p1[1], p2[1]])
                edges.append(LineString([(p1[0], p1[1]), (p2[0], p2[1])]))

    if plot_enable:
        l = len(nearest_poly)
        for i in range(l):
            plt.plot([nearest_poly[i][0], nearest_poly[(i + 1) % l][0]],
                     [nearest_poly[i][1], nearest_poly[(i + 1) % l][1]])

    dist = float("inf")
    min_edge = None
    filtered_edges = [edge for edge in edges if edge.intersects(view_line)]
    for edge in filtered_edges:
        dist_tmp = edge.distance(view_point)
        if dist_tmp < dist:
            dist = dist_tmp
            min_edge = edge

    if min_edge is not None:
        x, y = min_edge.xy
        x1 = x[0] - long
        x2 = x[1] - long
        y1 = y[0] - lat
        y2 = y[1] - lat
        a = np.arctan2(x1 * y2 - y1 * x2, x1 * x2 + y1 * y2)

        i = 0 if a > 0 else 1

        if plot_enable:
            plt.plot(x[i], y[i], 'bo')
            plt.plot(x, y)

        first_point_index = nearest_poly.index([x[i], y[i]])

        nearest_poly = nearest_poly[first_point_index:] + nearest_poly[:first_point_index]
        if nearest_poly.index([x[1 - i], y[1 - i]]) != 1:
            tmp = nearest_poly.copy()
            tmp = tmp[1:]
            tmp.reverse()
            nearest_poly = [nearest_poly[0]] + tmp
        # plt.plot(nearest_poly[0][0], nearest_poly[0][1], 'ro')
        # print(first_point_index)

    """  
    x = [p[0] for p in points[0]]
    y = [p[1] for p in points[0]]
    plt.plot(x, y)"""

    if plot_enable:
        plt.show()

    return nearest_poly


if __name__ == "__main__":
    angle = -1.0843861647984125
    lat = 47.062593
    long = 15.446344

    get_lot(angle, (lat, long))
