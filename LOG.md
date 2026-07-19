# Git Commit Log

## [REFACTOR] Rename ingestion script and configure global execution

**Commit Message:**
REFACTOR: Rename ingest_ASL_vocab_image.py to extractVocabASL.py and make executable from anywhere in PATH

- Renamed `ingest_ASL_vocab_image.py` to `extractVocabASL.py`.
- Created wrapper script `extractVocabASL` in `/Users/mbp-14/.local/bin/` to run the tool from any folder using the project's local virtual environment via `uv`.
- Configured file permissions with `chmod +x` on both files.
- Created documentation in `@Docs/Refactoring-ASL-Vocab-Extractor.md` detailing implementation and usage.
- Updated `README.md` to reference the new command names and paths.

**Files Changed:**
- `ingest_ASL_vocab_image.py` (Deleted/Renamed)
- `extractVocabASL.py` (New/Renamed)
- `README.md` (Modified)
- `@Docs/Refactoring-ASL-Vocab-Extractor.md` (New)
- `/Users/mbp-14/.local/bin/extractVocabASL` (New wrapper created in PATH, outside repo)

**Terminal Commands Run:**
- `git mv ingest_ASL_vocab_image.py extractVocabASL.py`
- `chmod +x extractVocabASL.py`
- `chmod +x /Users/mbp-14/.local/bin/extractVocabASL`

## [REFACTOR] Move number of images option from CLI argument to interactive console prompt

**Commit Message:**
REFACTOR: Prompt for number of images in console instead of using -n/--num-images argument

- Removed `-n` / `--num-images` from `argparse` in `extractVocabASL.py`.
- Refactored `clipboard_mode` to prompt for `num_images` interactively on start, defaulting to 2 when Enter is pressed.
- Updated `@Docs/Refactoring-ASL-Vocab-Extractor.md` to document the interactive prompt step.

**Files Changed:**
- `extractVocabASL.py` (Modified)
- `@Docs/Refactoring-ASL-Vocab-Extractor.md` (Modified)

**Terminal Commands Run:**
- None

## [REFACTOR] Support up to 6 images in card layout and update console prompt

**Commit Message:**
REFACTOR: Support up to 6 images in card renderer layouts and update console prompt range to 1-6

- Modified `src/asl_vocab/card_renderer.py` to allow rendering 5 or 6 images.
- Added 3x2 grid layouts for 5 and 6 images.
- Updated `extractVocabASL.py` prompt text and range validation to support 1-6 images.
- Updated `README.md` and documentation in `@Docs/Refactoring-ASL-Vocab-Extractor.md`.

**Files Changed:**
- `src/asl_vocab/card_renderer.py` (Modified)
- `extractVocabASL.py` (Modified)
- `README.md` (Modified)
- `@Docs/Refactoring-ASL-Vocab-Extractor.md` (Modified)

**Terminal Commands Run:**
- None

## [FEAT] Implement coordinate-based capture with global hotkey and AppleScript input dialog

**Commit Message:**
FEAT: Implement coordinate calibration, F8 global hotkey capture, and AppleScript preview workflow

- Added `pynput` as project dependency to support global hotkeys.
- Added `.asl_vocab_coords.json` to `.gitignore`.
- Created calibration mode (`--calibrate`) in `extractVocabASL.py` using a transparent Tkinter selection overlay.
- Added `hotkey_mode()` to listen globally for `F8` press, taking screenshots of the calibrated region using Pillow `ImageGrab`.
- Implemented temporary draft rendering, automatic Preview.app opening, and blocking AppleScript input popup dialog.
- Updated documentation in `@Docs/Refactoring-ASL-Vocab-Extractor.md` with calibration and usage instructions.

**Files Changed:**
- `pyproject.toml` (Modified)
- `.gitignore` (Modified)
- `extractVocabASL.py` (Modified)
- `@Docs/Refactoring-ASL-Vocab-Extractor.md` (Modified)

**Terminal Commands Run:**
- `uv sync`

## [BUGFIX] Display screen capture as overlay background in coordinate selector

**Commit Message:**
BUGFIX: Use screen capture as Tkinter selector background to solve black overlay bug on macOS

- Replaced semi-transparent root alpha window attribute with a static fullscreen screenshot background.
- Dimmed the screenshot background image using PIL blend.
- Added Retina scaling support by resizing the background screenshot to logical screen dimensions.
- Added `lift()` and `focus_force()` to ensure overlay opens in front of other apps.

**Files Changed:**
- `extractVocabASL.py` (Modified)

**Terminal Commands Run:**
- None

## [BUGFIX] Prevent native macOS fullscreen desktop swiping and PIL blend mode mismatch

**Commit Message:**
BUGFIX: Use borderless geometry and convert screen capture to RGB in coordinate selector

- Replaced native Tkinter fullscreen window mode with borderless geometry `overrideredirect(True)` and screen size calculation to avoid swiping to a new macOS desktop space.
- Added `convert("RGB")` to screenshot image before resizing to prevent `images do not match` mode mismatch errors in `Image.blend`.

**Files Changed:**
- `extractVocabASL.py` (Modified)

**Terminal Commands Run:**
- None

## [BUGFIX] Add countdown before calibration capture and revert to native fullscreen on macOS

**Commit Message:**
BUGFIX: Add 3-second countdown before screen grab and use native fullscreen for macOS focus

- Added 3-second countdown to `calibrate_coords` to give the user time to bring Chrome to front.
- Reverted to macOS native fullscreen mode (`self.root.attributes("-fullscreen", True)`) in coordinate selector to correctly steal active window focus and allow Escape key binding to close the overlay.

**Files Changed:**
- `extractVocabASL.py` (Modified)

**Terminal Commands Run:**
- None

## [FEAT] Add incrementing number badges on card images

**Commit Message:**
FEAT: Render incrementing number badges on top-right of each image on the card

- Created `draw_image_number` helper in `src/asl_vocab/card_renderer.py` to draw a clean circular badge with the image sequence number (1, 2, 3, etc.).
- Integrated the drawing loop at the end of the `render_card` function to dynamically place numbers on all images based on their positions.

**Files Changed:**
- `src/asl_vocab/card_renderer.py` (Modified)

**Terminal Commands Run:**
- None

## [FEAT] Copy final card and filename to system clipboard

**Commit Message:**
FEAT: Automatically copy generated card image and its filename to macOS system clipboard

- Replaced clipboard purge code with PyObjC `NSPasteboard` writing logic.
- Configured Cocoa pasteboard to store the final image data as `NSPasteboardTypeTIFF` and the filename string as `NSPasteboardTypeString` simultaneously, enabling seamless pasting as either text or image depending on the target app.

**Files Changed:**
- `extractVocabASL.py` (Modified)

**Terminal Commands Run:**
- None
