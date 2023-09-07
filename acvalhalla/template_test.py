import cv2
import os

from cv2_utils import *

script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
test_images_dir = os.path.join(images_dir, "tests")

test_menus = {
    "mainmenu_2k": cv2.imread(os.path.join(test_images_dir, "menu_test_2k.png"), cv2.IMREAD_UNCHANGED),
    "menu_2k": cv2.imread(os.path.join(test_images_dir, "main_menu_2k.png"), cv2.IMREAD_UNCHANGED),
    "menu_1080": cv2.imread(os.path.join(test_images_dir, "1080_mainmenu_27inch4kscreen.png"), cv2.IMREAD_UNCHANGED),
}

# found = locate_in_image(get_template('press_any'), test_menus['mainmenu_2k'], debug = 0)
# print(found)
found = locate_in_image(get_template('benchmark'), test_menus['menu_1080'], debug=1, threshold=0.8)
print(found)
