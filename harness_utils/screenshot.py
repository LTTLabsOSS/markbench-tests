import logging

import cv2
import mss
import numpy as np

logger = logging.getLogger(__name__)


class Screenshotter:
    def take_sc_bytes(self):
        with mss.mss() as sct:
            monitor_1 = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor_1))
            _, buf = cv2.imencode(".jpg", screenshot)
        return buf.tobytes()

    def take_sc_save_png(self, output_path):
        with mss.mss() as sct:
            monitor_1 = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor_1))
        cv2.imwrite(output_path, screenshot)
