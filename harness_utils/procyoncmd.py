"""Modules for executing shell commands and parsing strings"""
import subprocess
import re

def get_winml_devices(procyon_path):
    """
    Function which uses the ProcyonCmd.exe to list all available winml devices on the system. Returns a dictionary of device names and IDs
    """

    # run the command line utility for procyon in order to list available winml devices
    winml_devices = subprocess.run([f'{procyon_path}', '--list-winml-devices'], shell=True, capture_output=True, text=True, check=True).stdout

    winml_devices_split = winml_devices.split('\n')
    winml_devices_parsed = [device[9::] for device in winml_devices_split if re.search(r"(amd|nvidia|intel)", device.lower())]
    unique_winml_devices = list(dict.fromkeys(winml_devices_parsed))
    winml_dict = {device_split.split(', ')[0]:device_split.split(', ')[1] for device_split in unique_winml_devices}

    return winml_dict

def get_openvino_devices(procyon_path):
    """
    Function which uses the ProcyonCmd.exe to list all available openvino devices on the system. Returns a dictionary of device type and name
    """

    openvino_devices = subprocess.run([f'{procyon_path}', '--list-openvino-devices'], shell=True, capture_output=True, text=True, check=True).stdout

    openvino_devices_split = openvino_devices.split('\n')
    openvino_devices_parsed = [device[9::] for device in openvino_devices_split if re.search(r"(amd|nvidia|intel)", device.lower())]
    unique_openvino_devices = list(dict.fromkeys(openvino_devices_parsed))
    openvino_dict = {device_split.split(', ')[1]:device_split.split(', ')[0] for device_split in unique_openvino_devices}

    return openvino_dict

def get_openvino_gpu(openvino_devices, gpu_id):
    """
    function which checks the openvino_devices dictionary for GPU entries. 
    If only one gpu is detected, there should not be a GPU.0 and GPU.1 entry 
    so we just return the first detected gpu regardless of requested ID
    """

    gpu = openvino_devices.get("GPU", None)

    if gpu is None:
        gpu = openvino_devices.get(gpu_id, "No Openvino GPU Detected")

    return gpu

def get_cuda_devices(procyon_path):
    """
    Function which uses the ProcyonCmd.exe to list all available openvino devices on the system. Returns a dictionary of device type and name
    """

    cuda_devices = subprocess.run([f'{procyon_path}', '--list-cuda-devices'], shell=True, capture_output=True, text=True, check=True).stdout

    cuda_devices_split = cuda_devices.split('\n')
    cuda_devices_parsed = [device[9::] for device in cuda_devices_split if re.search(r"(nvidia)", device.lower())]
    unique_cuda_devices = list(dict.fromkeys(cuda_devices_parsed))

    if len(unique_cuda_devices) > 0:
        cuda_dict = {device_split.split(', ')[1]:device_split.split(', ')[0] for device_split in unique_cuda_devices}
    else:
        cuda_dict = {}

    return cuda_dict
