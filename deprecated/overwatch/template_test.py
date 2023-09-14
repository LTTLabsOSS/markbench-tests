import cv2
import os

from cv2_utils import *

script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
test_images_dir = os.path.join(images_dir, "tests")

test_menus = {
    "lobby_1080": cv2.imread(os.path.join(test_images_dir, "lobby_1080_27inch.jpg"), cv2.IMREAD_UNCHANGED),
}

# found = locate_in_image(get_template('press_any'), test_menus['mainmenu_2k'], debug = 0)
# print(found)
found = locate_in_image(get_template('start_button'), test_menus['lobby_1080'], debug=1, threshold=0.7)
print(found)
