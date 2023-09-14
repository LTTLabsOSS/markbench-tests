from cv2_utils import *

script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
test_images_dir = os.path.join(images_dir, "tests")

test_menus = {
    "mainmenu": cv2.imread(os.path.join(test_images_dir, "main_menu_2k.png"), cv2.IMREAD_UNCHANGED),
    "graphics_menu": cv2.imread(os.path.join(test_images_dir, "graphics_menu_2k.png"), cv2.IMREAD_UNCHANGED),
    "settings_menu": cv2.imread(os.path.join(test_images_dir, "settings_menu_2k.png"), cv2.IMREAD_UNCHANGED),
    "accessibility_menu": cv2.imread(os.path.join(test_images_dir, "settings_menu_2k.png"), cv2.IMREAD_UNCHANGED)
}

found = locate_in_image(get_template('accessibility'), test_menus['accessibility_menu'], threshold=0.8, debug=1)
print(found)
