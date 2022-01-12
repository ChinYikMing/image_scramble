#!/usr/local/bin/python3
import os
from os import environ
import getopt
import sys
import re
import random
import face_recognition
from matplotlib import pyplot as plt
from PIL import Image
from image_slicer import slice, join 
import numpy as np
from math import sqrt, ceil, floor

def totuple(a):
    try:
        return tuple(totuple(i) for i in a)
    except TypeError:
        return a

def my_calc_columns_rows(n):
    num_columns = int(ceil(sqrt(n)))
    num_rows = int(ceil(n / float(num_columns)))
    return (num_columns, num_rows)


def my_get_combined_size(tiles):
    columns, rows = my_calc_columns_rows(len(tiles))
    tile_size = tiles[0].image.size
    return (tile_size[0] * columns, tile_size[1] * rows)


def my_join(tiles, orders, width=0, height=0):
    if width > 0 and height > 0:
        im = Image.new("RGBA", (width, height), None)
    else:
        im = Image.new("RGBA", my_get_combined_size(tiles), None)
    columns, rows = my_calc_columns_rows(len(tiles))
    for tile, order in zip(tiles, orders):
        try:
            im.paste(tile.image, order)
        except IOError:
            continue
    return im

def is_scrambled_img(path):
    return path.startswith("s_")

def is_dir(path):
    return os.path.isdir(path) and path.endswith("\\")

def is_png_img(path):
    return os.path.isfile(path) and path.endswith(".png")

def delete_all_scramble(dir):
    cnt = 0
    for scrambled_img in os.listdir(dir): # scrambled_img prefixed with 's_'
        if is_png_img(dir + scrambled_img) and is_scrambled_img(scrambled_img):
            os.remove(dir + scrambled_img)
            print("'" + scrambled_img + "' has been deleted")
            cnt += 1

    if cnt == 0:
        print("None scrambled image found")

    exit()

def show_coor(img):
    print("Please record down your desired x-y(x1,x2,y1,y2) coordinates for scrambling later")
    plt.imshow(plt.imread(img))
    plt.show()
    # print("run again with specified x-y coordinates with -x and -y options")
    # print("Note: remove the -s option")
    exit()

def usage(script_name):
    print("python %s -a img_directory_name | -f img_filename -r img_row -c img_col [optional -x x1,x2 -y y1,y2] [optional -s img_to_show_coor] [optional -d img_directory_name]" % script_name)
    # print("\noptional parameter:")
    # print("-s img_to_show_coor, this parameter is used to show coordinates of the specified 'img_to_show_coor' png image file")
    # print("-x x1,x2 and -y y1,y2, these two parameters are used to specified the rectangle to be scrambled. If not specified, default will scramble the whole image")
    # print("-d img_directory_name, this parameter is used to delete all scramble image with name prefixed with 's_' in specified 'img_directory_name'")
    # print("\nNote:")
    # print("1. cannot use -a and -f options together")
    # print("2. cannot use -s option when scrambling images")
    exit()

def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

# opt_all_dir and opt_img_filename are mutual exclusive
opt_img_del_dir = None
opt_img_dir = None
opt_img_filename = None
opt_img_row = None
opt_img_col = None
opt_img_coor = None
opt_img_x1 = None
opt_img_x2 = None
opt_img_y1 = None
opt_img_y2 = None

