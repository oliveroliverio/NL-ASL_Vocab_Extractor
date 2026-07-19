from datetime import datetime
import re
import argparse

from PIL import ImageGrab

from asl_vocab.config import CARD_OUTPUT_DIR, GALLERY_OUTPUT_PATH, unit_slug
from asl_vocab.card_renderer import render_card
from asl_vocab.gallery_renderer import (
    generate_gallery_markdown,
    generate_unit_galleries,
)


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


def get_clipboard_image():
    img = ImageGrab.grabclipboard()

    if img is None:
        raise SystemExit("No image found in clipboard.")

    return img.convert("RGB")


def clipboard_mode(num_images: int):
    print("\nASL Vocab Image Ingest\n")

    images = []

    for i in range(1, num_images + 1):
        input(
            f"Take screenshot #{i} with Shift-Control-Command-4, "
            "then press Enter..."
        )
        images.append(get_clipboard_image())

    word = input("ASL word / phrase: ").strip()

    if not word:
        raise SystemExit("No word entered.")

    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    filename = f"{unit_slug()}_{slugify(word)}_{timestamp}.png"
    output_path = CARD_OUTPUT_DIR / filename

    result = render_card(
        word=word,
        images=images,
        output_path=output_path,
    )

    print(f"\nCreated card:\n{result}\n")

    refresh_gallery()


def main():
    parser = argparse.ArgumentParser(
        description="ASL Vocabulary Image Ingestion"
    )

    parser.add_argument(
        "-n",
        "--num-images",
        type=int,
        choices=[1, 2, 3, 4],
        default=2,
        help="Number of screenshots/images to include in the card.",
    )

    parser.add_argument(
        "--refresh-gallery",
        action="store_true",
        help="Regenerate GALLERY.md from existing cards.",
    )

    args = parser.parse_args()

    if args.refresh_gallery:
        refresh_gallery()
        return

    clipboard_mode(num_images=args.num_images)


if __name__ == "__main__":
    main()