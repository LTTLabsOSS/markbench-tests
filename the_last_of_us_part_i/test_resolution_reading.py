import os
import sys

from the_last_of_us_part_i_utils import get_resolution

config_path = "./sample_screeninfo.cfg"
results = get_resolution(config_path)

print(results)