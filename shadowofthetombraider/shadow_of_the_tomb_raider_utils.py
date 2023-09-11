import winreg

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