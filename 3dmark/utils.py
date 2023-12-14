import os
from pathlib import Path
import psutil
import xml.etree.ElementTree as ET

def is_process_running(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return process
    return None

def get_score(element_name, xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    found_elements = root.findall(".//{}".format(element_name))

    if len(found_elements) == 0:
        raise ValueError("Could not find a score in the XML report")
    
    return found_elements[0].text

if __name__ == "__main__":
    script_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    firestrike_example = script_dir / "sample_reports" / "firestrike_result.xml"
    portroyal_example = script_dir / "sample_reports" / "portroyal_result.xml"
    solarbay_example = script_dir / "sample_reports" / "solarbay_result.xml"
    timespy_example = script_dir / "sample_reports" / "timespy_result.xml"
    scores = []
    scores.append(get_score("FireStrike", firestrike_example))
    scores.append(get_score("PortRoyal", portroyal_example))
    scores.append(get_score("SolarBay", solarbay_example))
    scores.append(get_score("TimeSpy", timespy_example))
    print(scores)