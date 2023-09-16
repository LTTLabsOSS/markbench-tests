import os
import cv2

# path relative to script
script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
dir16x9 = os.path.join(images_dir, "16x9")
dir16x10 = os.path.join(images_dir, "16x10")

templates = {
    "options": {
        "16x10": cv2.imread(os.path.join(dir16x9, "options_menu_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x9": cv2.imread(os.path.join(dir16x9, "options_menu_1080.png"), cv2.IMREAD_UNCHANGED)
    },
    "benchmark": {
        "16x10": cv2.imread(os.path.join(dir16x9, "benchmark_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x9": cv2.imread(os.path.join(dir16x9, "benchmark_1080.png"), cv2.IMREAD_UNCHANGED)
    },
    "header": {
        "16x10": cv2.imread(os.path.join(dir16x9, "results_header_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x9": cv2.imread(os.path.join(dir16x9, "results_header_1080.png"), cv2.IMREAD_UNCHANGED)
    },
}

# Stub
def get_resolution():
    return 0,0