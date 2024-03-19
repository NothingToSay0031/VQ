import cv2
import glob
import time
import pickle
import numpy as np

TEST = True

def extract_feature(video_paths):
    video_features = []
    for path in video_paths:
        print(path)
        video = cv2.VideoCapture(path)
        features = []
        while True:
            success, frame = video.read()
            if not success:
                break
            features.append([frame.astype(np.float32).mean()])
        print(len(features))
        print(np.unique(features, axis=0).shape)
        print()
        video_features.append(np.array(features))
    return video_features

if __name__ == "__main__":
    video_paths = sorted(glob.glob('./Dataset/*.mp4'), key=lambda path: int(path.split("video")[-1].split(".")[0]))
    t = time.time()
    video_features = extract_feature(video_paths)
    print("extract feature: {} second".format(time.time() - t))

    if not TEST:
        with open("./CSCI576_features.pkl", "wb") as f:
            pickle.dump(video_features, f)

    if TEST:
        # test current feature file
        with open("./CSCI576_features.pkl", "rb") as f:
            video_features_load = pickle.load(f)
        assert len(video_features) == len(video_features_load)
        for i in range(len(video_features)):
            assert video_features[i].shape == video_features_load[i].shape
            print(np.sum(video_features[i] - video_features_load[i]))
            assert np.sum(video_features[i] - video_features_load[i]) == 0
