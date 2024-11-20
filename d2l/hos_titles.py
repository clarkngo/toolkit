import os
from constants import *

if not os.path.exists("txt_files"):
    os.makedirs("txt_files")

with open(f"txt_files/hos_titles.txt", "w") as start_file:
    for course in COURSES_GH_CL:
        for i in range(1, 11):
            # Using string formatting to ensure two digits
            start_file.write(f"{course}-Spring-2024-HOS{str(i).zfill(2)}\n")
