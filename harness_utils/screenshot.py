import cv2
import logging
from windows_capture import DxgiDuplicationSession

logger = logging.getLogger(__name__)

class Screenshotter():
    cam = None
    prev_sc = None
    
    def take_sc_bytes(self):
        if self.cam is None:
            self.cam = DxgiDuplicationSession()
        
        screenshot = self.cam.acquire_frame()
        if screenshot is None:
            logger.debug("grab returned none: using previous screenshot")
            screenshot = self.prev_sc
        else:
            screenshot = screenshot.to_bgr() 
        assert screenshot is not None, "Screenshot is None"
        ok, buf = cv2.imencode('.jpg', screenshot)
        if not ok:
            raise Exception("Failed to encode screenshot")
        self.prev_sc = screenshot
        return buf.tobytes()

    def take_sc_save_png(self, output_path):
        if self.cam is None:
            self.cam = DxgiDuplicationSession()
            
        screenshot = self.cam.acquire_frame()
        if screenshot is None:
            logger.debug("grab returned none: using previous screenshot")
            screenshot = self.prev_sc
        else:
            screenshot = screenshot.to_bgr()
        assert screenshot is not None, "Screenshot is None"
        cv2.imwrite(output_path, screenshot)

    def close(self):
        pass
        # if self.cam is not None:
        #     self.cam.release()