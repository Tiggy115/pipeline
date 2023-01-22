import math

from src.cgv import *

"""
Author: Kurt Cieslinski
"""


def lon2tile(lon, zoom):
    """
    from Bela Bohlender https://github.com/cc-bbohlender/cgv/tree/gh-pages
    """
    return ((lon + 180) / 360) * math.pow(2, zoom)


def lat2tile(lat, zoom):
    """
    from Bela Bohlender https://github.com/cc-bbohlender/cgv/tree/gh-pages
    """
    return (
            ((1 - math.log(math.tan((lat * math.pi) / 180) + 1 / math.cos((lat * math.pi) / 180)) / math.pi) / 2) *
            math.pow(2, zoom)
    )


def tile2lon(x, zoom):
    """
    from Bela Bohlender https://github.com/cc-bbohlender/cgv/tree/gh-pages
    """
    return (x / math.pow(2, zoom)) * 360 - 180


def tile2lat(y, zoom):
    """
    from Bela Bohlender https://github.com/cc-bbohlender/cgv/tree/gh-pages
    """
    n = math.pi - (2 * math.pi * y) / math.pow(2, zoom)
    return (180 / math.pi) * math.atan(0.5 * (math.exp(n) - math.exp(-n)))


def tileMeterRatio(y, zoom, tilePixelSize=256):
    """
    from Bela Bohlender https://github.com/cc-bbohlender/cgv/tree/gh-pages
    """
    lat = tile2lat(y, zoom)
    return ((156543.03 * math.cos((lat * math.pi) / 180)) / math.pow(2, zoom)) * tilePixelSize


def tileZoomRatio(fro, to):
    """
    from Bela Bohlender https://github.com/cc-bbohlender/cgv/tree/gh-pages
    """
    return math.pow(2, to) / math.pow(2, fro)


def to_point(x, y, pan_coord):
    """
    modified from Bela Bohlender https://github.com/cc-bbohlender/cgv/tree/gh-pages
    """
    glob_x = lon2tile(pan_coord[1], 0)
    glob_y = lat2tile(pan_coord[0], 0)

    zoom_ratio = tileZoomRatio(0, 18)
    meter_ratio = tileMeterRatio(round(y * zoom_ratio), 18)
    x_meter = ((x * zoom_ratio) - math.floor(glob_x * zoom_ratio)) * meter_ratio
    y_meter = ((y * zoom_ratio) - math.floor(glob_y * zoom_ratio)) * meter_ratio

    return x_meter, y_meter


