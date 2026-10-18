# khan-explainer

A Claude Code skill that makes Khan Academy style explainer videos: a pen draws while a voice explains. You describe the video, Claude writes a scene file, and one command renders the MP4.

Write-up: [Claude Code skills for content: how I make Khan Academy style videos for free](https://haiderfarooq.dev/blog/claude-code-skills-for-content)

![The same scene on the blackboard and on the whiteboard](docs/board.jpg)

It runs on your own machine (macOS, Windows or Linux) with an HTML canvas, Playwright, ffmpeg and the system's built-in voice. No API keys, no accounts, no editor.

## What it makes

| Mode | What you get |
|---|---|
| Blackboard lesson | A diagram drawn stroke by stroke while the voice explains it. |
| Draw-over-UI tutorial | Arrows, circles and numbered steps drawn over your product screenshots. |
| Real-audio clip | A YouTube video or podcast in, vertical shorts out. The speaker's own voice plays while the board is drawn to their words. It can also cut the speaker out and stand them in front of the board. |

Every mode renders as chalk on a blackboard or marker on a whiteboard, landscape or vertical. One flag switches between them, and a single beat can flip the board mid-video.

## Why the pen stays in sync

The voice drives the clock. A scene is a list of beats, and a beat is one spoken clause plus the drawing that happens while it is said. The renderer speaks each beat first, measures it, and fits that beat's drawing to its length. Nobody types a timestamp, so the pen cannot run ahead of the words.

```js
scene({
  beats: [
    { say: 'What is an AI agent?', draw: p => {
        write('What is an AI agent?', 60, 85, p, { size: 56, color: C.yellow });
    } },
    { say: "It's software that uses a language model to think,", draw: p => {
        stroke(oval(300, 330, 155, 82), seg(p, 0, .4), { color: C.blue });
        write('1. THINK', 300, 328, seg(p, .4, 1), { size: 40, color: C.blue, center: true });
    } },
  ],
})
```

## Install

You need Node 20 or newer and ffmpeg.

**macOS**

```sh
brew install ffmpeg
git clone https://github.com/WENGENG-boop/khan-explainer ~/.claude/skills/khan-explainer
cd ~/.claude/skills/khan-explainer/scripts && npm install && npx playwright install chromium
```

**Windows** (PowerShell)

```powershell
winget install Gyan.FFmpeg eSpeak-NG.eSpeak-NG astral-sh.uv
git clone https://github.com/WENGENG-boop/khan-explainer $HOME\.claude\skills\khan-explainer
cd $HOME\.claude\skills\khan-explainer\scripts; npm install; npx playwright install chromium
```

Open a new terminal afterwards so the new PATH is picked up. English and Chinese speak with the voices Windows ships; add more under Settings > Time & language > Speech, and espeak-ng speaks every other language. Run the talking-head script from Git Bash.

**Linux** (Debian/Ubuntu)

```sh
sudo apt install ffmpeg espeak-ng fonts-noto-core fonts-noto-cjk fonts-noto-extra
git clone https://github.com/WENGENG-boop/khan-explainer ~/.claude/skills/khan-explainer
cd ~/.claude/skills/khan-explainer/scripts && npm install && npx playwright install --with-deps chromium
```

| | macOS | Windows | Linux |
|---|---|---|---|
| Free voice | `say` | Windows voices, then espeak-ng | espeak-ng |
| Handwriting font | Bradley Hand | Ink Free | system cursive |
| Talking-head cutout | macOS Vision | MediaPipe | MediaPipe |

## Use

Ask Claude Code for the video you want:

> Make a 30-second Khan-style explainer on how DNS works.

> Draw over these screenshots and show a new user how to send their first invoice.

> Khanify this YouTube video: find the best moments and clip them, light and dark.

Or render one of the examples yourself:

```sh
cd ~/.claude/skills/khan-explainer
node scripts/render.js examples/ai-agents.js agents.mp4                    # blackboard
KHAN_THEME=light node scripts/render.js examples/ai-agents.js light.mp4    # whiteboard
node scripts/render.js examples/ui-tutorial.js tutorial.mp4                # drawn over screenshots
node scripts/render.js examples/arabic.js arabic.mp4                      # right-to-left writing
node scripts/render.js examples/languages.js languages.mp4                # one word in eight languages
```

In PowerShell, set the theme first: `$env:KHAN_THEME='light'; node scripts/render.js examples/ai-agents.js light.mp4` (then `Remove-Item env:KHAN_THEME`).

Each render also prints the path of a contact sheet: the board at the end of every beat, in one image. That sheet is how Claude checks its own layout before it shows you anything.

[SKILL.md](SKILL.md) is the full reference: the scene API, layout rules, the capture recipe for tutorials and the clip pipeline.

## Optional extras

- **A human voice.** Export `ELEVENLABS_API_KEY` and add `eleven: '<voice id>'` to a scene. The script is read in one take and cut back into beats, and takes are cached, so re-rendering the same words is free.
- **Kokoro, a free local human voice.** Install it into a Python 3.12 environment at `scripts/.venv`, which the renderer finds on its own: `uv venv --python 3.12 scripts/.venv`, then `uv pip install --python scripts/.venv kokoro soundfile`. Put `kokoro: true` on a scene, or set `KHAN_TTS=kokoro` for any scene. English, Spanish, French, Hindi, Italian, Japanese, Portuguese and Chinese. [SKILL.md](SKILL.md) lists the extra packages for Japanese and Chinese.
- **Any language on the board.** Arabic, Urdu and Hebrew are written right to left, Hindi, Thai, Chinese, Japanese, Korean, Russian and more left to right, each in a face that writes it properly. `lang: 'ar'` on a scene picks the matching voice. `node tests/run.js` renders them all.
- **Real-audio clips** need [uv](https://docs.astral.sh/uv/). `scripts/clip_audio.py` transcribes locally with faster-whisper. On Windows, yt-dlp cannot read Chrome or Edge cookies: export a `cookies.txt` from a signed-in YouTube tab and pass `--cookies cookies.txt`.
- **The talking-head cutout** uses macOS Vision, which builds itself with `swiftc` the first time (needs the Xcode command line tools). On Windows and Linux it uses MediaPipe instead, fetched by `uv`.
- **Slow model downloads.** Kokoro and faster-whisper download their models from Hugging Face on first use. If that hangs, set `HF_ENDPOINT=https://hf-mirror.com` for the first run.

## Tests

`node tests/run.js` renders every example and fifteen languages and fails on any layout warning; `node tests/fonts.js` shows which font each script gets. The latest full Windows run is in [tests/results/SUMMARY.md](tests/results/SUMMARY.md): 45 of 45 checks pass, with the talking head on real footage still to be verified.

## Credits

Made by [Haider Farooq](https://github.com/haiderfarooq3). Windows support in this fork by [WENGENG-boop](https://github.com/WENGENG-boop). MIT licensed: use it, change it, ship videos with it.

Not affiliated with or endorsed by Khan Academy. "Khan Academy style" describes the look: handwriting on a board, drawn as it is explained.