def parse_options():
    global opt_img_del_dir
    global opt_img_dir
    global opt_img_filename
    global opt_img_row
    global opt_img_col
    global opt_img_coor
    global opt_img_x1
    global opt_img_x2
    global opt_img_y1
    global opt_img_y2

    x = None
    y = None
    opt_img_del_dir = None
    opt_img_dir = None
    opt_img_filename = None
    opt_img_coor = None
    opt_img_row = None
    opt_img_col = None

    script_name = sys.argv[0]
    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:f:r:c:s:x:y:d:h")
    except getopt.GetoptError as err:
        print(err)
        print("\n")
        usage(script_name)

    for opt, arg in opts:
        if opt in ['-a']:
            if opt_img_filename != None or not is_dir(arg):
                print("invalid directory name(wrong directory spelling or not a directory)")
                exit()
            elif opt_img_del_dir != None:
                print("Cannot use -d and -a option together")
                exit()
            opt_img_dir = arg
        elif opt in ['-f']:
            if opt_img_dir != None or is_dir(arg) or not is_png_img(arg):
                print("invalid image file(wrong image spelling or not a png image)")
                exit()
            elif opt_img_del_dir != None:
                print("Cannot use -d and -f option together")
                exit()
            opt_img_filename = arg
        elif opt in ['-r']:
            opt_img_row = int(arg)
        elif opt in ['-c']:
            opt_img_col = int(arg)
        elif opt in ['-s']:
            if opt_img_del_dir != None:
                print("Cannot use -d and -s option together")
                exit()
            elif not is_png_img(arg):
                print("invalid image file(wrong image spelling or not a png image)")
                exit()
            opt_img_coor = arg
        elif opt in ['-x']:
            match = re.match("^[0-9]+,[0-9]+$", arg)
            if match == None:
                print("invalid x coordinates format, format: x1,x2")
                exit()
            x = arg.split(",")
            opt_img_x1 = int(x[0])
            opt_img_x2 = int(x[1])
        elif opt in ['-y']:
            match = re.match("^[0-9]+,[0-9]+$", arg)
            if match == None:
                print("invalid y coordinates format, format: y1,y2")
                exit()
            y = arg.split(",")
            opt_img_y1 = int(y[0])
            opt_img_y2 = int(y[1])
        elif opt in ['-d']:
            if not is_dir(arg):
                print("invalid directory name(wrong directory spelling or not a directory)")
                exit()
            elif opt_img_coor != None:
                print("Cannot use -d and -s option together")
                exit()
            elif opt_img_dir != None:
                print("Cannot use -d and -a option together")
                exit()
            elif opt_img_filename != None:
                print("Cannot use -d and -f option together")
                exit()
            opt_img_del_dir = arg
        elif opt in ['-h']:
            usage(script_name)

    if opt_img_del_dir != None:
        delete_all_scramble(opt_img_del_dir)

    if opt_img_coor != None:
        show_coor(opt_img_coor)

    if opt_img_dir == None and opt_img_filename == None:
        print("Please specified image file(use -f option) or directory(use -a option)")
        exit()

    if opt_img_row == None or opt_img_col == None:
        print("Please specified scrambled row(use -r option) and col(use -c option)")
        exit()

    if (opt_img_x1 != None and opt_img_x2 != None and opt_img_y1 == None and opt_img_y2 == None) or \
        (opt_img_x1 == None and opt_img_x2 == None and opt_img_y1 != None and opt_img_y2 != None):
        print("cannot specified either x or y coordinates individually (x-y coordinates should be specified together)")
        exit()

def scramble_img_and_save(img_filename, img_row, img_col, x1=None, x2=None, y1=None, y2=None):
    dirname = os.path.dirname(img_filename)
    basename = os.path.basename(img_filename)

    if x1 != None and x2 != None and y1 != None and y2 != None:
        img = Image.open(img_filename).resize((2133, 1600)) # let all image in directory have same x-y coordinates
        (left, upper, right, lower) = (x1, y1, x2, y2)
        face = img.crop((left, upper, right, lower)) 
        face.save("tmp.png")

        tiles = slice("tmp.png", row=img_row, col=img_col, save=False)

        orders = list()
        for t, i in zip(tiles, range(len(tiles))):
            orders.insert(i, t.coords)
        orders = tuple(orders)
        # print(orders)

        tiles_arr = np.asarray(tiles)
        random.shuffle(tiles_arr)
        tiles_new = totuple(tiles_arr)
        res = my_join(tiles_new, orders)

        img_cpy = img.copy()
        img_cpy.paste(res, (left, upper))
        img_cpy.save(dirname + "\s_" + basename)

    else: # default scramble whole image
        tiles = slice(img_filename, row=img_row, col=img_col, save=False)

        orders = list()
        for t, i in zip(tiles, range(len(tiles))):
            orders.insert(i, t.coords)
        orders = tuple(orders)
        # print(orders)

        tiles_arr = np.asarray(tiles)
        random.shuffle(tiles_arr)
        tiles_new = totuple(tiles_arr)
        res = my_join(tiles_new, orders)
        res.save(dirname + "\s_" + basename)

if __name__ == "__main__":
    suppress_qt_warnings()
    parse_options()

    if opt_img_dir != None:  # multiple image
        for filename in os.listdir(opt_img_dir):
            filename = opt_img_dir + filename
            if filename.endswith(".png"):
                if opt_img_x1 != None and opt_img_x2 != None and opt_img_y1 != None and opt_img_y2 != None:
                    scramble_img_and_save(filename, opt_img_row, opt_img_col, opt_img_x1, opt_img_x2, opt_img_y1, opt_img_y2)
                else:
                    scramble_img_and_save(filename, opt_img_row, opt_img_col)

    else: # single image 
        if opt_img_x1 != None and opt_img_x2 != None and opt_img_y1 != None and opt_img_y2 != None:
            scramble_img_and_save(opt_img_filename, opt_img_row, opt_img_col, opt_img_x1, opt_img_x2, opt_img_y1, opt_img_y2)
        else:
            scramble_img_and_save(opt_img_filename, opt_img_row, opt_img_col)

    if opt_img_x1 != None and opt_img_x2 != None and opt_img_y1 != None and opt_img_y2 != None:
        os.remove("tmp.png")