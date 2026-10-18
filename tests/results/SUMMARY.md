# Windows feature test

**Overall: PASS. 45 of 45 automated checks passed. One item is NOT TESTED: the talking-head cutout with a real face.**

Machine: Windows 11, 15.8 GB RAM, Node 24, ffmpeg 9.0.1, eSpeak NG 1.52.0, Kokoro in `scripts/.venv` (Python 3.12), faster-whisper `small.en` through `uvx --python 3.12`.

## Run 1 (2026-10-18)

These checks passed. Claude Code then stopped the run because the system was low on memory, before the clip steps.

| Test | Result | Log | Output |
|---|---|---|---|
| Fonts per script (16 scripts) | PASS: every script uses an installed face | `fonts.txt` | — |
| Built-in voices: 4 examples + 15 languages | PASS: 19/19 | `builtin.txt` | `builtin/*.mp4`, `builtin/*-sheet.jpg` |
| Kokoro voice: same 19 scenes | PASS: 19/19 | `kokoro.txt` | `kokoro/*.mp4`, `kokoro/*-sheet.jpg` |

In run 1 the light-theme step failed because the test script never created `light/`. The renderer was not at fault. `steps.txt` is that run's step log.

## Run 2 (2026-10-19): continuation, the 38 passed tests not repeated

Before starting, 2.6 GB of physical memory was free and Windows could commit 22.5 GB more (33.3 GB in use, 55.8 GB limit). Each step ran only when at least 1.5 GB was free, and it ran alone: one Chromium and one ffmpeg at a time. Whisper and MediaPipe never ran at the same time. Free memory stayed between 2.58 and 2.73 GB from start to finish. Every row of this table is also in `results.tsv`.

| Test | Result | Time | Log | Output |
|---|---|---|---|---|
| Light theme (`KHAN_THEME=light`, ai-agents) | PASS | 10s | `light.txt` | `light/ai-agents.mp4`, `light/ai-agents-sheet.jpg` |
| Transcribe (faster-whisper, offline from the cached model) | PASS: 5 lines, word for word | 9s | `transcribe.txt` | `clip/transcript.txt`, `clip/transcript.json` |
| Cut one clip | PASS: `ok`, no `CHECK` | 3s | `cut.txt` | `clip/clips/01-the-loop/audio.wav`, `words.txt` |
| Real-audio render, dark | PASS: 7.80s | 3s | `clip-render-dark.txt` | `clip/clips/01-the-loop/out.mp4`, `out-sheet.jpg` |
| Real-audio render, light | PASS: 7.80s | 3s | `clip-render-light.txt` | `clip/clips/01-the-loop/out-light.mp4`, `out-light-sheet.jpg` |
| Talking head, dark (MediaPipe cutout) | PASS | 8s | `talking-head-dark.txt` | `clip/clips/01-the-loop/cutout.mov`, `head.mp4` |
| Talking head, light (reuses `cutout.mov`) | PASS | 1s | `talking-head-light.txt` | `clip/clips/01-the-loop/head-light.mp4` |
| Talking head with a real face | **NOT TESTED** | — | — | — |

## Talking-head test details

The source was a generated test pattern (`clip/src-noface.mp4`), so this test covers only how the pipeline behaves with no face. The cutout found no face, and the alpha channel of `cutout.mov` is 0 in all 219 frames, which is correct: b-roll stays hidden. `clip/head-frames.jpg` shows one frame of each look, with the board at the top and nothing pasted below it. The repo and the installed packages contain no face sample, and personal photo and video folders were not searched. So the matte quality, the face detection and the blink bridging on real footage are still unchecked. To check them, run `scripts/talking_head_example.sh` on a clip with a person speaking to camera.

## Not covered

- **ElevenLabs:** needs an API key.
- **YouTube download:** YouTube needs a sign-in, and yt-dlp can't read Chrome or Edge cookies on Windows. See `SKILL.md`, step 1 of "Real-audio clips".
