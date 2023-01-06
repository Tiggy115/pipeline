from PIL import Image
from bs4 import BeautifulSoup


def get_color_dic(xml):
    with open(xml, 'r') as f:
        config_xml = f.read()

    config_data = BeautifulSoup(config_xml, "xml")

    dic = dict()
    region_defs = config_data.find("regionDefinitions")
    for region in region_defs:
        if region != "\n":
            color_id = region.get("id")
            color = region.get("color")
            lst = color.split(" ")
            dic[color_id] = tuple([int(i) for i in lst])
    return dic


def render_predictions(filename, xml):
    color_dic = get_color_dic(xml)

    label_file = open(filename, "r")

    height = 0
    width = 0

    for line in label_file:
        if height == 0:  # first iteration
            width = len(line.replace(" ", "").replace("\n", ""))
        else:
            if width != len(line.replace(" ", "").replace("\n", "")):
                raise Exception("Wrong input type! (width)")
        height += 1

    img = Image.new("RGB", size=(width, height))

    label_file = open(filename, "r")
    y = 0
    for line in label_file:
        x = 0
        line_cut = line.replace(" ", "").replace("\n", "")
        for row in line_cut:
            id = color_dic.get(row)
            img.putpixel((x, y), id)
            x += 1
        y += 1

    img_name = filename.replace(".txt", "") + "_pred.png"
    img.save(img_name)
