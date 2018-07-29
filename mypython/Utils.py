#!/usr/bin/env python

#############
# GEOMETRTY
#############

def orient_bbox(polygon_array):
    lons = sorted([polygon_array[0][0], polygon_array[1][0]])
    lats = sorted([polygon_array[0][1], polygon_array[1][1]])
    return [lons[0], lats[0], lons[1], lats[1]]


def orient_polygon_ccw(polygon_array):
    sum1 = 0
    sum2 = 0
    # Some geojson geometries contain elevation,
    # We need to filter just the lon, lats
    new_polygon_array = []
    for i in range(len(polygon_array[0:len(polygon_array) - 1])):
        new_polygon_array.append([polygon_array[i][0], polygon_array[i][1]])
        sum1 += polygon_array[i][0] * polygon_array[i + 1][1]
        sum2 += polygon_array[i + 1][0] * polygon_array[i][1]
    sum1 += polygon_array[len(polygon_array) - 1][0] * polygon_array[0][1]
    sum2 += polygon_array[0][0] * polygon_array[len(polygon_array) - 1][1]
    new_polygon_array.append([polygon_array[len(polygon_array) - 1][0], polygon_array[len(polygon_array) - 1][1]])
    A = sum1 - sum2
    # Already ccw
    if A > 0:
        return new_polygon_array
    # cw, need to reverse the coords
    if A < 0:
        return list(reversed(new_polygon_array))
    if A == 0:
        return new_polygon_array

def orient_polygons_ccw(feat_coords):
    geom_coords = []
    for poly in feat_coords:
        geom_coords.append([orient_polygon_ccw(lin_ring) for lin_ring in poly])
    return geom_coords