def translate_grammar(facade, pan_coord):
    p1 = facade.lot[0]
    p1 = to_point(lon2tile(p1[0], 0), lat2tile(p1[1], 0), pan_coord)

    p2 = facade.lot[1]
    p2 = to_point(lon2tile(p2[0], 0), lat2tile(p2[1], 0), pan_coord)
    width = math.dist(p1, p2)
    scale_factor = width / facade.width

    # scale_factor = 0.02

    width_anchor_x_lst = facade.width_anchor_x_lst
    height_anchor_y_lst = facade.height_anchor_y_lst
    first_floor_x_anchor_lst = facade.first_floor_x_anchor_lst
    first_floor_y_anchor = facade.first_floor_y_anchor
    first_floor_dim = facade.first_floor_dim
    door_rectangle_lst = facade.door_rectangle_lst
    # width = facade.width * scale_factor
    height = facade.height * scale_factor

    no_door = len(door_rectangle_lst) == 0

    width_anchor_x_lst.reverse()
    width_anchor_x_lst = [(tup[0] * scale_factor, width - tup[1] * scale_factor) for tup in width_anchor_x_lst]

    height_anchor_y_lst.reverse()
    height_anchor_y_lst = [(tup[0] * scale_factor, height - tup[1] * scale_factor) for tup in height_anchor_y_lst]

    first_floor_x_anchor_lst.reverse()
    first_floor_x_anchor_lst = [width - x * scale_factor for x in first_floor_x_anchor_lst]

    first_floor_y_anchor = height - first_floor_y_anchor * scale_factor

    first_floor_dim = (first_floor_dim[0] * scale_factor, first_floor_dim[1] * scale_factor)

    if not no_door:
        door_rectangle_lst = [(width - tup[0] * scale_factor, height - tup[1] * scale_factor,
                               tup[2] * scale_factor, tup[3] * scale_factor) for tup in door_rectangle_lst]

    grammar_string = START
    # lot = face(point2(0, 0), point2(0, 5), point2(width, 5), point2(width, 0))
    lot_points = []
    for p in facade.lot:
        tmp = to_point(lon2tile(p[0], 0), lat2tile(p[1], 0), pan_coord)
        lot_points.append(point2(tmp[0], tmp[1]))

    lot = face(lot_points)

    grammar_string = after(grammar_string, lot)
    grammar_string = after(grammar_string, rotate(0, 0, 0))
    grammar_string = after(grammar_string, translate(0, 0, 0))
    grammar_string = after(grammar_string, extrude(height))
    grammar_string = after(grammar_string, to_faces())

    # initial split
    # axis z in 3D here is equivalent to the "classic" y-axis in 2D
    split_z = [0]

    first_floor_higher_ys = []
    first_floor_lower_ys = []

    if not no_door:
        for box in door_rectangle_lst:
            y_anchor = box[1]
            first_floor_higher_ys.append(y_anchor)
            first_floor_lower_ys.append(y_anchor - box[3])

    first_floor_higher_ys.append(first_floor_y_anchor)
    first_floor_lower_ys.append(first_floor_y_anchor - first_floor_dim[1])

    # split first at the min of the first floor and then at the max
    first_floor_min = min(first_floor_lower_ys)
    first_floor_max = max(first_floor_higher_ys)
    split_z.append(first_floor_min)
    split_z.append(first_floor_max - first_floor_min)
    last_split = first_floor_max
    for tup in height_anchor_y_lst:
        split_z.append(tup[1] - tup[0] - last_split)
        split_z.append(tup[0])
        last_split = tup[1]
    split_z.append(height - last_split)
    split_z_string = split("z", "true", split_z)

    # split the windows at floor >= 2
    split_x = [0]
    last_split = 0
    for tup in width_anchor_x_lst:
        split_x.append(tup[1] - tup[0] - last_split)
        split_x.append(tup[0])
        last_split = tup[1]
    split_x.append(width - last_split)
    split_x_string = split("x", "true", split_x)

    # split first floor
    first_floor_width = first_floor_dim[0]
    first_floor_height = first_floor_dim[1]

    door_width_anchor_x = []
    if not no_door:
        door_width_anchor_x = [(box[2], box[0]) for box in door_rectangle_lst]
        door_width_anchor_x.append((math.inf, math.inf))

    door_x_anchor_index = 0
    split_x = [0]
    last_split = 0
    for x in first_floor_x_anchor_lst:
        if not no_door:
            door_x_anchor = door_width_anchor_x[door_x_anchor_index][1]
            if x > door_x_anchor:
                door_width = door_width_anchor_x[door_x_anchor_index][0]
                split_x.append(door_x_anchor - door_width - last_split)
                split_x.append(door_width)
                last_split = door_x_anchor
                door_x_anchor_index += 1
        split_x.append(x - first_floor_width - last_split)
        split_x.append(first_floor_width)
        last_split = x
    split_x.append(width - last_split)
    split_first_floor_x_string = split("x", "true", split_x)

    split_windows_first_floor = split("z", "true",
                                      [0, first_floor_y_anchor - first_floor_height - first_floor_min,
                                       first_floor_height, first_floor_max - first_floor_y_anchor])

    # remove mat.inf at the end
    if not no_door:
        door_width_anchor_x.pop()

    # get indexes of the door(s)
    door_indexes = []
    if not no_door:
        first_floor_windows_num = len(first_floor_x_anchor_lst)
        for door in door_width_anchor_x:
            if first_floor_x_anchor_lst[0] > door[1]:
                door_indexes.append(2)
                continue
            if first_floor_x_anchor_lst[first_floor_windows_num - 1] < door[1]:
                door_indexes.append((first_floor_windows_num + 1) * 2)
                continue
            for i in range(1, first_floor_windows_num):
                if first_floor_x_anchor_lst[i - 1] < door[1] < first_floor_x_anchor_lst[i]:
                    door_indexes.append((i + 1) * 2)
                    break

    floors_num = (len(height_anchor_y_lst) + 1) * 2 + 2
    first_floor_elements_num = (len(first_floor_x_anchor_lst) + len(door_rectangle_lst)) * 2 + 2

    color_door = color("#241f31")
    doors = THIS
    all_doors_cond = "false"
    if not no_door:
        for i, d in enumerate(door_indexes):
            door_split = split("z", "true", [0, door_rectangle_lst[i][1] - door_rectangle_lst[i][3] - first_floor_min,
                                             door_rectangle_lst[i][3], first_floor_max - door_rectangle_lst[i][1]])
            door = if_else(equal(index(), 2), color_door, THIS)
            door = after(door_split, door)
            door_cond = equal(modulo(index(), first_floor_elements_num), d)
            doors = if_else(door_cond, door, doors)
            if all_doors_cond == "false":
                all_doors_cond = door_cond
            else:
                all_doors_cond = and_o(door_cond, not_o(all_doors_cond))

    # colorize windows
    color_window = color("#1a5fb4")
    color_window = if_else(equal(modulo(index(), 2), 0), color_window, THIS)

    first_floor_cond = equal(index(), 2)
    first_floor_repeat_cond = equal(modulo(index(), floors_num), 2)
    windows_first_floor_cond = and_o(not_o(all_doors_cond), equal(modulo(index(), 2), 0))
    window_and_not_first_floor_cond = and_o(not_o(first_floor_repeat_cond), equal(modulo(index(), 2), 0))

    first_floor_repeat = if_else(equal(modulo(index(), 2), 0), after(split_windows_first_floor, color_window), THIS)
    first_floor_repeat = if_else(first_floor_repeat_cond, after(split_first_floor_x_string, first_floor_repeat), THIS)

    first_floor_elements = if_else(windows_first_floor_cond, after(split_windows_first_floor, color_window), doors)
    first_floor_elements = after(split_first_floor_x_string, first_floor_elements)

    first_floor = if_else(first_floor_cond, first_floor_elements, first_floor_repeat)

    windows = if_else(window_and_not_first_floor_cond, after(split_x_string, color_window), first_floor)
    windows = after(split_z_string, windows)
    windows = if_else(equal(id(), "\"0\""), windows, THIS)

    grammar_string = after(grammar_string, windows)

    windows_mid = noun("MidWindows")
    windows_mid = after(windows_mid, after(split_x_string, color_window))

    split_first_floor_x = noun("SplitFirstFloorX")
    split_first_floor_x = after(split_first_floor_x, split_first_floor_x_string)

    nouns = "\n" + windows_mid + "\n" + split_first_floor_x

    return grammar_string


if __name__ == "__main__":
    p1 = [
        15.446017,
        47.063621
    ]

    p1 = to_point(lon2tile(p1[0], 0), lat2tile(p1[1], 0), (47.0634489, 15.4457957))
    print(p1)
