"""Utility functions for Shadow of the Tomb Raider test script"""
from argparse import ArgumentParser
import winreg


def get_reg(name) -> any:
    """Get registry key value"""
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
    """Get resolution from registry"""
    width = get_reg("FullscreenWidth")
    height = get_reg("FullscreenHeight")
    return (height, width)


def get_args() -> any:
    """Returns command line arg values"""
    parser = ArgumentParser()
    parser.add_argument("--kerasHost", dest="keras_host",
                        help="Host for Keras OCR service", required=True)
    parser.add_argument("--kerasPort", dest="keras_port",
                        help="Port for Keras OCR service", required=True)
    return parser.parse_args()
