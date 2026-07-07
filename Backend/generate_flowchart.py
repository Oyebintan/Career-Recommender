"""
generate_flowchart.py

Generates Figure 3.2 as TWO VERTICAL COLUMNS placed side by side
(left column, then right column), connected by a horizontal arrow —
instead of one long straight chain.

USAGE
-----
pip install graphviz pillow
python generate_flowchart.py

Writes: diagram_output/Figure_3_2_Flowchart.png
"""

from pathlib import Path
import graphviz
from PIL import Image, ImageDraw, ImageFont

BACKEND_DIR = Path(__file__).resolve().parent
TMP_DIR = BACKEND_DIR / "_flowchart_col_tmp"

PURPLE = "#4c1d95"
LILAC = "#ede9fe"
PALE = "#f5f3ff"
DIAMOND = "#ddd6fe"


def render_column(name, nodes, edges):
    dot = graphviz.Digraph(
        name,
        format="png",
        graph_attr={
            "rankdir": "TB",
            "splines": "spline",
            "bgcolor": "white",
            "fontname": "Helvetica",
            "nodesep": "0.3",
            "ranksep": "0.35",
            "margin": "0.15",
        },
        node_attr={"fontname": "Helvetica", "fontsize": "11"},
        edge_attr={"fontname": "Helvetica", "fontsize": "9", "color": "#4a4a4a"},
    )
    for node_id, label, shape, fillcolor, fontcolor in nodes:
        dot.node(
            node_id, label, shape=shape,
            style="filled,rounded" if shape == "box" else "filled",
            fillcolor=fillcolor, fontcolor=fontcolor,
        )
    for src, dst, label, style in edges:
        kwargs = {}
        if label:
            kwargs["label"] = label
        if style:
            kwargs["style"] = style
        dot.edge(src, dst, **kwargs)

    TMP_DIR.mkdir(exist_ok=True)
    out_path = TMP_DIR / name
    dot.render(str(out_path), format="png", cleanup=True)
    return str(out_path) + ".png"


def stitch_columns_side_by_side(col_image_paths, output_path, connector_label=""):
    images = [Image.open(p).convert("RGBA") for p in col_image_paths]

    gap = 90
    max_height = max(img.height for img in images)
    total_width = sum(img.width for img in images) + gap * (len(images) - 1) + 20

    canvas = Image.new("RGBA", (total_width, max_height + 20), "white")
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 12)
    except Exception:
        font = ImageFont.load_default()

    x_cursor = 10
    for i, img in enumerate(images):
        y = 10 + (max_height - img.height) // 2
        canvas.paste(img, (x_cursor, y), img)
        x_cursor += img.width

        if i < len(images) - 1:
            arrow_y = max_height // 2 + 10
            left_x = x_cursor + 10
            right_x = x_cursor + gap - 12
            draw.line([(left_x, arrow_y), (right_x, arrow_y)], fill="#4a4a4a", width=2)
            draw.polygon(
                [
                    (right_x - 8, arrow_y - 6),
                    (right_x - 8, arrow_y + 6),
                    (right_x + 2, arrow_y),
                ],
                fill="#4a4a4a",
            )
            if connector_label:
                draw.text((left_x - 5, arrow_y - 28), connector_label,
                          fill="#4a4a4a", font=font)
            x_cursor += gap

    canvas.convert("RGB").save(output_path)


def build_flowchart():
    left_path = render_column(
        "left",
        nodes=[
            ("start", "User submits\nassessment answers", "ellipse", PURPLE, "white"),
            ("answers", "answers = {question_id:\nlikert_value}", "parallelogram", PALE, "black"),
            ("calc", "calculate_scores()\nraw_score += answer × weight", "box", LILAC, "black"),
            ("norm", "normalize_scores()\nscore% = raw ÷ top career score × 100", "box", LILAC, "black"),
            ("rank", "get_top_careers()\nsort by score%, descending", "box", LILAC, "black"),
            ("top3", "Top 3 careers + match %\nsaved to recommendations table", "parallelogram", PALE, "black"),
        ],
        edges=[
            ("start", "answers", None, None),
            ("answers", "calc", None, None),
            ("calc", "norm", None, None),
            ("norm", "rank", None, None),
            ("rank", "top3", None, None),
        ],
    )

    right_path = render_column(
        "right",
        nodes=[
            ("choose", "User selects a\nrecommended career?", "diamond", DIAMOND, "black"),
            ("reqskills", "get_required_skills()\nfetch required skills", "box", LILAC, "black"),
            ("userskills", "User enters their\nexisting skills", "parallelogram", PALE, "black"),
            ("gap", "analyze_skill_gap()\ncompare required vs. existing", "box", LILAC, "black"),
            ("readiness", "readiness% = possessed ÷\nrequired × 100", "box", LILAC, "black"),
            ("end", "Display possessed, missing\nskills and readiness%", "ellipse", PURPLE, "white"),
        ],
        edges=[
            ("choose", "reqskills", "Yes", None),
            ("reqskills", "userskills", None, None),
            ("userskills", "gap", None, None),
            ("gap", "readiness", None, None),
            ("readiness", "end", None, None),
        ],
    )

    out_dir = BACKEND_DIR / "diagram_output"
    out_dir.mkdir(exist_ok=True)
    final_path = out_dir / "Figure_3_2_Flowchart.png"

    stitch_columns_side_by_side(
        [left_path, right_path], str(final_path),
        connector_label="continues"
    )

    for p in TMP_DIR.glob("*.png"):
        p.unlink()
    TMP_DIR.rmdir()

    print("Flowchart generated successfully:")
    print(f"  {final_path}")


if __name__ == "__main__":
    build_flowchart()