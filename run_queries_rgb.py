import time
import glob

from query_match_rgb import initialize_rgb, match_rgb

if __name__ == "__main__":
    initialize_rgb('./CSCI576_features_rgb.pkl')
    found = []
    query_paths = sorted(glob.glob('./Queries/*.rgb'))
    t = time.time()
    for query_path in query_paths:
        found.append(match_rgb(query_path))
    print("average {} second per query".format(
        (time.time() - t) / len(query_paths)))
