"""Utility functions supporting Horizon Zero Dawn Remastered test script."""
from argparse import ArgumentParser
import re
import winreg
import os


def export_registry_key(hive, subkey, input_file):
    """Exports a registry key for interpretation."""
    try:
        if not os.path.exists(input_file):
            with open(input_file, 'w',  encoding="utf-8") as file:
                file.write("")
        with winreg.OpenKey(hive,subkey) as reg_key:
            with open(input_file, 'w',  encoding="utf-8") as reg_file:
                reg_file.write("Windows Registry Editor Version 5.00\n\n")
                reg_file.write(f"[{subkey}]\n")
                try:
                    index = 0
                    while True:
                        value_name, value_data, value_type = winreg.EnumValue(reg_key, index)
                        if value_type == winreg.REG_DWORD:
                            value_data = f"dword:{value_data:08x}"
                        elif value_type == winreg.REG_SZ:
                            value_data = f'"{value_data}"'
                        elif value_type == winreg.REG_QWORD:
                            value_data = f"qword:{value_data:0x16x}"
                        else:
                            value_data = f'"{value_data}"'
                        reg_file.write(f'"{value_name}"={value_data}\n')
                        index += 1
                except OSError:
                    pass
    except OSError as e:
        print(f"Failed to open the registry key: {e}")

def convert_dword_to_decimal(dword_hex):
    """Converts a dword key value to decimal numbers."""
    return int(dword_hex, 16)

def process_registry_file(hive, subkey, input_file, config_file):
    """Processes the exported registry file and converts it to readable text."""
    export_registry_key(hive, subkey, input_file)
    with open(input_file, 'r',  encoding="utf-8") as file:
        lines = file.readlines()

    modified_lines = []

    dword_pattern = re.compile(r'^(\"[^\"]+\")=dword:([0-9a-fA-F]+)', re.IGNORECASE)

    for line in lines:
        match = dword_pattern.search(line)
        if match:
            key = match.group(1)
            hex_value = match.group(2)
            decimal_value = convert_dword_to_decimal(hex_value)
            modified_line = f'{key}={decimal_value}\n'
            modified_lines.append(modified_line)
        else:
            modified_lines.append(line)
    with open(config_file, 'w',  encoding="utf-8") as file:
        file.writelines(modified_lines)



def get_resolution(config_file: str) -> tuple[int]:
    """Retrieve the resolution from local configuration files."""
    width_pattern = re.compile(r"\"FullscreenWidth\"=(\d+)")
    height_pattern = re.compile(r"\"FullscreenHeight\"=(\d+)")
    width = 0
    height = 0

    with open(config_file, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            width_match = width_pattern.match(line)
            height_match = height_pattern.match(line)

            if width_match:
                width = width_match.group(1)
            if height_match:
                height = height_match.group(1)

    return (height, width)

