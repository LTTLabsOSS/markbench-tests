import re


def get_resolution(config_path: str) -> tuple[int]:
    height = 0
    width = 0
    with open(config_path) as f:
        lines = f.readlines()
        for line in lines:
            if "defaultres" in line:
                patt1 = re.compile(r"\"\w+\.\w+\"[\t| ]+\"(\d+)\"")
                match1 = patt1.search(line)
                if match1:
                    width = match1.group(1)
            if "defaultresheight" in line:
                patt2 = re.compile(r"\"\w+\.\w+\"[\t| ]+\"(\d+)\"")
                match2 = patt2.search(line)
                if match2:
                    height = match2.group(1)
    return (height, width)