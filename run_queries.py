import time
import glob

from query_match import initialize, match

if __name__ == "__main__":
    initialize('./CSCI576_features.pkl')
    found = []
    query_paths = sorted(glob.glob('./Queries/*.mp4'))
    t = time.time()
    for query_path in query_paths:
        found.append(match(query_path))
    print("average {} second per query".format((time.time() - t) / len(query_paths)))