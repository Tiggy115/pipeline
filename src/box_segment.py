from __future__ import print_function

import math
from statistics import median

import cv2 as cv
import numpy as np

from bs4 import BeautifulSoup

from src.facade import Facade

show_img = False

"""
Author: Kurt Cieslinski
"""


def area(lst):
    return int(lst[2]) * int(lst[3])


def next_box(axis, boxes, mode):
    if mode == "y":
        upper_param = 1
        lower_param = 3
    elif mode == "x":
        upper_param = 0
        lower_param = 2
    else:
        raise Exception("Invalid mode!")

    dist_lower = []
    dist_upper = []
    for box in boxes:
        upper = abs(axis - box[upper_param])
        lower = abs(axis - (box[upper_param] + box[lower_param]))
        dist_lower.append(lower)
        dist_upper.append(upper)

    lower_min = min(dist_lower)
    upper_min = min(dist_upper)
    return 1 if lower_min < upper_min else -1


def box_dimension_avg(boxes):
    width_sum = 0
    height_sum = 0
    for box in boxes:
        width_sum += box[2]
        height_sum += box[3]

    return width_sum / len(boxes), height_sum / len(boxes)


def box_dimension_quant(boxes, quant):
    widths = [box[2] for box in boxes]
    heights = [box[3] for box in boxes]
    return np.quantile(widths, quant), np.quantile(heights, quant)


def calc_distances(boxes, width):
    distance_list = []
    for i in range(len(boxes) - 1):
        dist = abs(boxes[i][0] + width - boxes[i + 1][0])
        distance_list.append(dist)

    return distance_list


def med_anchor_y(boxes):
    anchor_y_list = [box[1] for box in boxes]
    return median(anchor_y_list)


def med_anchor_x(boxes):
    anchor_x_list = [box[0] for box in boxes]
    return median(anchor_x_list)


def remove_duplicates(boxes):
    checked_boxes = []
    for box in boxes:
        found_dup = False
        for checked_box in checked_boxes:
            if math.isclose(box[0], checked_box[0], abs_tol=3) and math.isclose(box[1], checked_box[1], abs_tol=3):
                found_dup = True
                break

        if not found_dup:
            checked_boxes.append(box)

    return checked_boxes


def check_intersection_line_box(axis, line_anchor, boxes):
    if axis == "y":
        anchor = 1
        length = 3
    elif axis == "x":
        anchor = 0
        length = 2
    else:
        raise Exception("Invalid mode!")

    for box in boxes:
        if box[anchor] <= line_anchor <= box[anchor] + box[length]:
            return True

    return False


def check_intersection_box_box(box1, box2):
    for x in range(box1[0], box1[0] + box1[2]):
        if box2[0] <= x <= box2[0] + box2[2]:
            for y in range(box1[1], box1[1] + box1[3]):
                if box2[1] <= y <= box2[1] + box2[3]:
                    return True
    return False


