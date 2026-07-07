"""
generate_code_images.py

Renders the "relevant lines" code screenshots referenced in Chapter 3
(Section 3.7) as clean, syntax-highlighted PNG images, so the figures are
crisp and stylistically consistent instead of ad-hoc editor screenshots.

Each image is produced directly from the live source files, so it can never
drift out of sync with the actual code.

USAGE
-----
pip install pygments pillow
python generate_code_images.py

Writes into: code_images/
"""

from pathlib import Path

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter

BACKEND_DIR = Path(__file__).resolve().parent
OUT_DIR = BACKEND_DIR / "code_images"

# (output name, source file, first line, last line or None for whole file)
TARGETS = [
    ("Code_1_dataset_loader.png",       "services/dataset_loader.py",       1, None),
    ("Code_2_recommendation_service.png", "services/recommendation_service.py", 1, None),
    ("Code_3_skill_gap_service.png",    "services/skill_gap_service.py",    1, None),
    ("Code_4_app.png",                  "app.py",                           1, 52),
]

# Try a few monospace fonts that are commonly present on Windows first.
FONT_CANDIDATES = ["Consolas", "Cascadia Mono", "Courier New", "DejaVu Sans Mono"]


def make_formatter(font):
    # NOTE: ImageFormatter is stateful and must NOT be reused across renders,
    # or Pygments draws each file on top of the previous one. Always build a
    # fresh instance per image.
    return ImageFormatter(
        style="friendly",
        font_name=font,
        font_size=26,
        line_numbers=True,
        line_number_bg="#f3f0fb",
        line_number_fg="#8b5cf6",
        line_number_separator=False,
        image_pad=26,
        line_pad=6,
    )


def pick_font():
    last_err = None
    for font in FONT_CANDIDATES:
        try:
            highlight("x = 1\n", PythonLexer(), make_formatter(font))
            print(f"Using font: {font}")
            return font
        except Exception as exc:  # font not found -> try the next candidate
            last_err = exc
    raise RuntimeError(f"No usable monospace font found. Last error: {last_err}")


def extract(src_path: Path, start: int, end):
    lines = src_path.read_text(encoding="utf-8").splitlines()
    end = end or len(lines)
    return "\n".join(lines[start - 1:end]) + "\n"


def main():
    OUT_DIR.mkdir(exist_ok=True)
    font = pick_font()

    for out_name, rel_src, start, end in TARGETS:
        src_path = BACKEND_DIR / rel_src
        code = extract(src_path, start, end)
        png = highlight(code, PythonLexer(), make_formatter(font))
        out_path = OUT_DIR / out_name
        out_path.write_bytes(png)
        span = f"lines {start}-{end}" if end else "whole file"
        print(f"  {out_name}  <-  {rel_src} ({span})")

    print(f"\nDone. {len(TARGETS)} code images written to {OUT_DIR}")


if __name__ == "__main__":
    main()
