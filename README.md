# Multimodal Coach

Real-time presentation / interview coaching that analyses **pose**, **facial expression**, **gaze**, and **speech** simultaneously from your MacBook webcam and microphone.

---

## What it does

| Modality | What is measured | Live feedback |
|---|---|---|
| **Pose** | Body tilt, head tilt, tremor, punch gesture | Overlay alerts (Korean + English) |
| **Expression** | Smile, brow tension, eye openness → confidence score | Score panel |
| **Gaze** | Gaze avoidance, eye jitter | Overlay alert after calibration |
| **Audio** | WPM, energy (volume), pitch variation | Bar meters + score panel |

A **live score panel** (bottom-left of the camera window) shows all four modality scores and a weighted overall score in real time.

Two extra modes use a reference video of Obama's 2004 DNC speech:
- **Practice** — side-by-side comparison with DTW pose-similarity bar + karaoke subtitles.
- **Test** — records a full run and produces a final 0–100 score breakdown.

---

## Quick start

### 1 — One-click (macOS Finder)

Double-click **`run_multimodal_coach.command`** in Finder.
The first time macOS will ask "allow Terminal to access camera/microphone" — click **Allow**.

> If macOS shows *"unidentified developer"*, right-click → **Open** → **Open** to bypass Gatekeeper (one-time only).

### 2 — Terminal

```bash
conda activate dslcv2
PYTHONPATH=src python apps/run_multimodal_coach.py
# Windoes Powershell 에서 실행하는 경우
$env:PYTHONPATH="src"; python apps/run_multimodal_coach.py
```

---

## Setup (first time)

```bash
# 1. Create / activate the conda environment
conda create -n dslcv2 python=3.11 -y
conda activate dslcv2

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pin mediapipe to the last version with the solutions API
pip install "mediapipe==0.10.14"
```

---

## Controls

| Key | Action |
|---|---|
| `Q` | Quit |
| Click **Practice Obama** | Start side-by-side practice mode |
| Click **Test Obama** | 3-second countdown then full scored test |
| `1` – `5` (Practice mode) | Playback speed × 0.5 / 1.0 / 1.25 / 1.5 / 2.0 |
| Click **← Quit** (Practice/Test) | Return to live coaching mode |

---

## Score weights

Defined as a class attribute in `Test4App` — edit freely:

```python
# src/multimodal_coach/app/runner.py
SCORE_WEIGHTS = {"pose": 0.35, "expression": 0.20, "gaze": 0.15, "audio": 0.30}
```

---

## macOS permissions troubleshooting

### Camera not detected

1. **System Settings → Privacy & Security → Camera**
2. Enable access for **Terminal** (or your IDE / Python launcher).
3. Restart the app.

If the webcam opens but shows a black frame, another app may hold the camera — quit FaceTime, Zoom, etc.

### Microphone not detected / audio score stuck at 50%

1. **System Settings → Privacy & Security → Microphone**
2. Enable access for **Terminal**.
3. The audio analyzer starts on launch; WPM/energy/pitch need a few seconds of speech to warm up.

### `AVCaptureDeviceTypeExternal is deprecated` warning

Harmless macOS SDK warning from OpenCV — the app works normally; ignore it.

### `mediapipe has no attribute 'solutions'`

mediapipe ≥ 0.10.20 removed the legacy solutions API. Fix:

```bash
pip install "mediapipe==0.10.14"
```

The `.command` launcher checks and fixes this automatically.

### Slow frame rate

- Close other camera-using apps (FaceTime, Photo Booth, Zoom).
- The Holistic model is CPU-heavy. Lowering resolution in `runner.py` (`cv2.CAP_PROP_FRAME_WIDTH/HEIGHT`) can help.

### Reference video / JSON not found

Assets must be present at:
```
assets/reference_videos/Obama's 2004 DNC keynote speech.mp4
assets/derived/Obama's 2004 DNC keynote speech.json
assets/subtitles/Obama's 2004 DNC keynote speech_subs.json
```
The `.npy` raw-pose file and speed-variant audio files are generated automatically on first launch of Practice/Test mode (requires `ffmpeg` on `$PATH` for audio extraction).

---

## Project structure

```
apps/
  run_multimodal_coach.py        # entry point
src/multimodal_coach/
  app/
    runner.py                    # Test4App — main orchestrator
  pipelines/
    vision/
      expression.py              # NEW — FaceMesh expression analyser
      pose_analyzer.py           # Pose metrics & Korean overlay alerts
      pose_comparator.py         # DTW-based pose similarity
      gaze.py                    # Gaze avoidance / jitter detector
      karaoke.py                 # Reference data extraction + similarity
      key_pose_extractor.py      # Peak-velocity gesture keyframe logging
    audio/
      audio_analyzer.py          # Real-time WPM / energy / pitch + final scoring
      event_analyzer.py          # Silence / filler / repair event detection
  api/
    feedback_server.py           # FastAPI + local LLM feedback endpoint
assets/
  reference_videos/
  reference_audio/
  derived/
  subtitles/
experiments/                     # Legacy pilot scripts (not used in production)
run_multimodal_coach.command     # One-click macOS launcher
```

---

## Optional: Speech Feedback API

Requires [LM Studio](https://lmstudio.ai) running locally with `qwen2.5-3b-instruct`.

```bash
PYTHONPATH=src uvicorn multimodal_coach.api.feedback_server:app --reload
# POST http://localhost:8000/feedback  with a SpeechScores JSON body
```
