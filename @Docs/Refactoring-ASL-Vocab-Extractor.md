# Refactoring: Rename Script and Enable Global Execution

This document details the step-by-step solution to rename the ingestion script to `extractVocabASL.py` and make it executable globally from any directory using the terminal path.

## Goal
1. Rename `ingest_ASL_vocab_image.py` to `extractVocabASL.py`.
2. Make it executable from anywhere by integrating it into the `PATH` (using the existing `/Users/mbp-14/.local/bin/` folder).

---

## Step-by-Step Implementation

### Step 1: Rename the Ingestion Script
We renamed the main script using Git to preserve its history:
```bash
git mv ingest_ASL_vocab_image.py extractVocabASL.py
```

### Step 2: Make the Script Executable
We added executable permissions to `extractVocabASL.py` in the workspace:
```bash
chmod +x extractVocabASL.py
```

### Step 3: Create the Global Wrapper Script
We created a wrapper script at `/Users/mbp-14/.local/bin/extractVocabASL` since `/Users/mbp-14/.local/bin` is already in the user's `PATH` environment variable.

The wrapper script contains:
```bash
#!/usr/bin/env bash
set -euo pipefail
exec uv --directory "/Users/mbp-14/CLONED/NL-ASL_Vocab_Extractor" run python "/Users/mbp-14/CLONED/NL-ASL_Vocab_Extractor/extractVocabASL.py" "$@"
```

By using the `uv --directory` flag, the command automatically resolves all local packages and virtual environment dependencies (such as `pillow` and `asl_vocab`) regardless of which folder the user runs the command from.

### Step 4: Make the Wrapper Script Executable
We granted executable permissions to the wrapper:
```bash
chmod +x /Users/mbp-14/.local/bin/extractVocabASL
```

### Step 5: Update References
We updated the references in `README.md` to point to the new `extractVocabASL.py` and documented the global command `extractVocabASL`.

### Step 6: Refactor Number of Images Option to Interactive Prompt
We replaced the command-line argument `-n` / `--num-images` with an interactive console question with a default of 2. The user is prompted for the number of images to ingest (1-6) at the start of ingestion:
```python
    # Prompt for number of images
    num_images = 2
    while True:
        val = input("Number of images (1-6, default: 2): ").strip()
        if not val:
            break
        try:
            num = int(val)
            if 1 <= num <= 6:
                num_images = num
                break
        except ValueError:
            pass
        print("Invalid input. Please enter a number between 1 and 6, or press Enter for the default.")
```

### Step 7: Update Card Renderer for 5 and 6 Images
We updated `src/asl_vocab/card_renderer.py` to support layout configurations for 5 and 6 images:
- **5 images**: Arranged in a 3x2 grid with the 6th slot (bottom-right) reserved for the centered vocabulary word.
- **6 images**: Arranged in a 3x2 grid with all 6 slots filled with images and the word displayed in a dedicated text band at the bottom.

### Step 8: Coordinate-Based Capture & Global Hotkey (Option B)
We refactored `extractVocabASL.py` to use a global hotkey capture workflow:
1. **Calibration Mode (`--calibrate`)**: Running `extractVocabASL --calibrate` starts a 3-second countdown, giving you time to switch focus to Chrome. After the countdown, a fullscreen dimmed screen capture Tkinter window opens where you click-and-drag a red selection rectangle over your video player box. The `(x1, y1, x2, y2)` coordinates are saved locally to `.asl_vocab_coords.json` (ignored in `.gitignore`).
2. **Global Hotkey listener**: When running, the script runs a background `pynput` listener. You press `F8` from inside Chrome to capture the calibrated region (1 to 6 images) and press `F9` to finalize and compile the card.
3. **Beep Indicators**: Plays distinct sounds to confirm actions: `Tink` on capture (`F8`), `Glass` on finalize (`F9`), and `Sosumi` on errors or limits.
4. **Draft Preview**: Once finalized, a draft layout containing the string `"PREVIEW"` is created and opened via macOS `open`.
5. **AppleScript Input Prompt**: A native dialog box overlays on top of Chrome asking you for the vocabulary word. Once submitted, the final card is saved, the preview is closed, the clipboard is populated with the image/filename representation, and the hotkey listener resets.

---

## Usage

### 1. Calibrate Screen Coordinates
First, set up Chrome and open the video player. Run the calibration command:
```bash
extractVocabASL --calibrate
```
You will see a 3-second countdown. Focus your Chrome window immediately. Once the overlay opens, drag the box over the video player region and release.

### 2. Run Ingestion (from anywhere)
Start the tool from your terminal:
```bash
extractVocabASL
```
- Switch to Chrome and scrub your video.
- Press `F8` to capture screenshots (1 to 6 times).
- Press `F9` to compile the card (or capture 6 images to compile automatically).
- The Preview app will open showing the draft card.
- An AppleScript dialog will pop up over Chrome. Type the vocabulary word and press Enter to save.

For options/help:
```bash
extractVocabASL --help
```
