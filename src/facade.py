import json

import cv2 as cv

"""
Author: Kurt Cieslinski
"""


class Facade:
    def __init__(self, width_anchor_x_lst=None, height_anchor_y_lst=None, first_floor_anchor=([], 0),
                 first_floor_dim=(0, 0), door_rectangle=None,
                 dim=(0, 0), lot=None):
        if door_rectangle is None:
            door_rectangle = []
        if height_anchor_y_lst is None:
            height_anchor_y_lst = []
        if width_anchor_x_lst is None:
            width_anchor_x_lst = []
        self.width_anchor_x_lst = width_anchor_x_lst
        self.height_anchor_y_lst = height_anchor_y_lst
        self.first_floor_x_anchor_lst = first_floor_anchor[0]
        self.first_floor_y_anchor = first_floor_anchor[1]
        self.first_floor_dim = first_floor_dim
        self.door_rectangle_lst = door_rectangle
        self.width = dim[0]
        self.height = dim[1]
        self.lot = lot

    def draw_facade(self, img, color_window, color_door):
        for width_anchor_x in self.width_anchor_x_lst:
            for height_anchor in self.height_anchor_y_lst:
                cv.rectangle(img, (int(width_anchor_x[1]), int(height_anchor[1])),
                             (int(width_anchor_x[1] + width_anchor_x[0]),
                              int(height_anchor[1] + height_anchor[0])), color_window, 2)

        if self.door_rectangle_lst is not None:
            for box in self.door_rectangle_lst:
                cv.rectangle(img, (int(box[0]), int(box[1])), (int(box[0] + box[2]), int(box[1] + box[3])), color_door,
                             2)

        for x in self.first_floor_x_anchor_lst:
            cv.rectangle(img, (int(x), int(self.first_floor_y_anchor)),
                         (int(x + self.first_floor_dim[0]), int(self.first_floor_y_anchor + self.first_floor_dim[1])),
                         color_window, 2)

        return img

    def generate_json(self):
        windows = []
        for width_anchor_x in self.width_anchor_x_lst:
            for height_anchor in self.height_anchor_y_lst:
                windows.append({"anchor": (int(width_anchor_x[1]), int(height_anchor[1])),
                                "width": width_anchor_x[0],
                                "height": height_anchor[0]})

        for x in self.first_floor_x_anchor_lst:
            windows.append({"anchor": (int(x), int(self.first_floor_y_anchor)),
                            "width": self.first_floor_dim[0],
                            "height": self.first_floor_dim[1]})

        doors = []
        if self.door_rectangle_lst is not None:
            for box in self.door_rectangle_lst:
                doors.append({"anchor": (int(box[0]), int(box[1])),
                              "width": box[2],
                              "height": box[3]})

        facade = {"width": self.width,
                  "height": self.height,
                  "lot": self.lot,
                  "windows": windows,
                  "doors": doors}

        return json.dumps(facade)

    def read_json(self, json_path):

        json_file = open(json_path, "r")
        facade = json.loads(json_file.read())
        json_file.close()

        self.width = facade["width"]
        self.height = facade["height"]

        self.door_rectangle_lst = []
        doors = facade["doors"]
        for door in doors:
            x = door["anchor"][0]
            y = door["anchor"][1]
            width = door["width"]
            height = door["height"]
            self.door_rectangle_lst.append((x, y, width, height))

        windows = facade["windows"]
        self.first_floor_y_anchor = max([w["anchor"][1] for w in windows])
        self.first_floor_x_anchor_lst = [w["anchor"][0] for w in windows if w["anchor"][1] == self.first_floor_y_anchor]

        first_floor_dim = (0, 0)
        for w in windows:
            if w["anchor"][1] == self.first_floor_y_anchor:
                first_floor_dim = (w["width"], w["height"])
                break
        self.first_floor_dim = first_floor_dim

        windows = [w for w in windows if w["anchor"][1] != self.first_floor_y_anchor]

        width_anchor_x = [(w["width"], w["anchor"][0]) for w in windows]
        height_anchor_y = [(w["height"], w["anchor"][1]) for w in windows]

        self.width_anchor_x_lst = list(set(width_anchor_x))
        self.width_anchor_x_lst.sort(key=lambda x: x[1])
        self.height_anchor_y_lst = list(set(height_anchor_y))
        self.height_anchor_y_lst.sort(key=lambda x: x[1])
