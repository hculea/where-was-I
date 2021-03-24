#!/usr/bin/env python
import cv2
from video_tools import get_frame_count, get_frame_rate
import progressbar
import pickle
import image_search
import os.path


def get_sift_features(im_list):
    """get_sift_features accepts a list of image names and computes the sift descriptors for each image.
    It returns a dictionary with descriptor as value and image name as key """
    sift = cv2.xfeatures2d.SIFT_create()
    features = {}
    total = len(im_list)
    bar = progressbar.ProgressBar(maxval=total, \
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    count = 0
    bar.start()
    for im_name in im_list:
        bar.update(count)
        # load grayscale image
        key = im_name.keys()
        key = list(key)[0]
        gray = cv2.cvtColor(im_name[key], cv2.COLOR_BGR2GRAY)
        kp, desc = sift.detectAndCompute(gray, None)
        features[count] = desc
        count += 1
    bar.finish()
    return features


def sift_query(frame, result_list, frame_nbr, database):
    frame_nbr_str = str(frame_nbr)
    # Get file name without extension
    base = os.path.splitext(database)[0]
    db_name = database

    search = image_search.Searcher(db_name)
    fname = base + '_sift_vocabulary.pkl'
    # Load the vocabulary to project the features of our query image on
    with open(fname, 'rb') as f:
        sift_vocabulary = pickle.load(f, encoding="latin1")

    dictionary = {}
    dictionary[frame_nbr_str] = frame
    sift_query = get_sift_features([dictionary])
    # Get a histogram of visual words for the query image
    image_words = sift_vocabulary.project(sift_query[list(sift_query.keys())[0]])
    # Use the histogram to search the database
    sift_candidates = search.query_iw('sift', image_words)

    # If candidates exists, show the top N candidates
    N = 10

    if not sift_candidates is None:
        sift_winners = [search.get_filename(cand[1]) for cand in sift_candidates][0:N]
        for i in range(len(sift_winners)):
            result_list.append(sift_winners[i])


def get_key(my_dict, val):
    for key, value in my_dict.items():
        if val == value:
            return key


def get_landmark(result_list):
    landmarks = {
        "nk": "Nieuwe Kerk",
        "rh": "Stadhuis",
        "oj": "Oude Jan"
    }

    keys = []

    for key, value in landmarks.items():
        keys.append(key)

    nk = keys[0]
    rh = keys[1]
    oj = keys[2]

    countNK = 0
    countRH = 0
    countOJ = 0
    for i in result_list:
        if nk in i:
            countNK += 1
        elif rh in i:
            countRH += 1
        elif oj in i:
            countOJ += 1

    counts = {
        "nk": countNK,
        "rh": countRH,
        "oj": countOJ
    }

    values = []
    for key, value in counts.items():
        values.append(value)

    totalCounts = countNK + countRH + countOJ
    maximum = max(values)
    if maximum/totalCounts < 0.535:
        return None
    else:
        landmark = get_key(counts, maximum)
        result = landmarks.get(landmark)
        return result


def query(database, video):
    cap = cv2.VideoCapture(video)

    # frame_count = get_frame_count(video) + 1
    # frame_rate = get_frame_rate(video)

    frame_nbr = 0
    result_list = []
    while cap.isOpened():
        ret, frame = cap.read()
        if frame is None:
            break

        if frame_nbr % 30 == 0:
            sift_query(frame, result_list, frame_nbr, database)

        frame_nbr += 1

    return get_landmark(result_list)
