import cv2
import pickle
import numpy as np


def initialize(feature_path):
    '''
    read the pre-computed feature as global variable

    :param feature_path: path to pre-computed feature
    '''
    global video_features

    with open(feature_path, "rb") as f:
        video_features = pickle.load(f)


def match(query_path):
    '''
    read the query video and find the match

    :param query_path: path to the query video
    :return: a list containing the matched video ID and frame ID
    '''
    global video_features

    video = cv2.VideoCapture(query_path)

    # take 10 anchor frames with 1.5s interval for matching
    query_frames = []
    for i in range(10):
        video.set(cv2.CAP_PROP_POS_FRAMES, 45 * i)  # 45 frame -> 1.5s (30 fps)
        success, frame = video.read()
        if not success:
            break
        query_frames.append(frame.astype(np.float32).mean())
    query_frames = np.array(query_frames).astype(np.float32)

    min_diff = 2147483647
    found_video = None
    found_start = None
    for j in range(len(video_features)):
        video_feature = video_features[j]

        # 1. find first frame (may have multiple matches)
        diff_first = abs(video_feature[:, 0] - query_frames[0])
        found_first = np.nonzero(diff_first < 0.001)[0]
        if found_first.shape[0] == 0:
            continue
        # 2. find the last frame (may have multiple matches)
        diff_last = abs(video_feature[:, 0] - query_frames[-1])
        found_last = np.nonzero(diff_last < 0.001)[0]
        if found_last.shape[0] == 0:
            continue
        # 3. found a pair of match such that the number of frames between them is the same as the query video
        for a in found_first:
            for idx, b in enumerate(found_last):
                if b - a > 45 * (len(query_frames)-1):
                    break
                if b - a == 45 * (len(query_frames)-1):
                    # 4. for all potential (a, b) pair, compute difference using middle frames
                    diff_mid = []
                    for i in range(1, len(query_frames)-1):  # for all the middle frames
                        diff_mid.append(
                            video_feature[a + 45 * i, 0] - query_frames[i])
                    diff_mid = np.array(diff_mid)
                    if (diff_mid < 0.001).all():
                        if (diff_first[a] + np.sum(diff_mid) + diff_last[b]) < min_diff:
                            found_video = j+1
                            found_start = a
                            min_diff = diff_first[a] + \
                                np.sum(diff_mid) + diff_last[b]
                    found_last = found_last[idx:]
                    break
            if min_diff == 0:
                break
        if min_diff == 0:
            break
    if found_video is not None and found_start is not None:
        print(query_path)
        print("found: video {}, start frame {} for mp4 file, {} for real index, difference {}\n".format(
            found_video, found_start, found_start - 1, min_diff))
    return [found_video, found_start]
