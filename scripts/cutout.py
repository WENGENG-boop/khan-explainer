#!/usr/bin/env python3
"""Person cutout for a talking head, for systems without macOS Vision (cutout.swift): raw BGRA frames
in on stdin, the same frames out on stdout with the person's matte in the alpha channel. Free and
local: MediaPipe selfie segmentation. Same rules as cutout.swift: a frame with no face looking at the
camera (b-roll, a screen recording) comes out fully transparent, and the bottom rows fade out.

  ffmpeg -i in.mp4 -vf scale=W:H -f rawvideo -pix_fmt bgra - \
    | uv run --no-project --python 3.12 --with mediapipe==0.10.21 python cutout.py W H \
    | ffmpeg -f rawvideo -pix_fmt bgra -s WxH -r 30 -i - ...
"""
import sys
from collections import deque
import numpy as np
import mediapipe as mp

if len(sys.argv) != 3: sys.exit("usage: cutout.py <width> <height>")
w, h = int(sys.argv[1]), int(sys.argv[2])
size = w * h * 4
src, dst = sys.stdin.buffer, sys.stdout.buffer
# One segmenter for the whole stream, like the Vision request: the landscape model suits a 16:9 crop.
seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)
faces = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

# Tighten the matte: the soft outer edge carries the old background (bright sky reads as a halo on a dark board).
def levels(m):
    t = np.clip((m - 0.35) / 0.5, 0, 1)
    return t * t * (3 - 2 * t)
fade_rows, bridge = h // 9, 10   # bottom fade height; a face lost for fewer than `bridge` frames either side is a blink, not b-roll
fade = np.ones((h, 1), np.float32)
fade[h - fade_rows:, 0] = (h - 1 - np.arange(h - fade_rows, h)) / fade_rows

def read():
    buf = bytearray()
    while len(buf) < size:
        chunk = src.read(size - len(buf))
        if not chunk: return None
        buf += chunk
    return np.frombuffer(bytes(buf), np.uint8).reshape(h, w, 4).copy()

waiting, flags, written = deque(), [], 0
def flush(end, at_end):
    global written
    while written < end:
        i = written
        past = any(flags[max(0, i - bridge):i])
        future = any(flags[i + 1:i + 1 + bridge]) if i + 1 < len(flags) else at_end
        frame = waiting.popleft()
        if not (flags[i] or (past and future)): frame[..., 3] = 0
        dst.write(frame.tobytes())
        written += 1

while (frame := read()) is not None:
    rgb = np.ascontiguousarray(frame[..., 2::-1])
    m = seg.process(rgb).segmentation_mask
    frame[..., 3] = (levels(m) * fade * 255).round().astype(np.uint8) if m is not None else 0
    # A real talking-head frame has a large face in it; anything else is a cutaway.
    found = faces.process(rgb).detections or []
    flags.append(any(d.location_data.relative_bounding_box.height >= 0.2 for d in found))
    waiting.append(frame)
    flush(len(flags) - bridge, False)
flush(len(flags), True)
dst.flush()
