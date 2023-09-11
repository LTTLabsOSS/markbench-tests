import cv2
import os

from cv2_utils import *

script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
test_images_dir = os.path.join(images_dir, "tests")

test_menus = {
    "mainmenu_2k": cv2.imread(os.path.join(test_images_dir, "mainmenu_2k.png"), cv2.IMREAD_UNCHANGED),
    "graphicsmenu_2k": cv2.imread(os.path.join(test_images_dir, "graphicsmenu_2k.png"), cv2.IMREAD_UNCHANGED),
    "mainmenu_4k": cv2.imread(os.path.join(test_images_dir, "mainmenu_4k.png"), cv2.IMREAD_UNCHANGED),
    "mainmenu_1": cv2.imread(os.path.join(test_images_dir, "menu1.png"), cv2.IMREAD_UNCHANGED),
    "mainmenu_2": cv2.imread(os.path.join(test_images_dir, "menu2.png"), cv2.IMREAD_UNCHANGED),
    "mainmenu_3": cv2.imread(os.path.join(test_images_dir, "menu3.png"), cv2.IMREAD_UNCHANGED),
    "mainmenu_4": cv2.imread(os.path.join(test_images_dir, "menu4.png"), cv2.IMREAD_UNCHANGED),
    "16:10MainMenu": cv2.imread(os.path.join(test_images_dir, "main_menu_1920x1200.png"), cv2.IMREAD_UNCHANGED)
}


found2 = locate_in_image(get_template('menu_options'), test_menus['mainmenu_4k'], threshold=0.8, debug=0)
print(found2)
