import glob
import math
import os
import shutil
import timeit

import numpy as np

from src.osm import get_lot
from src.render_prediction import render_predictions
from src.box_segment import box_segment
from src.facade import Facade
from src.translate_grammar import translate_grammar
import cv2 as cv
from src.cut_facades import cut_facade

import lib.Panorama_Rectification.Batch_Simon_Panoramas_final as pr
import matlab.engine
import urllib.request

CONFIG = "config/etrimsConfigFile.xml"
TEST_LIST = "testList.txt"
TMP = "../tmp/"
STAGES = 3


def cut_street_pavement(img):
    y = len(img)

    pixel_per_row = [None] * y
    all_pixel = 0

    first_after_halve = int(y / 2)
    for i in range(y):
        row = img[i]
        pixel_count = 0
        for pixel in row:
            color = (pixel[0], pixel[1], pixel[2])
            if color == (0, 64, 128) or color == (128, 128, 128):
                pixel_count += 1
                if first_after_halve == int(y / 2) and i > int(y / 2):
                    first_after_halve = i

        pixel_per_row[i] = pixel_count
        all_pixel += pixel_count

    q = all_pixel * 0.95
    pixel_count = 0
    for i in range(y - 1, int(y / 2), -1):
        pixel_count += pixel_per_row[i]
        if q <= pixel_count:
            print(i)
            return i

    print("Halve")
    return first_after_halve


def cp_rectified_img(pan_name, angle):
    pan = "../lib/Panorama_Rectification/out/Pano_refine/" + pan_name

    suffix = "_VP_0_0" if angle < 0 else "_VP_0_1"

    os.system("cp " + pan + suffix + ".jpg" + " ../img/")
    os.system("mogrify -auto-orient -format png ../img/*.jpg")
    os.system("rm ../img/*.jpg")

    return pan_name + suffix


def check_routed(pan_name, angle):
    file = "../out/" + pan_name
    file += "_VP_0_0" if angle < 0 else "_VP_0_1"
    file += "_grammar.cgv"
    try:
        f = open(file)
        f.close()
        return file
    except FileNotFoundError:
        return ""


def check_rectified(pan_name, angle):
    file = "../lib/Panorama_Rectification/out/Pano_refine/" + pan_name
    file += "_VP_0_0.jpg" if angle < 0 else "_VP_0_1.jpg"
    try:
        f = open(file)
        f.close()
        return "found"
    except FileNotFoundError:
        return ""


def cleanup():
    os.system('rm -rf ../lib/Panorama_Rectification/Pano_input/')
    os.system("mkdir ../lib/Panorama_Rectification/Pano_input/")

    os.system('rm -rf ../img/')
    os.system("mkdir ../img/")

    os.system('rm ' + TEST_LIST)

    os.system('rm -rf ' + TMP + '*')
    os.system('rm -rf ../cache')
    os.system('rm tmp.sh')

    dirs = ["../img", "../out", "../out/auxFeatures", "../lib/Panorama_Rectification/Pano_hl_z_vp",
            "../lib/Panorama_Rectification/Pano_refine", "../lib/Panorama_Rectification/Rendering"]

    for check_dir in dirs:
        if not os.path.isdir(check_dir):
            os.mkdir(check_dir)


def calc_selected_point(angle, width):
    fov = 154 *2
    t = math.degrees(abs(angle)) - (90 - (fov / 2))
    p = (1 - t / fov) if angle > 0 else t / fov
    return p * width



def img_rot(angle, pan_angle):
    pi = np.pi
    r = math.fmod((angle - (pan_angle - 270) * pi / 180), (2 * pi)) + pi
    if r > pi:
        r -= 2 * pi
    if r < -pi:
        r += 2 * pi

    return r


def parse_pan_angle(pan_name):
    tmp = pan_name.split(",")
    tmp = tmp[len(tmp) - 1]

    return float(tmp)


def parse_lat_long(pan_name):
    tmp = pan_name.split("@")
    tmp = tmp[1].split(",")
    lat = float(tmp[0])
    long = float(tmp[1])

    return lat, long


