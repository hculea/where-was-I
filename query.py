#!/usr/bin/env python
import cv2
import progressbar
import pickle
import image_search
import os.path
import numpy as np


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
    N = 5

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

    maximum = max(values)


    print(maximum)
    print(values)
    print(sum(values))

    if float(maximum)/float(sum(values)) <= 0.4:
        return "NOT IDENTIFIED"

    landmark = get_key(counts, maximum)
    result = landmarks.get(landmark)
    return result


def query(database, video):

    if is_video_file(video):
        cap = cv2.VideoCapture(video)

        frame_nbr = 0
        result_list = []
        while cap.isOpened():
            ret, frame = cap.read()
            if frame is None:
                break

            if frame_nbr % 10 == 0:
                sift_query(frame, result_list, frame_nbr, database)

            frame_nbr += 1

        return get_landmark(result_list)

    else:
        result_list = []
        img = cv2.imread(video)
        sift_query(img, result_list, 1, database)
        return get_landmark(result_list)


def is_video_file(filename):
    video_file_extensions = (
'.264', '.3g2', '.3gp', '.3gp2', '.3gpp', '.3gpp2', '.3mm', '.3p2', '.60d', '.787', '.89', '.aaf', '.aec', '.aep', '.aepx',
'.aet', '.aetx', '.ajp', '.ale', '.am', '.amc', '.amv', '.amx', '.anim', '.aqt', '.arcut', '.arf', '.asf', '.asx', '.avb',
'.avc', '.avd', '.avi', '.avp', '.avs', '.avs', '.avv', '.axm', '.bdm', '.bdmv', '.bdt2', '.bdt3', '.bik', '.bin', '.bix',
'.bmk', '.bnp', '.box', '.bs4', '.bsf', '.bvr', '.byu', '.camproj', '.camrec', '.camv', '.ced', '.cel', '.cine', '.cip',
'.clpi', '.cmmp', '.cmmtpl', '.cmproj', '.cmrec', '.cpi', '.cst', '.cvc', '.cx3', '.d2v', '.d3v', '.dat', '.dav', '.dce',
'.dck', '.dcr', '.dcr', '.ddat', '.dif', '.dir', '.divx', '.dlx', '.dmb', '.dmsd', '.dmsd3d', '.dmsm', '.dmsm3d', '.dmss',
'.dmx', '.dnc', '.dpa', '.dpg', '.dream', '.dsy', '.dv', '.dv-avi', '.dv4', '.dvdmedia', '.dvr', '.dvr-ms', '.dvx', '.dxr',
'.dzm', '.dzp', '.dzt', '.edl', '.evo', '.eye', '.ezt', '.f4p', '.f4v', '.fbr', '.fbr', '.fbz', '.fcp', '.fcproject',
'.ffd', '.flc', '.flh', '.fli', '.flv', '.flx', '.gfp', '.gl', '.gom', '.grasp', '.gts', '.gvi', '.gvp', '.h264', '.hdmov',
'.hkm', '.ifo', '.imovieproj', '.imovieproject', '.ircp', '.irf', '.ism', '.ismc', '.ismv', '.iva', '.ivf', '.ivr', '.ivs',
'.izz', '.izzy', '.jss', '.jts', '.jtv', '.k3g', '.kmv', '.ktn', '.lrec', '.lsf', '.lsx', '.m15', '.m1pg', '.m1v', '.m21',
'.m21', '.m2a', '.m2p', '.m2t', '.m2ts', '.m2v', '.m4e', '.m4u', '.m4v', '.m75', '.mani', '.meta', '.mgv', '.mj2', '.mjp',
'.mjpg', '.mk3d', '.mkv', '.mmv', '.mnv', '.mob', '.mod', '.modd', '.moff', '.moi', '.moov', '.mov', '.movie', '.mp21',
'.mp21', '.mp2v', '.mp4', '.mp4v', '.mpe', '.mpeg', '.mpeg1', '.mpeg4', '.mpf', '.mpg', '.mpg2', '.mpgindex', '.mpl',
'.mpl', '.mpls', '.mpsub', '.mpv', '.mpv2', '.mqv', '.msdvd', '.mse', '.msh', '.mswmm', '.mts', '.mtv', '.mvb', '.mvc',
'.mvd', '.mve', '.mvex', '.mvp', '.mvp', '.mvy', '.mxf', '.mxv', '.mys', '.ncor', '.nsv', '.nut', '.nuv', '.nvc', '.ogm',
'.ogv', '.ogx', '.osp', '.otrkey', '.pac', '.par', '.pds', '.pgi', '.photoshow', '.piv', '.pjs', '.playlist', '.plproj',
'.pmf', '.pmv', '.pns', '.ppj', '.prel', '.pro', '.prproj', '.prtl', '.psb', '.psh', '.pssd', '.pva', '.pvr', '.pxv',
'.qt', '.qtch', '.qtindex', '.qtl', '.qtm', '.qtz', '.r3d', '.rcd', '.rcproject', '.rdb', '.rec', '.rm', '.rmd', '.rmd',
'.rmp', '.rms', '.rmv', '.rmvb', '.roq', '.rp', '.rsx', '.rts', '.rts', '.rum', '.rv', '.rvid', '.rvl', '.sbk', '.sbt',
'.scc', '.scm', '.scm', '.scn', '.screenflow', '.sec', '.sedprj', '.seq', '.sfd', '.sfvidcap', '.siv', '.smi', '.smi',
'.smil', '.smk', '.sml', '.smv', '.spl', '.sqz', '.srt', '.ssf', '.ssm', '.stl', '.str', '.stx', '.svi', '.swf', '.swi',
'.swt', '.tda3mt', '.tdx', '.thp', '.tivo', '.tix', '.tod', '.tp', '.tp0', '.tpd', '.tpr', '.trp', '.ts', '.tsp', '.ttxt',
'.tvs', '.usf', '.usm', '.vc1', '.vcpf', '.vcr', '.vcv', '.vdo', '.vdr', '.vdx', '.veg','.vem', '.vep', '.vf', '.vft',
'.vfw', '.vfz', '.vgz', '.vid', '.video', '.viewlet', '.viv', '.vivo', '.vlab', '.vob', '.vp3', '.vp6', '.vp7', '.vpj',
'.vro', '.vs4', '.vse', '.vsp', '.w32', '.wcp', '.webm', '.wlmp', '.wm', '.wmd', '.wmmp', '.wmv', '.wmx', '.wot', '.wp3',
'.wpl', '.wtv', '.wve', '.wvx', '.xej', '.xel', '.xesc', '.xfl', '.xlmv', '.xmv', '.xvid', '.y4m', '.yog', '.yuv', '.zeg',
'.zm1', '.zm2', '.zm3', '.zmv'  )

    return filename.endswith(video_file_extensions)

