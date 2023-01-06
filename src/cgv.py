NULL = "null"
THIS = "this"
START = "Start -->"


def noun(name):
    return name + " -->"


def point2(x, y):
    return "point2(" + str(x) + "," + str(y) + ")"


def point3(x, y, z):
    return "point2(" + str(x) + "," + str(y) + "," + str(z) + ")"


def face(*p):
    if type(p[0]) is list:
        p = p[0]
    if len(p) < 3:
        raise Exception("Too less points!")

    face_string = "face(\n\t "
    for point in p:
        face_string += point + ",\n\t "
    face_string = face_string.removesuffix(",\n\t ")
    return face_string + "\n\t)"


def line(p1, p2):
    return "line(" + p1 + "," + p2 + ")"


def extrude(height):
    return "extrude(" + str(height) + ")"


def split(axis, repeat, *size):
    """

    @param axis: split axis
    @param repeat: "false": single split, "true": repeated split (infinite), <int>: num of splits
    @param size: size between splits
    @return: split string
    """
    if len(size) < 1:
        raise Exception("Too less splits")
    if type(size[0]) is list:
        size = size[0]
        if len(size) < 1:
            raise Exception("Too less splits")

    split_string = "split(\n\t \"" + axis + "\",\n\t " + str(repeat)
    for s in size:
        split_string += ",\n\t " + str(s)

    return split_string + "\n\t)"


def if_else(cond, then, el):
    return "if\n\t " + cond + "\n\tthen {\n\t " + then + "\n\t} else {\n\t " + el + "\n\t}"


def color(col):
    return "color(\"" + col + "\")"


def switch_case(condition, *case_then_tuple):
    switch_case_string = "switch " + condition + "{ "
    for case in case_then_tuple:
        switch_case_string += "case " + case[0] + ": " + case[1] + " "

    return switch_case_string + "}"


def to_faces():
    return "toFaces()"


def to_points():
    return "toPoints()"


def to_lines():
    return "toLines()"


def equal(arg1, arg2):
    return str(arg1) + " == " + str(arg2)


def unequal(arg1, arg2):
    return str(arg1) + " != " + str(arg2)


def greater(arg1, arg2):
    return str(arg1) + " > " + str(arg2)


def greater_equal(arg1, arg2):
    return str(arg1) + " >= " + str(arg2)


def smaller(arg1, arg2):
    return str(arg1) + " < " + str(arg2)


def smaller_equal(arg1, arg2):
    return str(arg1) + " <= " + str(arg2)


def and_o(arg1, arg2):
    return arg1 + " && " + arg2


def or_o(arg1, arg2):
    return arg1 + " || " + arg2


def not_o(arg):
    return "!" + arg


def invert(arg):
    return "-" + str(arg)


def add(arg1, arg2):
    return str(arg1) + " + " + str(arg2)


def subtract(arg1, arg2):
    return str(arg1) + " - " + str(arg2)


def multiply(arg1, arg2):
    return str(arg1) + " * " + str(arg2)


def divide(arg1, arg2):
    return str(arg1) + " \\ " + str(arg2)


def modulo(arg1, arg2):
    return str(arg1) + " % " + str(arg2)


def id():
    return "id()"


def rotate(x, y, z):
    return "rotate(" + str(x) + "," + str(y) + "," + str(z) + ")"


def translate(x, y, z):
    return "translate(" + str(x) + "," + str(y) + "," + str(z) + ")"


def index():
    return "index()"


def sample(i):
    return "sample(" + str(i) + ")"


def size(axis):
    return "size(\"" + axis + "\")"


def load(arg):
    return "load(" + arg + ")"


def random_float(lower, upper):
    return "randomFloat(" + str(lower) + "," + str(upper) + ")"


def select(arg1, arg2):
    return "select(" + str(arg1) + "," + str(arg2) + ")"


def scale(x, y, z):
    return "scale(" + str(x) + "," + str(y) + "," + str(z) + ")"


def expand_graph(arg):
    return "expandGraph(" + str(arg) + ")"


def gable_roof(rot):
    return "gableRoof(" + str(rot) + ")"


def direction():
    return "direction()"


def get_variable(var):
    return THIS + "." + var


def after(before_insert, after_insert):
    if before_insert.endswith("-->"):
        return before_insert + " \n\t" + after_insert
    return before_insert + " -> \n\t" + after_insert


def before(to_insert, into):
    split_i = into.rfind("->")
    return into[:split_i + 2] + " " + to_insert + " ->" + into[split_i + 2:]


def parallel(arg1, arg2):
    return arg1 + " | " + arg2
