#!/usr/bin/env python
import subprocess
import os
from numpy import random
import time
import glob

from query_match import initialize, match

import subprocess


if __name__ == '__main__':
    directory = 'Dataset/'  # Directory to scan for videos
    output_directory = 'GeneratedTests/'

    if os.path.exists(output_directory):
        for filename in os.listdir(output_directory):
            if filename.endswith('.mp4'):
                os.remove(os.path.join(output_directory, filename))

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    tests = {}
    # Scan the directory for videos
    files = ['video' + str(x) + '.mp4' for x in range(19, 20)]

    for filename in os.listdir(directory):
        if filename in files:
            query_video = os.path.join(directory, filename)

            index = query_video.rfind('/') + 1
            base_output_name = output_directory + query_video[index:-4]

            # Check if files already exist and get the next index
            i = 1
            while os.path.exists(f"{base_output_name}_{i}.mp4"):
                i += 1

            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames', '-of', 'default=noprint_wrappers=1:nokey=1',
                 query_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            total_frames = int(result.stdout.strip())

            # Generate multiple videos
            for _ in range(2):  # Change this to generate more or fewer videos

                cut_length = random.uniform(20, 30)

                output_name = f"{base_output_name}_{i}.mp4"
                i += 1

                start_frame = random.uniform(
                    0, total_frames - cut_length*30) / 30 * 30
                start_time = start_frame / 30

                tests[output_name[output_name.rfind('/') + 1:]] = start_frame

                # tell python to run ffmpeg on the commandline
                subprocess.run(
                    ['ffmpeg', '-y', '-ss', str(start_time), '-i', query_video, '-t', str(cut_length), '-vcodec', 'copy', '-acodec',
                     'copy', '-avoid_negative_ts', 'make_zero', output_name])

    initialize('./CSCI576_features.pkl')
    t = time.time()
    print(tests)
    for filename in os.listdir(output_directory):
        query_video = os.path.join(output_directory, filename)
        result = match(query_video)
        print(f'Result: {result}')
        print(f'Actual Frame: {tests[filename]}\n\n')
    print("average {} second per query".format(
        (time.time() - t) / len(os.listdir(output_directory))))

    # Clean up
    for filename in os.listdir(output_directory):
        if filename.endswith('.mp4'):
            os.remove(os.path.join(output_directory, filename))
