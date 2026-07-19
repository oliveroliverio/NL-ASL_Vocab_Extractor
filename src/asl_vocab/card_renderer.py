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


def render_card(
    word: str,
    images: list[str | Path | Image.Image],
    output_path: str | Path,
) -> Path:
    layout = ASL_VOCAB_LAYOUT

    if len(images) not in {1, 2, 3, 4}:
        raise ValueError("render_card supports 1, 2, 3, or 4 images.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    card = Image.new(
        "RGB",
        (layout.card_width, layout.card_height),
        "white",
    )
    draw = ImageDraw.Draw(card)

    loaded_images = [load_image(img) for img in images]

    # 1 image: centered, old behavior
    if len(loaded_images) == 1:
        img = fit_image(
            loaded_images[0],
            (layout.image_width, layout.image_height),
        )

        card.paste(
            img,
            (
                (layout.card_width - layout.image_width) // 2,
                140,
            ),
        )

        draw.text(
            (layout.margin + 10, layout.card_height - 250),
            word.replace("_", " "),
            fill="black",
            font=get_font(),
        )

    # 2 images: keep your original offset layout
    elif len(loaded_images) == 2:
        img1 = fit_image(
            loaded_images[0],
            (layout.image_width, layout.image_height),
        )
        img2 = fit_image(
            loaded_images[1],
            (layout.image_width, layout.image_height),
        )

        card.paste(img1, (layout.margin, layout.margin))

        card.paste(
            img2,
            (
                layout.card_width - layout.image_width - layout.margin,
                layout.card_height - layout.image_height - layout.margin,
            ),
        )

        draw.text(
            (layout.margin + 10, layout.card_height - 250),
            word.replace("_", " "),
            fill="black",
            font=get_font(),
        )

    # 3 images: two top, one bottom-left, word in bottom-right blank space
    elif len(loaded_images) == 3:
        tile_w = (layout.card_width - (layout.margin * 3)) // 2
        tile_h = (layout.card_height - (layout.margin * 3)) // 2

        positions = [
            (layout.margin, layout.margin),
            (layout.margin * 2 + tile_w, layout.margin),
            (layout.margin, layout.margin * 2 + tile_h),
        ]

        for img_source, pos in zip(loaded_images, positions):
            img = fit_image(img_source, (tile_w, tile_h))
            card.paste(img, pos)

        text_box = (
            layout.margin * 2 + tile_w,
            layout.margin * 2 + tile_h,
            layout.margin * 2 + tile_w + tile_w,
            layout.margin * 2 + tile_h + tile_h,
        )

        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    # 4 images: 2x2 grid, word at bottom
    elif len(loaded_images) == 4:
        text_band_h = 130

        tile_w = (layout.card_width - (layout.margin * 3)) // 2
        tile_h = (
            layout.card_height
            - text_band_h
            - (layout.margin * 3)
        ) // 2

        positions = [
            (layout.margin, layout.margin),
            (layout.margin * 2 + tile_w, layout.margin),
            (layout.margin, layout.margin * 2 + tile_h),
            (layout.margin * 2 + tile_w, layout.margin * 2 + tile_h),
        ]

        for img_source, pos in zip(loaded_images, positions):
            img = fit_image(img_source, (tile_w, tile_h))
            card.paste(img, pos)

        text_box = (
            layout.margin,
            layout.card_height - text_band_h,
            layout.card_width - layout.margin,
            layout.card_height - layout.margin,
        )

        draw_centered_text(
            draw=draw,
            text=word,
            box=text_box,
            max_font_size=layout.font_size,
        )

    draw_border(draw)

    card.save(output_path)
    return output_path