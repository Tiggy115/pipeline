from __future__ import division
from __future__ import print_function

import math
from statistics import median
import cv2 as cv
import numpy as np
from lib.sky_detector import detector


def lowest_not_black(img):
    for i in range(len(img) - 1, -1, -1):
        row = img[i]
        for pixel in row:
            color = (pixel[0], pixel[1], pixel[2])
            if color != (0, 0, 0):
                return i


def cut_facade(img_path, selection):
    filename = img_path
    img = cv.imread(filename)

    src = img  # cv.cvtColor(enhanced_img, cv.COLOR_BGR2GRAY)

    blur = cv.GaussianBlur(src, (5, 5), 1)
    dst = cv.Canny(blur, 50, 100, None, 3)
    cv.imwrite("dst_" + img_path, dst)

    cdstP = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)
    # cdstP = np.copy(dst)

    tmp = np.zeros((cdstP.shape[0], cdstP.shape[1], 3), dtype=np.uint8)
    for i in range(50, 80, 2):
        linesP = cv.HoughLinesP(dst, 1, np.pi / 180, i, None, 35, 15)

        if linesP is not None:
            for i in range(0, len(linesP)):
                l = linesP[i][0]
                angle = np.arctan2(l[3] - l[1], l[2] - l[0]) * 180.0 / np.pi
                if 87 <= abs(angle) <= 93 or 267 <= abs(angle) <= 273:
                    cv.line(tmp, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv.LINE_AA)

    kernel = np.ones((2, 2))
    tmp_dilate = cv.dilate(tmp, kernel, iterations=4)
    tmp_erode = cv.erode(tmp_dilate, kernel, iterations=4)

    imgray = cv.cvtColor(tmp_erode, cv.COLOR_BGR2GRAY)
    contours, hierarchy = cv.findContours(imgray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    contour_area = []
    for cnt in contours:
        x, y, w, h = cv.boundingRect(cnt)

        contour_area.append((cnt, h))

    max_h = max([cnt[1] for cnt in contour_area])
    # q = np.quantile([i[1] for i in contour_area], 0.975)

    contours_filtered = []
    factor = 0.8
    while len(contours_filtered) < 3:
        contours_filtered = [c[0] for c in contour_area if c[1] >= factor * max_h]
        factor -= 0.01
    # contours_filtered = [c[0] for c in contour_area if c[1] >= q]

    contours = contours_filtered

    cv.drawContours(cdstP, contours, -1, (0, 255, 0), 3)

    crop_lines = []
    rows, cols = cdstP.shape[:2]
    for cnt in contours:
        [vx, vy, x, y] = cv.fitLine(cnt, cv.DIST_FAIR, 0, 0.01, 0.01)
        left_y = int((-x * vy / vx) + y)
        right_y = int(((cols - x) * vy / vx) + y)
        angle = np.arctan2(left_y - right_y, -cols - 1) * 180.0 / np.pi
        if 80 <= abs(angle) <= 100 or 260 <= abs(angle) <= 280:
            X = [p[0][0] for p in cnt]
            med = int(median(X))
            crop_lines.append(med)
            cv.line(cdstP, (med, 0), (med, rows - 1), (0, 0, 255), 2)
            try:
                # cv.line(cdstP, (cols - 1, right_y), (0, left_y), (0, 255, 0), 2)
                pass
            except cv.error:
                pass

    selection = len(src[0]) / 2 if selection is None else selection
    cv.line(cdstP, (int(selection), 0), (int(selection), rows - 1), (0, 255, 0), 2)
    cv.imwrite("cdstP.png", cdstP)

    crop_lines.sort()
    crop_line_index = 0
    if len(crop_lines) > 2:
        for i in range(0, len(crop_lines) - 1):
            if crop_lines[i] <= selection <= crop_lines[i + 1]:
                crop_line_index = i
                break

    if crop_lines[len(crop_lines) - 1] <= selection:
        crop_line_index = len(crop_lines) - 2

    img_cropped = src[:, crop_lines[crop_line_index]:crop_lines[crop_line_index + 1]]

    # detect sky
    sky = detector.get_sky_region_gradient(img_cropped)

    crop_sky = lowest_not_black(sky)
    img_cropped = img_cropped[crop_sky:, :]

    # cv.imshow("Source", src)
    # cv.imwrite("source.png", src)
    # cv.imwrite("tmp_erode.png", tmp_erode)
    cv.imwrite(img_path, img_cropped)
    cv.imwrite("tmp.png", tmp)

    # cv.imshow("Detected Lines (in red) - Standard Hough Line Transform", cdst)
    # cv.imwrite("cdst.png", cdst)
    # cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", cdstP)

    # cv.waitKey()


if __name__ == '__main__':
    cut_facade("panorama-83aejlYnx_Y7Q-8Jn-6d2g-3_VP_0_1.png", None)
