"""Epic Games launcher utility functions"""

import json
import re


def find_eg_game_version(gamefoldername: str) -> str | None:
    """Find the version of the specific game (e.g., AlanWake2) from the launcher installed data."""
    installerdat = r"C:\ProgramData\Epic\UnrealEngineLauncher\LauncherInstalled.dat"

    try:
        # Open the file and read its entire content
        with open(installerdat, encoding="utf-8") as file:
            file_content = file.read()

        # Check if the "InstallationList" section is in the content
        installation_list_match = re.search(
            r'"InstallationList":\s*(\[[^\]]*\])', file_content
        )
        if not installation_list_match:
            print("No InstallationList found.")
            return None

        # Extract the InstallationList part from the file
        installation_list_json = installation_list_match.group(1)

        # Load the installation list as JSON
        installation_list = json.loads(installation_list_json)

        # Loop through each item in the installation list
        for game in installation_list:
            # Check if the game's InstallLocation contains the target string (AlanWake2)
            if gamefoldername in game.get("InstallLocation", ""):
                # Return the AppVersion for this game
                return game.get("AppVersion", None)

    except Exception as e:
        print(f"Error: {e}")

    return None
