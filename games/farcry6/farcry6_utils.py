"""Far Cry 6 utilities for test script"""
import os
import xml.etree.ElementTree as ET

# Corrected XML file path (use raw string r"" or double backslashes)
username = os.getlogin()
xml_file = rf"C:\Users\{username}\Documents\My Games\Far Cry 6\gamerprofile.xml"

# Parse the XML file
def get_resolution() -> tuple[int, int]:
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Find the <RenderProfile> element first
        render_profile = root.find("RenderProfile")
        if render_profile is None:
            raise ValueError("RenderProfile not found in XML file.")

        # Now find <VideoModeProfileFullscreen> inside <RenderProfile>
        video_mode = render_profile.find("VideoModeProfileFullscreen")
        if video_mode is None:
            raise ValueError("VideoModeProfileFullscreen not found in XML file.")

        # Extract width and height
        width = int(video_mode.get("width", 0))
        height = int(video_mode.get("height", 0))

        return width, height

    except FileNotFoundError:
        print(f"Error: File not found -> {xml_file}")
    except ET.ParseError:
        print("Error: Failed to parse XML file")
    except ValueError as e:
        print(f"Error: {e}")

    return 0, 0  # Default return in case of errors