from cv2_utils import *

script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
test_images_dir = os.path.join(images_dir, "tests")

test_menus = {
    "mainmenu_1080": cv2.imread(os.path.join(test_images_dir, "menu_1080_27inch.png"), cv2.IMREAD_UNCHANGED),
    "famous_menu_1440": cv2.imread(os.path.join(test_images_dir, "famous_menu_1440_27inch.png"), cv2.IMREAD_UNCHANGED),
    "activities_menu_1440": cv2.imread(os.path.join(test_images_dir, "activities_1440_27inch.png"),
                                       cv2.IMREAD_UNCHANGED)
}

# found = locate_in_image(get_template('press_any'), test_menus['mainmenu_2k'], debug = 0)
# print(found)
found = locate_in_image(get_template('landing_challenges'), test_menus['activities_menu_1440'], threshold=0.77, debug=1)
print(found)
