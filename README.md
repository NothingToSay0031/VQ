# CSCI576-Final-Project

## How to configure / run

1. Python version >= 3.8
2. pip install opencv-python numpy pyglet
3. install [ffmpeg](https://pyglet.readthedocs.io/en/latest/programming_guide/media.html#guide-supportedmedia-ffmpeg)
4. `python player.py Queries/video3_1.mp4`
```
.
├── CSCI576_features.pkl
├── Dataset         // Source files
│   ├── video1.mp4
│   ├── video10.mp4
│   ├── video11.mp4
│   ├── video12.mp4
│   ├── video13.mp4
│   ├── video14.mp4
│   ├── video15.mp4
│   ├── video16.mp4
│   ├── video17.mp4
│   ├── video18.mp4
│   ├── video19.mp4
│   ├── video2.mp4
│   ├── video20.mp4
│   ├── video3.mp4
│   ├── video4.mp4
│   ├── video5.mp4
│   ├── video6.mp4
│   ├── video7.mp4
│   ├── video8.mp4
│   └── video9.mp4
├── Queries
│   ├── video10_1.mp4
│   ├── video11_1.mp4
│   ├── video1_1.mp4
│   ├── video2_1.mp4
│   ├── video3_1.mp4
│   ├── video4_1.mp4
│   ├── video5_1.mp4
│   ├── video6_1.mp4
│   ├── video6_2.mp4
│   ├── video7_1.mp4
│   ├── video8_1.mp4
│   └── video9_1.mp4
├── README.md
├── player.py       // main function to run a single query
├── query_match.py  // query match lib
└── run_queries.py  // test the runtime of a series of queries
```

## DONE
- [x] More tests on exact match, play, pause, reset buttons and audio/video synchronization.
- [x] Faster.
- [x] When it finishes playing, start from the beginning.
- [x] Reset button has bug
- [x] Integrate, input retrieval video and output original video with exact frame index.
- [x] Sometimes `player.py` runs with black video content.

## Reference

https://github.com/pyglet/pyglet/blob/master/examples/media/media_player.py#L169

https://pyglet.readthedocs.io/en/latest/modules/media.html
