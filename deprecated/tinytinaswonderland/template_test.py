from cv2_utils import *

script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
test_images_dir = os.path.join(images_dir, "tests")

test_menus = {
    "mainmenu": cv2.imread(os.path.join(test_images_dir, "main_menu_2k.png"), cv2.IMREAD_UNCHANGED),
    "settings_menu": cv2.imread(os.path.join(test_images_dir, "settings_menu_2k.png"), cv2.IMREAD_UNCHANGED),
    "benchmark_menu": cv2.imread(os.path.join(test_images_dir, "benchmark_menu_2k.png"), cv2.IMREAD_UNCHANGED),
    "1080menu": cv2.imread(os.path.join(test_images_dir, "menu_1080p_27inch.png"), cv2.IMREAD_UNCHANGED)
}

found = locate_in_image(get_template('options'), test_menus['1080menu'], threshold=0.8, debug=1)
print(found)
