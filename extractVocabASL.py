from datetime import datetime
import re
import argparse
import json
import os
import subprocess
import threading
from pathlib import Path
from PIL import ImageGrab, Image, ImageTk

from asl_vocab.config import CARD_OUTPUT_DIR, GALLERY_OUTPUT_PATH, unit_slug
from asl_vocab.card_renderer import render_card
from asl_vocab.gallery_renderer import (
    generate_gallery_markdown,
    generate_unit_galleries,
)

COORDS_FILE = ".asl_vocab_coords.json"


def refresh_gallery():
    gallery_path = generate_gallery_markdown(
        image_dir=CARD_OUTPUT_DIR,
        output_markdown_path=GALLERY_OUTPUT_PATH,
    )

    unit_gallery_paths = generate_unit_galleries(
        image_dir=CARD_OUTPUT_DIR,
        output_dir=GALLERY_OUTPUT_PATH.parent,
    )

    print(f"\nUpdated main gallery:\n{gallery_path}\n")

    for path in unit_gallery_paths:
        print(f"Updated unit gallery: {path}")


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def get_coords():
    if not os.path.exists(COORDS_FILE):
        return None
    try:
        with open(COORDS_FILE, "r") as f:
            data = json.load(f)
            return (data["x1"], data["y1"], data["x2"], data["y2"])
    except Exception:
        return None


def save_coords(x1, y1, x2, y2):
    with open(COORDS_FILE, "w") as f:
        json.dump({"x1": x1, "y1": y1, "x2": x2, "y2": y2}, f)


def calibrate_coords():
    print("\nCalibration Mode:")
    print("1. Switch to your Chrome window (ensure the video player is visible).")
    print("2. A screenshot will be captured in 3 seconds to use for alignment.")
    print("3. Draw a rectangle over the video player region to calibrate.")
    print("Press Escape on the overlay screen to cancel without saving.")

    import time
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)

    try:
        import tkinter as tk
    except ImportError:
        print("\nError: tkinter is not installed or configured on your system python.")
        print(f"Please manually create/edit '{COORDS_FILE}' in the project root with content like:")
        print('{"x1": 100, "y1": 200, "x2": 600, "y2": 700}')
        return

    try:
        # Take screen capture after the countdown when Chrome is active
        screen_img = ImageGrab.grab()

        class Selector:
            def __init__(self):
                self.root = tk.Tk()
                self.root.config(cursor="cross")

                # Use macOS native fullscreen to open overlay directly on top of fullscreen apps and capture focus
                self.root.attributes("-fullscreen", True)
                
                # Bring window to absolute front
                self.root.lift()
                self.root.focus_force()

                self.root.bind("<Escape>", lambda e: self.root.destroy())

                # Get logical dimensions
                logical_w = self.root.winfo_screenwidth()
                logical_h = self.root.winfo_screenheight()

                # Resize screen capture to match logical screen dimensions (Retina scaling)
                try:
                    resample_mode = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_mode = Image.ANTIALIAS
                
                # Convert screenshot to RGB to avoid mode mismatch errors during blending
                resized_img = screen_img.convert("RGB").resize((logical_w, logical_h), resample_mode)
                
                # Blend screen image with 30% black to dim it for selection mode
                dimmed_img = Image.blend(resized_img, Image.new("RGB", resized_img.size, "black"), 0.3)
                
                self.bg_photo = ImageTk.PhotoImage(dimmed_img)

                self.canvas = tk.Canvas(self.root, cursor="cross", highlightthickness=0)
                self.canvas.pack(fill="both", expand=True)
                
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

                self.canvas.bind("<ButtonPress-1>", self.on_press)
                self.canvas.bind("<B1-Motion>", self.on_drag)
                self.canvas.bind("<ButtonRelease-1>", self.on_release)

                self.start_x = None
                self.start_y = None
                self.rect = None
                self.coords = None

            def on_press(self, event):
                self.start_x = event.x
                self.start_y = event.y
                self.rect = self.canvas.create_rectangle(
                    self.start_x, self.start_y, self.start_x, self.start_y,
                    outline="red", width=3
                )

            def on_drag(self, event):
                self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

            def on_release(self, event):
                x1 = min(self.start_x, event.x)
                y1 = min(self.start_y, event.y)
                x2 = max(self.start_x, event.x)
                y2 = max(self.start_y, event.y)

                if (x2 - x1) > 10 and (y2 - y1) > 10:
                    self.coords = (x1, y1, x2, y2)
                self.root.destroy()

            def run(self):
                self.root.mainloop()
                return self.coords

        selector = Selector()
        coords = selector.run()
        if coords:
            save_coords(*coords)
            print(f"\nSuccessfully calibrated! Coordinates saved: {coords}")
        else:
            print("\nCalibration cancelled or selection too small.")
    except Exception as e:
        print(f"\nFailed to run Tkinter calibration overlay: {e}")
        print(f"Please manually configure coordinates in '{COORDS_FILE}'.")


