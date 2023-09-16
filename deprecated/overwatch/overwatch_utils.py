"""Utilities for Overwatch test script"""
import os
import cv2

# path relative to script
script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
dir16x9 = os.path.join(images_dir, "16x9")
dir16x10 = os.path.join(images_dir, "16x10")

templates = {
    "start_button": {
        "16x10": cv2.imread(os.path.join(dir16x9, "start_room_button.png"), cv2.IMREAD_UNCHANGED),
        "16x9": cv2.imread(os.path.join(dir16x9, "start_room_button.png"), cv2.IMREAD_UNCHANGED)
    }
}
