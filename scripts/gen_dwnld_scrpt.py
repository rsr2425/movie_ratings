# NOTE: needs to be run from the scripts folder

import numpy as np
from clean import movies
import os
import sys

movie_titles = list(movies['title'])

file = open("download_data.sh", "w+")

for i, movie in enumerate(movie_titles[:int(sys.argv[1])]):
    if i % 8 == 0 and i > 0:
        file.write("wait\n")
    file.write(f"python search_bing_api.py --query \"{movie}\" --output '' &\n")

file.close()