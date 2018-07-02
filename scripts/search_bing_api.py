'''

Download images from Bing image search and sort them into
training and validation sets based on provided proportion.

Note: The directories files are downloaded to need to already
exist before executing script.  Otherwise, it will crash with
an error.

Most of this file is NOT MY CODE

Taken from the following tutorial:-----TODO attribute------
Lightly modified for my purposes.
'''
import numpy as np
import pandas as pd

from ignore import API_KEY, BASE
from requests import exceptions
import argparse
import requests
import cv2
import shutil
import os


from random import shuffle
from math import floor

import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True,
                help="search query to search Bing Image API for")
ap.add_argument("-o", "--output", required=True,
                help="path to output directory of images")
#ap.add_argument("-t", "--train_splt", required=True,
#                help="proportion of files to go into training and valid set")
args = vars(ap.parse_args())

# set your Microsoft Cognitive Services API key along with (1) the
# maximum number of results for a given search and (2) the group size
# for results (maximum of 50 per request)
MAX_RESULTS = 50
#MAX_RESULTS = 250
GROUP_SIZE = 50

# set the endpoint API URL
URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

# when attempting to download images from the web both the Python
# programming language and the requests library have a number of
# exceptions that can be thrown so let's build a list of them now
# so we can filter on them
EXCEPTIONS = set([IOError, FileNotFoundError,
                  exceptions.RequestException, exceptions.HTTPError,
                  exceptions.ConnectionError, exceptions.Timeout])

# store the search term in a convenience variable then set the
# headers and search parameters
term = args["query"]
headers = {"Ocp-Apim-Subscription-Key": API_KEY}
params = {"q": term, "offset": 0, "count": GROUP_SIZE}

id_mapper = np.load('id.npy').item()
id = id_mapper[term]

# make the search
print("[INFO] searching Bing API for '{}'".format(term))
search = requests.get(URL, headers=headers, params=params)
search.raise_for_status()

# grab the results from the search, including the total number of
# estimated results returned by the Bing API
results = search.json()
estNumResults = min(results["totalEstimatedMatches"], MAX_RESULTS)
print("[INFO] {} total results for '{}'".format(estNumResults,
                                                term))

# initialize the total number of images downloaded thus far
total = 0

# output_fldr is initial location for files after downloading
# if empty string is passed for output, the temp folder will be used
# output_fldr does not exist, create it
if args["output"] == '':
    output_fldr = BASE + "movie_" + str(id)
else:
    output_fldr = args["output"]
output_dir = os.path.join(BASE, output_fldr)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# loop over the estimated number of results in `GROUP_SIZE` groups
for offset in range(0, estNumResults, GROUP_SIZE):
    # update the search parameters using the current offset, then
    # make the request to fetch the results
    print("[INFO] making request for group {}-{} of {}...".format(
        offset, offset + GROUP_SIZE, estNumResults))
    params["offset"] = offset
    search = requests.get(URL, headers=headers, params=params)
    search.raise_for_status()
    results = search.json()
    print("[INFO] saving images for group {}-{} of {}...".format(
        offset, offset + GROUP_SIZE, estNumResults))

    # loop over the results
    for v in results["value"]:
        # try to download the image
        try:
            # make a request to download the image
            print("[INFO] fetching: {}".format(v["contentUrl"]))
            r = requests.get(v["contentUrl"], timeout=30)

            # build the path to the output image
            ext = v["contentUrl"][v["contentUrl"].rfind("."):]
            score = os.path.sep.join([output_dir, "{}{}".format(
                str(total).zfill(8), ext)])

            # write the image to disk
            f = open(score, "wb")
            f.write(r.content)
            f.close()

        # catch any errors that would not unable us to download the
        # image
        except Exception as e:
            # check to see if our exception is in our list of
            # exceptions to check for
            if type(e) in EXCEPTIONS:
                print("[INFO] skipping: {}".format(v["contentUrl"]))
                continue

        # try to load the image from disk
        image = cv2.imread(score)

        # if the image is `None` then we could not properly load the
        # image from disk (so it should be ignored)
        if image is None:
            print("[INFO] deleting: {}".format(score))
            os.remove(score)
            continue

        # update the counter
        total += 1

def fldr_name(rating_num):
    return {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine",
        10: "ten",
    }.get(rating_num)

# sort the files just downloaded into training and validation sets

# support code to help separate files into training and validation set
def get_file_list_from_dir(datadir):
    all_files = os.listdir(datadir)
    return all_files


def randomize_files(file_list):
    shuffle(file_list)


def get_training_and_testing_sets(file_list, split=0.7):
    split_index = floor(len(file_list) * split)
    training = file_list[:split_index]
    testing = file_list[split_index:]
    return training, testing

#train_splt = args["train_splt"]

# determine the score of the movie based off of the movie
# database data.  Round to nearest int 1-10.
avg_rating_from_id = np.load('avg_rating_from_id.npy').item()
avg_rating_from_title = np.load('avg_rating_from_title.npy').item()
rating_fldr = fldr_name(avg_rating_from_title[term])

fl = get_file_list_from_dir(output_dir)
randomize_files(fl)
training, testing = get_training_and_testing_sets(fl)

if not os.path.exists(BASE + 'train/' + rating_fldr):
    os.makedirs(BASE + 'train/' + rating_fldr)

if not os.path.exists(BASE + 'valid/' + rating_fldr):
    os.makedirs(BASE + 'valid/' + rating_fldr)

for t in training:
    fn = output_dir + '/' + t
    nfn = BASE + 'train/' + rating_fldr + '/' + t
    os.rename(fn, nfn)

for t in testing:
    fn = output_dir + '/' + t
    nfn = BASE + 'valid/' + rating_fldr + '/' + t
    os.rename(fn, nfn)

shutil.rmtree(output_dir)