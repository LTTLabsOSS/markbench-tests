import dxcam
import cv2
import logging

logger = logging.getLogger(__name__)

class Screenshotter():
    cam = None
    prev_sc = None
    
    def take_sc_bytes(self):
        if self.cam is None:
            self.cam = dxcam.create(output_color="BGR")
        
        screenshot = self.cam.grab()
        if screenshot is None:
            logger.debug("grab returned none: using previous screenshot")
            screenshot = self.prev_sc
        ok, buf = cv2.imencode('.jpg', screenshot)
        if not ok:
            raise Exception("Failed to encode screenshot")
        self.prev_sc = screenshot
        return buf.tobytes()

    def take_sc_save_png(self, output_path):
        if self.cam is None:
            self.cam = dxcam.create(output_color="BGR")
            
        screenshot = self.cam.grab()
        if screenshot is None:
            raise Exception("Failed to capture screenshot")
        cv2.imwrite(output_path, screenshot)

    def close(self):
        if self.cam is not None:
            self.cam.release()