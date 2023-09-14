import os
import re
import shutil
import tempfile
import winreg
import logging

HEIGHT_PATTERN = r"FullscreenHeight=(\d*)"
WIDTH_PATTERN = r"FullscreenWidth=(\d*)"
vendorid_pattern = r"AdapterVendorID=(\w+)"
deviceid_pattern = r"AdapterDeviceID=(\w+)"
ASS_CREED_FOLDER = "Assassin's Creed Valhalla"
CONFIG_FILENAME = "ACValhalla.ini"


def sed_inplace(filename, pattern, repl):
    '''
    Perform of in-place `sed` substitution: e.g.,
    `sed -i -e 's/'${pattern}'/'${repl}' "${filename}"`.
    See https://stackoverflow.com/a/31499114
    '''
    pattern_compiled = re.compile(pattern)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        with open(filename) as src_file:
            for line in src_file:
                tmp_file.write(pattern_compiled.sub(repl, line))

    shutil.copystat(filename, tmp_file.name)
    shutil.move(tmp_file.name, filename)


def set_resolution(path, height, width):
    sed_inplace(path, HEIGHT_PATTERN, f"FullscreenHeight={height}")
    sed_inplace(path, WIDTH_PATTERN, f"FullscreenWidth={width}")


def mydocumentspath():
    SHELL_FOLDER_KEY = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
    try:
        root_handle = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        shell_folders_handle = winreg.OpenKeyEx(root_handle, SHELL_FOLDER_KEY)
        personal_path_key = winreg.QueryValueEx(shell_folders_handle, 'Personal')
        return personal_path_key[0]
    finally:
        root_handle.Close()


def load_preset(name, height, width):
    mydocuments = mydocumentspath()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    preset_path = os.path.join(script_dir, "presets", f'{name}.ini')
    dest = os.path.join(mydocuments, ASS_CREED_FOLDER, CONFIG_FILENAME)
    vendorid, deviceid = read_device_ids()
    logging.info(f"vendorid: {vendorid} deviceid: {deviceid}")
    logging.info(f"Copying config {preset_path} to {dest}")
    shutil.copy2(preset_path, dest)
    set_resolution(dest, height, width)
    sed_inplace(dest, vendorid_pattern, f"AdapterVendorID={vendorid}")
    sed_inplace(dest, deviceid_pattern, f"AdapterDeviceID={deviceid}")
   

def save_current_config(dest):
    mydocuments = mydocumentspath()
    src = os.path.join(mydocuments, ASS_CREED_FOLDER, CONFIG_FILENAME)
    shutil.copy2(src, dest)


def read_device_ids():
    pat1 = re.compile(vendorid_pattern)
    pat2 = re.compile(deviceid_pattern)
    mydocuments = mydocumentspath()
    src = os.path.join(mydocuments, ASS_CREED_FOLDER, CONFIG_FILENAME)
    vendorid = 0
    deviceid = 0
    with open(src) as fp:
        lines = fp.readlines()
        for line in lines:
            result = pat1.match(line)
            if result is not None:
                vendorid = result.group(1)
            result2 = pat2.match(line)
            if result2 is not None:
                deviceid = result2.group(1)
            if int(vendorid) > 0 and int(deviceid) > 0:
                break
    return (vendorid, deviceid)


def read_current_resolution():
    mydocuments = mydocumentspath()
    src = os.path.join(mydocuments, ASS_CREED_FOLDER, CONFIG_FILENAME)
    hpattern = re.compile(HEIGHT_PATTERN)
    wpattern = re.compile(WIDTH_PATTERN)
    h = w = 0
    with open(src) as fp:
        lines = fp.readlines()
        for line in lines:
            result = hpattern.match(line)
            if result is not None:
                h = result.group(1)

            result2 = wpattern.match(line)
            if result2 is not None:
                w = result2.group(1)
            if int(h) > 0 and int(w) > 0:
                break
    return (h, w)
