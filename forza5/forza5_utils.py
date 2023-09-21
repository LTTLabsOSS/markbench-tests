import re


def read_resolution(config_path: str) -> tuple[int]:    
    height_pattern = re.compile(r"<ResolutionHeight value=\"(\d+)\"/>")
    width_pattern = re.compile(r"<ResolutionWidth value=\"(\d+)\"/>")
    width = 0
    height = 0
    with open(config_path) as f:
        lines = f.readlines()
        for line in lines:
            height_match = height_pattern.search(line)
            width_match = width_pattern.search(line)
            if height_match is not None:
                height = height_match.group(1)
            if width_match is not None:
                width = width_match.group(1)
    return (width, height)