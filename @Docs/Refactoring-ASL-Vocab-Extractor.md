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
We replaced the command-line argument `-n` / `--num-images` with an interactive console question with a default of 2. The user is prompted for the number of images to ingest (1-4) at the start of ingestion:
```python
    # Prompt for number of images
    num_images = 2
    while True:
        val = input("Number of images (1-4, default: 2): ").strip()
        if not val:
            break
        try:
            num = int(val)
            if 1 <= num <= 4:
                num_images = num
                break
        except ValueError:
            pass
        print("Invalid input. Please enter a number between 1 and 4, or press Enter for the default.")
```

---

## Usage

### Run from Workspace
To execute the tool from the project repository:
```bash
uv run python extractVocabASL.py
# or
python extractVocabASL.py
```

### Run from Anywhere
You can now run the tool from any folder in your terminal:
```bash
extractVocabASL
```

For options/help:
```bash
extractVocabASL --help
```
