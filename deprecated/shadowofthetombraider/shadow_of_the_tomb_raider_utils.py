import winreg
import os
import cv2

def get_reg(name) -> any:
    reg_path = r'SOFTWARE\Eidos Montreal\Shadow of the Tomb Raider\Graphics'
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0,
                                      winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def get_resolution() -> tuple[int]:
    width = get_reg("FullscreenWidth")
    height = get_reg("FullscreenHeight")
    return (height, width)


# path relative to script
script_dir = os.path.dirname(os.path.realpath(__file__))
images_dir = os.path.join(script_dir, "images")
dir16x9 = os.path.join(images_dir, "16x9")
dir16x10 = os.path.join(images_dir, "16x10")

templates = {
    "load_menu_play": {
        "16x9": cv2.imread(os.path.join(images_dir, "load_menu_play.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(images_dir, "load_menu_play.png"), cv2.IMREAD_UNCHANGED)
    },
     "load_menu_play_orange": {
        "16x9": cv2.imread(os.path.join(images_dir, "play_orange.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(images_dir, "play_orange.png"), cv2.IMREAD_UNCHANGED)
    },
    "menu_options": {
        "16x9": cv2.imread(os.path.join(dir16x9, "options_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(dir16x10, "options.png"), cv2.IMREAD_UNCHANGED)
    },
    "menu_options_save_game": {
        "16x9": cv2.imread(os.path.join(dir16x9, "options_1080_savedgame.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(dir16x10, "options_savedgame.png"), cv2.IMREAD_UNCHANGED)
    },
    "menu_options_highlighted": {
        "16x9": cv2.imread(os.path.join(dir16x9, "options2_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(dir16x10, "options2.png"), cv2.IMREAD_UNCHANGED)
    },
    "menu_options_save_game_highlighted": {
        "16x9": cv2.imread(os.path.join(dir16x9, "options2_1080_savegame.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(dir16x10, "options2_savegame.png"), cv2.IMREAD_UNCHANGED)
    },
    "menu_graphics": {
        "16x9": cv2.imread(os.path.join(dir16x9, "graphics_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(dir16x10, "graphics_button.png"), cv2.IMREAD_UNCHANGED)
    },
    "menu_graphics_tab": {
        "16x9": cv2.imread(os.path.join(dir16x9, "graphics_tab_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(dir16x10, "graphics_tab.png"), cv2.IMREAD_UNCHANGED)
    },
    "run_benchmark": {
        "16x9": cv2.imread(os.path.join(dir16x9, "run_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(dir16x10, "run.png"), cv2.IMREAD_UNCHANGED)
    },
    "results_header": {
        "16x9": cv2.imread(os.path.join(dir16x9, "results_1080.png"), cv2.IMREAD_UNCHANGED),
        "16x10": cv2.imread(os.path.join(dir16x10, "results.png"), cv2.IMREAD_UNCHANGED)
    }
}