def find_bounding_boxes(color_filtered_img, bool_door):
    src_gray = cv.cvtColor(color_filtered_img, cv.COLOR_RGB2GRAY)
    src_gray = cv.blur(src_gray, (3, 3))

    se = cv.getStructuringElement(cv.MORPH_RECT, (9, 9))
    filtered_img = cv.morphologyEx(src_gray, cv.MORPH_OPEN, se)

    if show_img:
        cv.imshow("filtered_img", filtered_img)
        cv.waitKey()

    thresh = 20
    canny_output = cv.Canny(filtered_img, thresh, thresh * 2)
    contours, _ = cv.findContours(canny_output, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    rectangle_list = []
    for i, c in enumerate(contours):
        rectangle_list.append(cv.boundingRect(cv.approxPolyDP(c, 3, True)))
        # area_lst.append((area(boundRect), boundRect))

    merge_threshold = 8
    rectangle_margin_list = rectangle_list.copy()

    for i in range(len(rectangle_margin_list)):
        rec = rectangle_margin_list[i]
        rectangle_margin_list[i] = (
            rec[0] - merge_threshold, rec[1] - merge_threshold, rec[2] + 2 * merge_threshold,
            rec[3] + 2 * merge_threshold)

    tmp = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

    for box in rectangle_margin_list:
        color = (255, 255, 255)
        # cv.drawContours(img, contours_poly, i, color)
        cv.rectangle(tmp, (int(box[0]), int(box[1])),
                     (int(box[0] + box[2]), int(box[1] + box[3])), color, -1)

    src_gray = cv.cvtColor(tmp, cv.COLOR_BGR2GRAY)
    src_gray = cv.blur(src_gray, (3, 3))

    if show_img:
        cv.imshow("Black-white", src_gray)
        cv.waitKey()

    canny_output = cv.Canny(src_gray, thresh, thresh * 2)
    contours, _ = cv.findContours(canny_output, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    box_area_lst = []
    rectangle_margin_list = []
    for i, c in enumerate(contours):
        rectangle_margin_list.append(cv.boundingRect(cv.approxPolyDP(c, 3, True)))
        # area_lst.append((area(boundRect), boundRect))
    rectangle_list = rectangle_margin_list.copy()

    for i, val in enumerate(rectangle_margin_list):
        rectangle_list[i] = (
            val[0] + merge_threshold, val[1] + merge_threshold, val[2] - 2 * merge_threshold,
            val[3] - 2 * merge_threshold)

    for rec in rectangle_list:
        box_area_lst.append((rec, area(rec)))

    if len(box_area_lst) == 0:
        return None
    max_box = max([i[1] for i in box_area_lst])
    # quant = np.quantile([i[1] for i in box_area_lst], 0.05)

    # box_area_lst = list(filter(lambda x: x[1] >= quant, box_area_lst))

    if bool_door:
        box_area_lst = list(filter(lambda x: x[1] >= max_box * 0.6, box_area_lst))
    else:
        box_area_lst = list(filter(lambda x: x[1] >= max_box * 0.15, box_area_lst))

    rectangle_list = [rectangle_margin[0] for rectangle_margin in box_area_lst]
    rectangle_list = remove_duplicates(rectangle_list)

    if show_img:
        for box in rectangle_list:
            color = (255, 255, 255)
            # cv.drawContours(img, contours_poly, i, color)
            cv.rectangle(filtered_img, (int(box[0]), int(box[1])),
                         (int(box[0] + box[2]), int(box[1] + box[3])), color, 5)

        cv.imshow("filtered_img", filtered_img)
        cv.waitKey()

    return rectangle_list


def box_segment(img_path, xml):
    with open(xml, 'r') as f:
        config_xml = f.read()

    config_data = BeautifulSoup(config_xml, "xml")

    window_color = (None, None, None)
    door_color = (None, None, None)
    region_defs = config_data.find("regionDefinitions")
    for region in region_defs:
        if region != "\n":
            if region.get("name") == "window":
                color = region.get("color")
                lst = color.split(" ")
                window_color = tuple([int(i) for i in lst])
            if region.get("name") == "door":
                color = region.get("color")
                lst = color.split(" ")
                door_color = tuple([int(i) for i in lst])

    # img_path = "test.png"
    img = cv.imread(img_path)
    rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    windows_img = rgb.copy()
    door_img = rgb.copy()

    # windows_img = cv.morphologyEx(rgb, cv.MORPH_DILATE, se)
    # door_img = cv.morphologyEx(rgb, cv.MORPH_DILATE, se)

    windows_img[~np.all(windows_img == window_color, axis=-1)] = (0, 0, 0)
    door_img[~np.all(door_img == door_color, axis=-1)] = (0, 0, 0)

    window_rectangle_lst = find_bounding_boxes(windows_img, False)
    door_rectangle_lst = find_bounding_boxes(door_img, True)
    no_door = door_rectangle_lst is None

    if not no_door:
        for window in window_rectangle_lst:
            for door in door_rectangle_lst:
                if check_intersection_box_box(window, door):
                    window_rectangle_lst.remove(window)

    next_box_y_lst = []
    for y, _ in enumerate(img):
        next_box_y_lst.append(next_box(y, window_rectangle_lst, "y"))

    lines_y_lst = []
    prev_item = -1
    for i, val in enumerate(next_box_y_lst):
        if val != prev_item:
            lines_y_lst.append(i)
        prev_item = val

    lines_y_lst = [line for line in lines_y_lst if not check_intersection_line_box("y", line, window_rectangle_lst)]
    lines_y_lst.insert(0, 0)
    lines_y_lst.append(len(img))

    next_box_x_lst = []
    for x, _ in enumerate(img[0]):
        next_box_x_lst.append(next_box(x, window_rectangle_lst, "x"))

    lines_x_lst = []
    prev_item = -1
    for i, val in enumerate(next_box_x_lst):
        if val != prev_item:
            lines_x_lst.append(i)
        prev_item = val

    lines_x_lst = [line for line in lines_x_lst if not check_intersection_line_box("x", line, window_rectangle_lst)]
    lines_x_lst.insert(0, 0)
    lines_x_lst.append(len(img[0]))

    for y in lines_y_lst:
        cv.line(img, (0, y), (len(img[0]), y), (0, 0, 0), 2)

    for x in lines_x_lst:
        cv.line(img, (x, 0), (x, len(img)), (0, 0, 0), 2)

    if show_img:
        source_window = 'Source'
        cv.namedWindow(source_window)
        cv.imshow(source_window, img)
        cv.waitKey()

    num_floors = len(lines_y_lst) - 1
    num_windows_in_floor = len(lines_x_lst) - 1

    floor_lst = [[] for _ in range(num_floors)]
    for box in window_rectangle_lst:
        y = box[1]
        for i in range(num_floors):
            if lines_y_lst[i] <= y < lines_y_lst[i + 1]:
                floor_lst[i].append(box)
                break

    if [] in floor_lst:
        floor_lst.remove([])
    first_floor = floor_lst.pop()
    while len(first_floor) <= 1:
        first_floor = floor_lst.pop()

    column_list = [[] for _ in range(num_windows_in_floor)]
    for box in window_rectangle_lst:
        x = box[0]
        if box in first_floor:
            continue
        for i in range(num_windows_in_floor):
            if lines_x_lst[i] <= x < lines_x_lst[i + 1]:
                column_list[i].append(box)
                break

    if [] in column_list:
        column_list.remove([])

    height_anchor_y_lst = []
    for floor in floor_lst:
        _, quant_height = box_dimension_quant(floor, 0.60)
        height_anchor_y_lst.append((quant_height, med_anchor_y(floor)))

    height_anchor_y_lst.sort(key=lambda x: x[1])

    first_floor_dim = box_dimension_quant(first_floor, 0.60)
    first_floor_y_anchor = med_anchor_y(first_floor)
    first_floor_x_anchor_lst = [box[0] for box in first_floor]
    first_floor_x_anchor_lst.sort()
    first_floor_anchor = (first_floor_x_anchor_lst, first_floor_y_anchor)

    width_anchor_x_lst = []
    for column in column_list:
        quant_width, _ = box_dimension_quant(column, 0.60)
        width_anchor_x_lst.append((quant_width, med_anchor_x(column)))

    width_anchor_x_lst.sort(key=lambda x: x[1])

    """
    dist_list = []
    for i, floor in enumerate(floor_lst):
        dist_list.extend(calc_distances(floor, width))
    
    distance = median(dist_list)
    """

    img = cv.imread(img_path)

    # draw
    """
    for floor in floor_lst:
        for box in floor:
            color = (255, 255, 255)
            cv.rectangle(img, (int(box[0]), int(box[1])),
                         (int(box[0] + box[2]), int(box[1] + box[3])), color, 2)
    """

    facade = Facade(width_anchor_x_lst, height_anchor_y_lst, first_floor_anchor, first_floor_dim, door_rectangle_lst,
                    (len(img[0]), len(img)))

    window_box_color = (255, 255, 255)
    img = facade.draw_facade(img, window_box_color, door_color)

    """
    for y, floor in enumerate(floor_lst):
        next_anka = min([digit[0] for digit in floor])
        for x in range(num_windows_in_floor):
            color = (0, 255, 255)
            cv.rectangle(img, (int(next_anka), int(anchor_y_lst[y])),
                         (int(next_anka + width), int(anchor_y_lst[y] + height)), color, 2)
            next_anka = next_anka + width + distance
    """

    if show_img:
        source_window = 'Source'
        cv.namedWindow(source_window)
        cv.imshow(source_window, img)
        cv.waitKey()

    cv.imwrite(str(img_path[:img_path.rfind(".stage3")]) + "_predBox.png", img)

    return facade
