"""Modules for executing shell commands and parsing strings"""

import re
import subprocess


def parse_device_list(output, device_header):
    """Parse device name/ID pairs from a Procyon device list."""
    devices = {}
    parsing_devices = False

    for line in output.splitlines():
        line = line.strip()

        # Remove Procyon timestamp from the beginning of the line.
        line = re.sub(
            r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ",
            "",
            line,
        )

        if line.startswith(device_header):
            parsing_devices = True
            continue

        if not parsing_devices:
            continue

        if line == "Command line actions complete, exiting":
            break

        if not line or "," not in line:
            continue

        device_name, device_id = line.rsplit(",", 1)

        device_name = device_name.strip()
        device_id = device_id.strip()

        if device_name and device_id:
            devices[device_id] = device_name

    return devices

def get_directml_devices(procyon_path):
    """
    Function which uses the ProcyonCmd.exe to list all available DirectML
    devices on the system.

    Returns a dictionary of device IDs and names.
    """

    directml_devices = subprocess.run(
        [f"{procyon_path}", "--list-directml-devices"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    return parse_device_list(
        directml_devices,
        "DirectML devices (name, id):",
    )


def get_winml_devices(procyon_path):
    """
    Function which uses the ProcyonCmd.exe to list all available WinML
    devices on the system.

    Returns a dictionary of device IDs and names.
    """

    winml_devices = subprocess.run(
        [f"{procyon_path}", "--list-winml-devices"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    return parse_device_list(
        winml_devices,
        "Graphics adapters (name, device_id):",
    )


def get_openvino_devices(procyon_path):
    """
    Function which uses the ProcyonCmd.exe to list all available OpenVINO
    devices on the system.

    Returns a dictionary of device IDs/types and names.
    """

    openvino_devices = subprocess.run(
        [f"{procyon_path}", "--list-openvino-devices"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    return parse_device_list(
        openvino_devices,
        "OpenVINO devices (name, type):",
    )


def get_cuda_devices(procyon_path):
    """
    Function which uses the ProcyonCmd.exe to list all available CUDA
    devices on the system.

    Returns a dictionary of device IDs and names.
    """

    cuda_devices = subprocess.run(
        [f"{procyon_path}", "--list-cuda-devices"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    return parse_device_list(
        cuda_devices,
        "CUDA devices (name, id):",
    )


def get_openvino_gpu(openvino_devices, gpu_id):
    """
    Function which checks the openvino_devices dictionary for GPU entries.

    If only one GPU is detected, there should not be a GPU.0 and GPU.1
    entry, so return the first detected GPU regardless of requested ID.
    """

    gpu = openvino_devices.get("GPU", None)

    if gpu is None:
        gpu = openvino_devices.get(gpu_id, "No OpenVINO GPU Detected")

    return gpu


if __name__ == "__main__":
    procyon_path = r"C:\Program Files\UL\Procyon\ProcyonCmd.exe"

    print("DirectML:")
    print(get_directml_devices(procyon_path))

    print("\nWinML:")
    print(get_winml_devices(procyon_path))

    print("\nOpenVINO:")
    print(get_openvino_devices(procyon_path))

    print("\nCUDA:")
    print(get_cuda_devices(procyon_path))