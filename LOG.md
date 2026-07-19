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
