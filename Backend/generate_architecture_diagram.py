"""
generate_architecture_diagram.py

Generates Figure 3.1 (Overall System Architecture) as a 2x2 GRID
(Presentation | Application  /  Service | Data) connected by arrows in
a Z-pattern, instead of one long vertical chain.

Each layer's file/table list is still pulled LIVE from your actual
project folders and database models — nothing is hand-typed.

USAGE
-----
pip install graphviz pillow
python generate_architecture_diagram.py

Writes: diagram_output/Figure_3_1_Architecture.png
"""

import sys
from pathlib import Path
import graphviz
from PIL import Image, ImageDraw, ImageFont

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "Frontend"
TMP_DIR = BACKEND_DIR / "_arch_tmp"

sys.path.insert(0, str(BACKEND_DIR))


def list_py_modules(folder: Path):
    if not folder.exists():
        return []
    return sorted(f.name for f in folder.glob("*.py") if f.name != "__init__.py")


def list_templates(folder: Path):
    if not folder.exists():
        return []
    return sorted(f.name for f in folder.glob("*.html"))


def get_table_names():
    try:
        from flask import Flask
        from extensions import db
        import models  # noqa
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        db.init_app(app)
        with app.app_context():
            return sorted(db.metadata.tables.keys())
    except Exception as exc:
        print(f"Warning: could not introspect models ({exc}); using placeholder list.")
        return ["users", "profiles", "assessments", "assessment_answers", "recommendations"]


def render_box(name, title, items, color):
    """Renders ONE layer as its own small, self-contained PNG."""
    dot = graphviz.Digraph(
        name,
        format="png",
        graph_attr={"bgcolor": "white", "margin": "0.1"},
        node_attr={"shape": "plaintext", "fontname": "Helvetica"},
    )
    rows = "".join(f'<TR><TD ALIGN="LEFT">{item}</TD></TR>' for item in items)
    # Graphviz treats a label as HTML-like only when the string itself begins
    # with '<' and ends with '>'. Keep the delimiters flush (no surrounding
    # whitespace) so the table is parsed as HTML instead of printed literally.
    title_html = title.replace("\n", "<BR/>")
    label = (
        '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5">'
        f'<TR><TD BGCOLOR="{color}"><FONT COLOR="white"><B>{title_html}</B></FONT></TD></TR>'
        f'{rows}'
        '</TABLE>>'
    )
    dot.node("box", label=label)
    TMP_DIR.mkdir(exist_ok=True)
    out_path = TMP_DIR / name
    dot.render(str(out_path), format="png", cleanup=True)
    return str(out_path) + ".png"


def build_diagram():
    routes = list_py_modules(BACKEND_DIR / "routes")
    services = list_py_modules(BACKEND_DIR / "services")
    templates = list_templates(FRONTEND_DIR / "templates")
    tables = get_table_names()

    top_left = render_box("presentation", "Presentation Layer\n(Flask + Jinja2 Templates)", templates, "#4c1d95")
    top_right = render_box("application", "Application Layer\n(Flask Route Blueprints)", routes, "#6d28d9")
    bottom_left = render_box("service", "Service Layer\n(Business Logic)", services, "#7c3aed")
    bottom_right = render_box("data", "Data Layer\n(PostgreSQL via SQLAlchemy ORM)", tables, "#8b5cf6")

    imgs = {
        "tl": Image.open(top_left).convert("RGBA"),
        "tr": Image.open(top_right).convert("RGBA"),
        "bl": Image.open(bottom_left).convert("RGBA"),
        "br": Image.open(bottom_right).convert("RGBA"),
    }

    col_w = max(imgs["tl"].width, imgs["bl"].width, imgs["tr"].width, imgs["br"].width)
    row_h_top = max(imgs["tl"].height, imgs["tr"].height)
    row_h_bot = max(imgs["bl"].height, imgs["br"].height)

    gap_x = 100
    gap_y = 90
    margin = 20

    canvas_w = col_w * 2 + gap_x + margin * 2
    canvas_h = row_h_top + row_h_bot + gap_y + margin * 2

    canvas = Image.new("RGBA", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 12)
    except Exception:
        font = ImageFont.load_default()

    tl_x, tl_y = margin, margin
    tr_x, tr_y = margin + col_w + gap_x, margin
    bl_x, bl_y = margin, margin + row_h_top + gap_y
    br_x, br_y = margin + col_w + gap_x, margin + row_h_top + gap_y

    canvas.paste(imgs["tl"], (tl_x, tl_y), imgs["tl"])
    canvas.paste(imgs["tr"], (tr_x, tr_y), imgs["tr"])
    canvas.paste(imgs["bl"], (bl_x, bl_y), imgs["bl"])
    canvas.paste(imgs["br"], (br_x, br_y), imgs["br"])

    def arrow(p1, p2, label=""):
        draw.line([p1, p2], fill="#4a4a4a", width=2)
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = max((dx**2 + dy**2) ** 0.5, 1)
        ux, uy = dx / length, dy / length
        left = (p2[0] - 8*ux + 6*uy, p2[1] - 8*uy - 6*ux)
        right = (p2[0] - 8*ux - 6*uy, p2[1] - 8*uy + 6*ux)
        draw.polygon([left, right, p2], fill="#4a4a4a")
        if label:
            draw.text(((p1[0]+p2[0])//2 - 30, (p1[1]+p2[1])//2 - 20), label, fill="#4a4a4a", font=font)

    arrow((tl_x + imgs["tl"].width + 5, tl_y + imgs["tl"].height // 2),
          (tr_x - 5, tr_y + imgs["tr"].height // 2), "HTTP requests")

    arrow((tr_x + imgs["tr"].width // 2, tr_y + imgs["tr"].height + 5),
          (br_x + imgs["br"].width // 2, br_y - 5), "function calls")

    arrow((br_x - 5, br_y + imgs["br"].height // 2),
          (bl_x + imgs["bl"].width + 5, bl_y + imgs["bl"].height // 2), "ORM queries")

    out_dir = BACKEND_DIR / "diagram_output"
    out_dir.mkdir(exist_ok=True)
    final_path = out_dir / "Figure_3_1_Architecture.png"
    canvas.convert("RGB").save(final_path)

    for p in TMP_DIR.glob("*.png"):
        p.unlink()
    TMP_DIR.rmdir()

    print("Architecture diagram generated successfully:")
    print(f"  {final_path}")
    print(f"Detected {len(templates)} templates, {len(routes)} route files, "
          f"{len(services)} service files, {len(tables)} database tables.")


if __name__ == "__main__":
    build_diagram()