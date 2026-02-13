"""3dmark test utils"""
from pathlib import Path
import xml.etree.ElementTree as ET

def get_score(element_name, xml_path):
    """fetch the score from the xml report"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    found_elements = root.findall(f".//{element_name}")

    if len(found_elements) == 0:
        raise ValueError("Could not find a score in the XML report")

    return found_elements[0].text

if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
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
