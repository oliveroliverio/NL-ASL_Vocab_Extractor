from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from .config import ASL_VOCAB_LAYOUT


def load_image(image_source):
    if isinstance(image_source, Image.Image):
        return image_source.convert("RGB")

    return Image.open(image_source).convert("RGB")


def fit_image(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    img = img.convert("RGB")
    img.thumbnail(target_size)

    canvas = Image.new("RGB", target_size, "white")
    x = (target_size[0] - img.width) // 2
    y = (target_size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def get_font(size: int | None = None):
    layout = ASL_VOCAB_LAYOUT
    size = size or layout.font_size

    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    ]

    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    max_font_size: int,
):
    x1, y1, x2, y2 = box
    text = text.replace("_", " ")

    font_size = max_font_size

    while font_size >= 24:
        font = get_font(font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        if text_w <= (x2 - x1 - 20) and text_h <= (y2 - y1 - 20):
            break

        font_size -= 4

    text_x = x1 + ((x2 - x1) - text_w) // 2
    text_y = y1 + ((y2 - y1) - text_h) // 2

    draw.text((text_x, text_y), text, fill="black", font=font)


def draw_border(draw: ImageDraw.ImageDraw):
    layout = ASL_VOCAB_LAYOUT

    for i in range(layout.border_width):
        draw.rectangle(
            [i, i, layout.card_width - 1 - i, layout.card_height - 1 - i],
            outline="black",
        )


def draw_image_number(
    draw: ImageDraw.ImageDraw,
    number: int,
    pos: tuple[int, int],
    size: tuple[int, int],
):
    # Calculate top-right corner of the image box
    x = pos[0] + size[0]
    y = pos[1]

    # Badge radius / size (scaled slightly if tile is small)
    radius = 16 if size[0] < 300 else 18
    # Center of the circle: offset slightly inside the top-right corner of the image
    center_x = x - radius - 8
    center_y = y + radius + 8

    # Draw filled circle with border
    draw.ellipse(
        [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
        fill="white",
        outline="black",
        width=2,
    )

    font_sz = 18 if size[0] < 300 else 22
    font = get_font(font_sz)

    # Draw the number text centered in the circle
    text = str(number)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_x = center_x - text_w // 2
    text_y = center_y - text_h // 2 - 2

    draw.text((text_x, text_y), text, fill="black", font=font)


def render_card(
    word: str,
    images: list[str | Path | Image.Image],
    output_path: str | Path,
) -> Path:
    layout = ASL_VOCAB_LAYOUT

    if len(images) not in {1, 2, 3, 4, 5, 6, 7, 8}:
        raise ValueError("render_card supports 1, 2, 3, 4, 5, 6, 7, or 8 images.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    card = Image.new(
        "RGB",
        (layout.card_width, layout.card_height),
        "white",
    )
    draw = ImageDraw.Draw(card)

    loaded_images = [load_image(img) for img in images]
    positions = []
    image_size = (0, 0)

    m = layout.margin
    gap = getattr(layout, "gap", 14)

    # 1 image: centered large image
    if len(loaded_images) == 1:
        tile_w = layout.card_width - (m * 2)
        tile_h = 600
        img = fit_image(loaded_images[0], (tile_w, tile_h))

        pos = (m, m)
        card.paste(img, pos)
        positions = [pos]
        image_size = (tile_w, tile_h)

        text_box = (
            m,
            m + tile_h + gap,
            layout.card_width - m,
            layout.card_height - m,
        )
        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # 2 images: offset diagonal layout
    elif len(loaded_images) == 2:
        img1 = fit_image(
            loaded_images[0],
            (layout.image_width, layout.image_height),
        )
        img2 = fit_image(
            loaded_images[1],
            (layout.image_width, layout.image_height),
        )

        pos1 = (m, m)
        pos2 = (
            layout.card_width - layout.image_width - m,
            layout.card_height - layout.image_height - m,
        )
        card.paste(img1, pos1)
        card.paste(img2, pos2)
        positions = [pos1, pos2]
        image_size = (layout.image_width, layout.image_height)

        text_box = (
            m,
            layout.card_height - layout.image_height - m,
            layout.card_width - layout.image_width - m - gap,
            layout.card_height - m,
        )
        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # 3 images: two top, one bottom-left, word in bottom-right blank space
    elif len(loaded_images) == 3:
        tile_w = (layout.card_width - (m * 2) - gap) // 2
        tile_h = (layout.card_height - (m * 2) - gap) // 2

        positions = [
            (m, m),
            (m + tile_w + gap, m),
            (m, m + tile_h + gap),
        ]
        image_size = (tile_w, tile_h)

        for img_source, pos in zip(loaded_images, positions):
            img = fit_image(img_source, (tile_w, tile_h))
            card.paste(img, pos)

        text_box = (
            m + tile_w + gap,
            m + tile_h + gap,
            layout.card_width - m,
            layout.card_height - m,
        )

        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # 4 images: 2x2 grid, word at bottom
    elif len(loaded_images) == 4:
        text_band_h = 100

        tile_w = (layout.card_width - (m * 2) - gap) // 2
        tile_h = (layout.card_height - text_band_h - (m * 2) - gap) // 2

        positions = [
            (m, m),
            (m + tile_w + gap, m),
            (m, m + tile_h + gap),
            (m + tile_w + gap, m + tile_h + gap),
        ]
        image_size = (tile_w, tile_h)

        for img_source, pos in zip(loaded_images, positions):
            img = fit_image(img_source, (tile_w, tile_h))
            card.paste(img, pos)

        text_box = (
            m,
            layout.card_height - text_band_h,
            layout.card_width - m,
            layout.card_height - m,
        )

        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # 5 images: 3x2 grid, bottom-right blank space used for the word
    elif len(loaded_images) == 5:
        tile_w = (layout.card_width - (m * 2) - (gap * 2)) // 3
        tile_h = (layout.card_height - (m * 2) - gap) // 2

        positions = [
            (m, m),
            (m + tile_w + gap, m),
            (m + (tile_w * 2) + (gap * 2), m),
            (m, m + tile_h + gap),
            (m + tile_w + gap, m + tile_h + gap),
        ]
        image_size = (tile_w, tile_h)

        for img_source, pos in zip(loaded_images, positions):
            img = fit_image(img_source, (tile_w, tile_h))
            card.paste(img, pos)

        text_box = (
            m + (tile_w * 2) + (gap * 2),
            m + tile_h + gap,
            layout.card_width - m,
            layout.card_height - m,
        )

        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # 6 images: 3x2 grid, word in bottom text band
    elif len(loaded_images) == 6:
        text_band_h = 100

        tile_w = (layout.card_width - (m * 2) - (gap * 2)) // 3
        tile_h = (layout.card_height - text_band_h - (m * 2) - gap) // 2

        positions = [
            (m, m),
            (m + tile_w + gap, m),
            (m + (tile_w * 2) + (gap * 2), m),
            (m, m + tile_h + gap),
            (m + tile_w + gap, m + tile_h + gap),
            (m + (tile_w * 2) + (gap * 2), m + tile_h + gap),
        ]
        image_size = (tile_w, tile_h)

        for img_source, pos in zip(loaded_images, positions):
            img = fit_image(img_source, (tile_w, tile_h))
            card.paste(img, pos)

        text_box = (
            m,
            layout.card_height - text_band_h,
            layout.card_width - m,
            layout.card_height - m,
        )

        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # 7 images: 4x2 grid, bottom-right blank space used for the word
    elif len(loaded_images) == 7:
        tile_w = (layout.card_width - (m * 2) - (gap * 3)) // 4
        tile_h = (layout.card_height - (m * 2) - gap) // 2

        positions = [
            (m, m),
            (m + tile_w + gap, m),
            (m + (tile_w * 2) + (gap * 2), m),
            (m + (tile_w * 3) + (gap * 3), m),
            (m, m + tile_h + gap),
            (m + tile_w + gap, m + tile_h + gap),
            (m + (tile_w * 2) + (gap * 2), m + tile_h + gap),
        ]
        image_size = (tile_w, tile_h)

        for img_source, pos in zip(loaded_images, positions):
            img = fit_image(img_source, (tile_w, tile_h))
            card.paste(img, pos)

        text_box = (
            m + (tile_w * 3) + (gap * 3),
            m + tile_h + gap,
            layout.card_width - m,
            layout.card_height - m,
        )

        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # 8 images: 4x2 grid, word in bottom text band
    elif len(loaded_images) == 8:
        text_band_h = 90

        tile_w = (layout.card_width - (m * 2) - (gap * 3)) // 4
        tile_h = (layout.card_height - text_band_h - (m * 2) - gap) // 2

        positions = [
            (m, m),
            (m + tile_w + gap, m),
            (m + (tile_w * 2) + (gap * 2), m),
            (m + (tile_w * 3) + (gap * 3), m),
            (m, m + tile_h + gap),
            (m + tile_w + gap, m + tile_h + gap),
            (m + (tile_w * 2) + (gap * 2), m + tile_h + gap),
            (m + (tile_w * 3) + (gap * 3), m + tile_h + gap),
        ]
        image_size = (tile_w, tile_h)

        for img_source, pos in zip(loaded_images, positions):
            img = fit_image(img_source, (tile_w, tile_h))
            card.paste(img, pos)

        text_box = (
            m,
            layout.card_height - text_band_h,
            layout.card_width - m,
            layout.card_height - m,
        )

        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # Draw image numbers on top right of each image (only if there are multiple images)
    if len(positions) > 1:
        for idx, pos in enumerate(positions):
            draw_image_number(draw, idx + 1, pos, image_size)

    draw_border(draw)

    card.save(output_path)
    return output_path