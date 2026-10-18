# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Claude Code skill (`SKILL.md`) that renders Khan Academy style explainer videos: a scene file (JS) describes beats, and `scripts/render.js` turns it into an MP4. `SKILL.md` is the user-facing reference for the scene API, layout rules, the draw-over-UI capture recipe and the real-audio clip pipeline. Read it before changing scene-facing behavior.

## Commands

Setup (once): `cd scripts && npm install && npx playwright install chromium`. Also needs ffmpeg/ffprobe on PATH, and a voice: macOS `say`; on Windows the installed System.Speech voices (via PowerShell), falling back to espeak-ng; `espeak-ng` on Linux. Kokoro runs from `scripts/.venv` (Python 3.12, made with `uv venv`) when it exists, else `KHAN_PYTHON`.

```sh
node scripts/render.js <scene.js> <out.mp4>              # render one scene; prints per-beat timings, WARN lines, and a contact-sheet path
KHAN_THEME=light node scripts/render.js <scene> <out>    # re-skin any scene as a whiteboard
KHAN_TTS=kokoro node scripts/render.js <scene> <out>     # local Kokoro voice (KHAN_PYTHON picks the interpreter)
node tests/run.js [outDir]                                # the test suite: render every examples/*.js and tests/languages/*.js
node tests/fonts.js                                       # which font face each script actually resolves to on this machine
```

There is no unit-test framework or linter. A "single test" is rendering one scene: `node scripts/render.js tests/languages/ar.js out/ar.mp4`. `tests/run.js` fails a scene on non-zero exit **or any `WARN` line** (text off the board, overlapping labels); a missing system voice counts as `skip`, not failure. CI (`.github/workflows/render.yml`) runs this on macOS and Ubuntu, once with the default voice and once with `KHAN_TTS=kokoro`.

## Architecture

Two halves talk across a Playwright page:

- **`scripts/board.html`** — the in-browser runtime. Defines the scene globals (`scene`, `write`, `stroke`, `arrow`, `oval`, `box`, `ring`, `around`, `seg`, `C` colors, …) and a `window.*` API that `render.js` drives: `sceneMeta`, `setTheme`, `loadImages`, `setTimings`, `frame(t)` (returns a JPEG data URL), `warnings`. Board coordinates are logical (1280×720 default, set via `size`) and rendered at `SCALE`. All wobble is deterministic (sin-based, never `Math.random`) because every frame redraws every stroke from scratch at progress `p`. `SCRIPTS` maps Unicode scripts to handwriting-appropriate fonts (Mac face first, Noto fallback; order matters — Urdu before Arabic, kana before Han); RTL scripts are written right to left.
- **`scripts/render.js`** — the Node driver. Injects the scene file into the page inside its own IIFE scope, reads `sceneMeta`, then **the voice drives the clock**: each beat's `say` is synthesized first and its measured duration (via ffprobe) becomes that beat's drawing window. Voice sources, in priority order: `audio` (a recorded file; beats need `at` timestamps), `eleven` (ElevenLabs, one take cut back into beats at character timings), `kokoro` (`scripts/kokoro_tts.py` via stdin JSON), then the system voice per beat: `say` on macOS (`SAY` map keyed by scene `lang`), System.Speech on Windows (matched by culture), espeak-ng as the fallback (`ESPEAK` map). ElevenLabs and Kokoro takes are cached in `.voice/` beside the scene. Frames are piped as MJPEG into ffmpeg and mixed with `adelay`ed audio clips. Afterwards it renders a QA contact sheet (the board at the end of each beat) and verifies the output duration.

Beat timing details that are easy to break: a beat's QA frame is sampled just past its end, so back-to-back beats (gap ≈ 0) finish 0.02s early to avoid capturing the next beat's wiped board.

Other scripts are for the real-audio clip mode: `clip_audio.py` (faster-whisper transcription, run with `uv`), `cutout.swift` (macOS Vision person cutout, compiled on first use to `scripts/cutout`) and its MediaPipe twin `cutout.py` for other systems (same stdin/stdout BGRA contract, same matte levels, bottom fade and b-roll bridging — keep the two in step), `talking_head_example.sh` (bash; on Windows run it from Git Bash).

Cross-platform pitfalls already handled: page URLs go through `pathToFileURL` (a bare `'file://' + path` breaks on `C:\`), Python files are opened as UTF-8 (Windows defaults to the locale code page), and `.gitattributes` keeps `*.sh` LF so bash can run them on `core.autocrlf` checkouts.

## Conventions

- `SKILL.md` at the root is the source of truth; `skills/khan-explainer/SKILL.md` is a copy for skills.sh discovery (identical except for a one-line note under the frontmatter). Keep them in sync when editing.
- Adding a language: add the voice to `SAY` (and `ESPEAK`/`KOKORO` if needed) in `render.js`, a face to `SCRIPTS` in `board.html` if it is a new script, and a `tests/languages/<code>.js` scene.
- Code style is dense: short names, one-line helpers, comments that explain *why*. Match it.