def start_processing(pan, angle):
    p = os.path.split("/")

    os.chdir("src")
    # os.system("export DARWIN="$PWD"")
    # os.system("export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${DARWIN}/external/opencv/lib")
    cleanup()

    start = timeit.default_timer()

    pan_name = pan.split("/")
    pan_name = pan_name[len(pan_name) - 1]
    pan_name = str(pan_name[:pan_name.rfind(".png")])

    pan_angle = parse_pan_angle(pan_name)

    pan_rot = img_rot(angle, pan_angle)

    rectified = True if check_rectified(pan_name, pan_rot) != "" else False

    check = check_routed(pan_name, pan_rot)
    if check != "":
        with open(check, 'r') as file:
            data = file.read().replace('\n', '')
            print("check")
            os.chdir("..")
            return data

    pan_local_ref = "../lib/Panorama_Rectification/Pano_input/" + pan_name + ".png"
    urllib.request.urlretrieve(pan, "../lib/Panorama_Rectification/Pano_input/" + pan_name + ".png")

    time_rectify = 0
    if not rectified:
        start_rectify = timeit.default_timer()
        pr.render_facades("../lib/Panorama_Rectification/")
        stop_rectifiy = timeit.default_timer()
        time_rectify = stop_rectifiy - start_rectify

    start2 = timeit.default_timer()


    rectified_pan = cp_rectified_img(pan_name, pan_rot)

    pan_local = cv.imread("../img/" + rectified_pan + ".png")
    width = len(pan_local[0])

    clicked_house = calc_selected_point(pan_rot, width)

    print(rectified_pan)

    """
    os.system("cp -a ../lib/Panorama_Rectification/Pano_new/Pano_refine/. ../img/")
    os.system("mogrify -auto-orient -format png ../img/*.jpg")
    os.system("rm ../img/*.jpg")
    os.system("find ../img/ -name '*_VP_1_*' -delete")
    os.system("mogrify -quality 50% ../img/*")
    """

    # print(clicked_house)

    cut_facade("../img/" + rectified_pan + ".png", clicked_house)

    os.system('rm ' + TEST_LIST)
    imgFile = open(TEST_LIST, "w")
    imgFile.write(rectified_pan)
    imgFile.close()

    stop2 = timeit.default_timer()

    os.system('rm -rf ' + TMP + '*')
    os.system('rm -rf ../cache')
    os.system('rm tmp.sh')

    start3 = timeit.default_timer()

    eng = matlab.engine.start_matlab()
    # eng.cd(r"src", nargout=0)

    eng.createTmpXML(CONFIG, STAGES, TMP, nargout=0)
    for i in range(1, STAGES + 1):
        print("Stage " + str(i) + ":")
        xml = TMP + "_stage" + str(i) + ".xml"
        eng.facadeSeg(xml, TMP, i, TEST_LIST, nargout=0)
        os.system("./tmp.sh")

    eng.quit()

    os.system('rm -rf ' + TMP + '*')
    os.system('rm -rf ../cache')
    os.system('rm tmp.sh')

    stop3 = timeit.default_timer()
    start4 = timeit.default_timer()

    pred_list = glob.glob('../out/' + rectified_pan + '.*.txt')
    for pred in pred_list:
        if "pot.txt" in pred:
            continue
        render_predictions(pred, CONFIG)

    pred = '../out/' + rectified_pan + '.stage3.projMultiSeg6_pred.png'

    img = cv.imread(pred)
    cut = cut_street_pavement(img)
    img = img[:cut, :]
    path = str(pred[:pred.rfind(".png")]) + "_cut.png"
    cv.imwrite(path, img)

    img_path_png = "../out/" + rectified_pan + ".stage3.projMultiSeg6_pred_cut.png"

    # facade = Facade()
    # facade.read_json(img_path + ".json")

    facade = box_segment(img_path_png, CONFIG)
    lat, long = parse_lat_long(pan_name)
    facade.lot = get_lot(angle, (lat, long))

    json = facade.generate_json()
    json_file = open("../out/" + rectified_pan + ".json", "w")
    json_file.write(json)
    json_file.close()

    grammar = translate_grammar(facade, (lat, long))
    grammar_file = open("../out/" + rectified_pan + "_grammar.cgv", "w")
    grammar_file.write(grammar)
    grammar_file.close()
    stop4 = timeit.default_timer()

    stop = timeit.default_timer()
    time = stop - start
    time2 = stop2 - start2
    time3 = stop3 - start3
    time4 = stop4 - start4
    print("Time: " + str(time) + ", rectify: " + str(time_rectify) + ", Time2: " + str(time2) + ", Time3: " + str(
        time3) + ", Time4: " + str(time4))

    os.chdir("..")
    return grammar


if __name__ == '__main__':
    start_processing("Panorama_Rectification/Pano_new/New/images/img.png", 4096 / 2)
