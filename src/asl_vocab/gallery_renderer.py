from pathlib import Path
import re
from collections import defaultdict


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def parse_card_filename(path: Path):
    """
    Handles:
      6-2_body_260610_175424_card.png
      6-2_cranky_grouchy_260610_144357_card.png
    """

    stem = path.stem

    match = re.match(
        r"^(?P<unit>\d+-\d+)_(?P<name>.+)_\d{6}_\d{6}_card$",
        stem,
    )

    if not match:
        return None

    unit = match.group("unit")
    name = match.group("name").replace("_", " ").title()

    return unit, name


def generate_gallery_markdown(
    image_dir: Path,
    output_markdown_path: Path,
    title: str = "ASL Vocabulary Gallery",
    unit: str | None = None,
) -> Path:
    image_dir = Path(image_dir)
    output_markdown_path = Path(output_markdown_path)

    images = []

    if not image_dir.exists():
        image_dir.mkdir(parents=True, exist_ok=True)

    for path in image_dir.iterdir():
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        parsed = parse_card_filename(path)
        if parsed is None:
            continue

        image_unit, display_name = parsed

        if unit is not None and image_unit != unit:
            continue

        images.append((path, image_unit, display_name))

    images.sort(key=lambda item: item[0].name.lower())

    lines = [
        f"# {title}",
        "",
        f"Total cards: {len(images)}",
        "",
    ]

    for image_path, image_unit, display_name in images:
        relative_path = image_path.relative_to(output_markdown_path.parent)

        lines.extend(
            [
                f"## {display_name}",
                "",
                f"![{display_name}]({relative_path.as_posix()})",
                "",
                "---",
                "",
            ]
        )

    output_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_markdown_path.write_text("\n".join(lines), encoding="utf-8")

    return output_markdown_path


def generate_unit_galleries(
    image_dir: Path,
    output_dir: Path,
) -> list[Path]:
    image_dir = Path(image_dir)
    output_dir = Path(output_dir)

    units = set()

    if not image_dir.exists():
        return []

    for path in image_dir.iterdir():
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        parsed = parse_card_filename(path)
        if parsed is None:
            continue

        unit, _ = parsed
        units.add(unit)

    created = []

    for unit in sorted(units):
        gallery_path = output_dir / f"{unit}_GALLERY.md"

        created.append(
            generate_gallery_markdown(
                image_dir=image_dir,
                output_markdown_path=gallery_path,
                title=f"ASL Vocabulary Gallery — Unit {unit.replace('-', '.')}",
                unit=unit,
            )
        )

    return created