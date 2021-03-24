import glob
import sys

import Vocabulary
import db_index
import pickle
import os.path
import cv2
import progressbar

CREATE_DATABASE = True


def get_sift_features(im_list):
    sift = cv2.xfeatures2d.SIFT_create()
    features = {}
    total = len(im_list)
    bar = progressbar.ProgressBar(maxval=total,
                                  widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    count = 0

    bar.start()
    for im_name in im_list:
        bar.update(count)
        im = cv2.imread(im_name, 0)
        kp, desc = sift.detectAndCompute(im, None)
        features[im_name] = desc
        count += 1
    bar.finish()
    return features


def feature_active(name, feature):
    return feature == name or feature == 'all'


def load_features(name, prefix, base):
    # create file name from prefix(path), base name, feature name and extension.
    fname = prefix + base + '_' + name + '.pkl'
    feat = None
    # open file fname in (r)eading mode in (b)inary format
    with open(fname, 'rb') as f:
        # deserialize the binary file
        feat = pickle.load(f)
    return feat


def compute_features(image_list, name, feature_function, prefix, base):
    fname = prefix + base + '_' + name + '.pkl'
    # Check if file exists already. If true, ask if features need be recomputed.
    if os.path.isfile(fname):
        compute = input("Found existing features: " + fname + " Do you want to recompute them? ([Y]/N): ")
    else:
        # If file is not found, mark compute flag for computing.
        compute = 'Y'

    if compute == 'Y' or compute == '':
        # Compute features using the provided function.
        features = feature_function(image_list)
        # Open file in writing mode and write serialized binary data to disk to save computing time during next runs.
        with open(fname, 'wb') as f:
            pickle.dump(features, f)
    else:
        # If features do not need to be computed, just load features from disk
        features = load_features(name)
    return features


def create_DB(training_set):
    if not CREATE_DATABASE:
        return

    deleteIfExists("./db/MMA.db")
    deleteIfExists("./db/MMA_sift.pkl")
    deleteIfExists("./db/MMA_sift_vocabulary.pkl")

    database = "MMA.db"
    clusters = 100
    prefix = "db/"

    types = ('*.jpg', '*.JPG', '*.png')
    # The prefix argument can be an nonexisting folder. This folder is created if needed.
    if not os.path.exists(prefix):
        os.makedirs(prefix)

    # Retrieve image list from traning_set argument specified on the command line.
    image_list = []
    for type_ in types:
        files = training_set + type_
        image_list.extend(glob.glob(files))

    # Get file name without extension and prefix
    base = os.path.basename(database).split('.')[0]

    sift_features = None
    sift_vocabulary = None

    # Compute sift features and vocabulary if sift is 'active'
    if feature_active('sift', 'sift'):
        sift_features = compute_features(image_list, 'sift', get_sift_features, prefix, base)

        fname = prefix + base + '_sift_vocabulary.pkl'
        if os.path.isfile(fname):
            compute = input("Found existing vocabulary: " + fname + " Do you want to recompute it? ([Y]/N): ")
        else:
            compute = 'Y'
        if compute == 'Y' or compute == '':
            sift_vocabulary = Vocabulary.Vocabulary(base)
            sift_vocabulary.train(sift_features, clusters)
            fname = prefix + base + '_sift_vocabulary.pkl'
            with open(fname, 'wb') as f:
                pickle.dump(sift_vocabulary, f)

    db_name = prefix + base + '.db'

    if os.path.isfile(db_name):
        action = input('Database already exists. Do you want to (r)emove, (a)ppend or (q)uit? ')
    else:
        action = 'c'

    if action == 'r':
        os.remove(db_name)
        new = True

    elif action == 'c':
        new = True

    else:
        sys.exit(0)

    # Create indexer which can create the database tables and provides an API to insert data into the tables.
    indx = db_index.Indexer(db_name)
    if new:
        indx.create_tables()

    if feature_active('sift', 'sift'):
        if sift_vocabulary is None:
            sift_vocabulary = load_features('sift_vocabulary')
        if sift_features is None:
            sift_features = load_features('sift')

        for i in range(len(image_list)):
            indx.add_to_index('sift', image_list[i], sift_features[image_list[i]], sift_vocabulary)

    indx.db_commit()


def deleteIfExists(filePath):
    if os.path.exists(filePath):
        os.remove(filePath)
    else:
        print("Can not delete the file as it doesn't exists")