def play_beep():
    subprocess.Popen(
        ["afplay", "/System/Library/Sounds/Tink.aiff"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def play_done_beep():
    subprocess.Popen(
        ["afplay", "/System/Library/Sounds/Glass.aiff"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def play_error_beep():
    subprocess.Popen(
        ["afplay", "/System/Library/Sounds/Sosumi.aiff"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def ask_for_word_applescript() -> str | None:
    script = (
        'display dialog "Enter the ASL word/phrase for this card (or click Cancel to discard):" '
        'default answer "" '
        'with title "ASL Vocab Extractor" '
        'buttons {"Cancel", "OK"} '
        'default button "OK"'
    )
    try:
        res = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        out = res.stdout.strip()
        match = re.search(r"text returned:(.*)", out)
        if match:
            return match.group(1).strip()
        return ""
    except subprocess.CalledProcessError:
        return None


def hotkey_mode():
    coords = get_coords()
    if not coords:
        print(f"\nError: Coordinates not calibrated. Please run with --calibrate first:")
        print("  extractVocabASL --calibrate\n")
        raise SystemExit(1)

    print("\nASL Vocab Image Ingest (Dynamic Coordinate Hotkey Mode)")
    print("Press F8 inside Chrome to capture a screenshot (1 to 8 images).")
    print("Press F9 inside Chrome to finalize and compile the card.")
    print("Active Coordinates:", coords)

    captured_images = []
    lock = threading.Lock()
    is_processing = False

    def process_captured_set():
        nonlocal is_processing
        print(f"\nProcessing captured set ({len(captured_images)} images)...")
        preview_path = Path("/tmp/asl_vocab_preview.png")
        
        try:
            # Render temporary preview card
            render_card(word="PREVIEW", images=captured_images, output_path=preview_path)
            
            # Open preview
            subprocess.Popen(["open", str(preview_path)])
            
            # Prompt for word via AppleScript
            word = ask_for_word_applescript()
            
            # Close Preview window named after preview file
            try:
                subprocess.run(
                    ["osascript", "-e", 'tell application "Preview" to close (every window whose name contains "asl_vocab_preview.png")'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

            if word is not None and word.strip() != "":
                # Save final card
                timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
                filename = f"{unit_slug()}_{slugify(word)}_{timestamp}.png"
                output_path = CARD_OUTPUT_DIR / filename
                
                render_card(word=word, images=captured_images, output_path=output_path)
                print(f"Created card: {output_path.name}")
                refresh_gallery()
                
                # Copy the generated card image and its filename to the system clipboard
                try:
                    from AppKit import NSPasteboard, NSPasteboardTypeTIFF, NSPasteboardTypeString, NSImage

                    image = NSImage.alloc().initByReferencingFile_(str(output_path))
                    if image:
                        tiff_data = image.TIFFRepresentation()
                        if tiff_data:
                            pb = NSPasteboard.generalPasteboard()
                            pb.clearContents()
                            pb.declareTypes_owner_([NSPasteboardTypeTIFF, NSPasteboardTypeString], None)
                            pb.setData_forType_(tiff_data, NSPasteboardTypeTIFF)
                            pb.setString_forType_(filename, NSPasteboardTypeString)
                            print(f"Copied card image and filename '{filename}' to system clipboard!")
                except Exception as clipboard_err:
                    print(f"Failed to copy final card to clipboard: {clipboard_err}")
            else:
                print("Ingest cancelled. Discarding screenshots.")
        except Exception as e:
            print(f"Error during final processing: {e}")
        finally:
            # Clean up temporary preview file
            if preview_path.exists():
                try:
                    preview_path.unlink()
                except Exception:
                    pass
            
            with lock:
                captured_images.clear()
                is_processing = False
                print("\nReady for next set. Press F8 to capture, F9 to finalize (0 captured)...")

    def on_press(key):
        nonlocal is_processing
        try:
            from pynput import keyboard
        except ImportError:
            return

        # F8: Capture screenshot
        if key == keyboard.Key.f8:
            with lock:
                if is_processing:
                    return
                if len(captured_images) >= 8:
                    print("Maximum of 8 images already reached. Press F9 to finalize.")
                    play_error_beep()
                    return

                try:
                    # Capture exact screen bounding box
                    img = ImageGrab.grab(bbox=coords)
                    captured_images.append(img.convert("RGB"))
                    play_beep()
                    print(f"Captured {len(captured_images)} (max 8)...")

                    # If 8 images reached, automatically trigger processing
                    if len(captured_images) == 8:
                        is_processing = True
                        print("Reached maximum limit (8 images). Finalizing automatically...")
                        threading.Thread(target=process_captured_set, daemon=True).start()
                except Exception as e:
                    print(f"Error capturing: {e}")

        # F9: Finalize set
        elif key == keyboard.Key.f9:
            with lock:
                if is_processing:
                    return
                if len(captured_images) == 0:
                    print("No screenshots captured yet. Press F8 first.")
                    play_error_beep()
                    return
                
                is_processing = True
                play_done_beep()
                threading.Thread(target=process_captured_set, daemon=True).start()

    try:
        from pynput import keyboard
    except ImportError:
        print("\nError: pynput package is missing. Please run `uv sync` first.\n")
        raise SystemExit(1)

    print(f"\nStarting global keyboard listener. Listening for F8 / F9 keys...")
    print("Keep Chrome active. Press F8 to capture, F9 to compile.")
    print("Press Ctrl+C in this terminal window to stop the listener.\n")
    print("Ready for first set. Press F8 to capture (0 captured)...")

    # Start the non-blocking global hotkey listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        # Keep main thread alive while pynput listener runs in background
        listener.join()
    except KeyboardInterrupt:
        print("\nStopping listener...")
        listener.stop()


def main():
    parser = argparse.ArgumentParser(
        description="ASL Vocabulary Image Ingestion"
    )

    parser.add_argument(
        "--refresh-gallery",
        action="store_true",
        help="Regenerate GALLERY.md from existing cards.",
    )

    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Calibrate screen coordinate region for auto-capture.",
    )

    args = parser.parse_args()

    if args.refresh_gallery:
        refresh_gallery()
        return

    if args.calibrate:
        calibrate_coords()
        return

    hotkey_mode()


if __name__ == "__main__":
    main()