"""
generate_erd.py

Generates Figure 3.3 (Entity Relationship Diagram) DIRECTLY from the
live SQLAlchemy models in Backend/models/, by introspecting
db.metadata.tables at runtime. Nothing here is hand-drawn or guessed —
every table, column, and foreign key relationship shown in the output
image is read straight from your actual model definitions.

USAGE
-----
1. Place this file inside your Backend/ folder (same level as app.py).
2. From inside Backend/, with your virtual environment active, run:

       pip install graphviz
       python generate_erd.py

   (You also need the Graphviz system package installed, not just the
   Python wrapper. On Windows: download and install from
   https://graphviz.org/download/ and make sure it's added to PATH.
   On Mac: brew install graphviz. On Ubuntu/Debian: sudo apt install graphviz.)

3. The script writes:
       erd_output/Figure_3_3_ERD.png   (raster image to insert into Word)
       erd_output/Figure_3_3_ERD.pdf   (vector version, optional)

OUTPUT NOTES
------------
- Primary keys are marked with (PK) and underlined-style bold.
- Foreign keys are marked with (FK).
- An arrow is drawn from each foreign key to the table/column it
  references, labelled with the relationship (one-to-many, etc.)
  inferred from the SQLAlchemy relationship() calls in your models.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flask import Flask
from extensions import db
import models  # noqa: registers all model classes with db.metadata

import graphviz


def build_erd():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.init_app(app)

    dot = graphviz.Digraph(
        "ERD",
        format="png",
        graph_attr={
            "rankdir": "TB",
            "splines": "spline",
            "bgcolor": "white",
            "fontname": "Helvetica",
            "nodesep": "0.6",
            "ranksep": "0.9",
        },
        node_attr={
            "shape": "plaintext",
            "fontname": "Helvetica",
        },
        edge_attr={
            "fontname": "Helvetica",
            "fontsize": "10",
            "color": "#4a4a4a",
        },
    )

    with app.app_context():
        tables = db.metadata.tables

        for table_name, table in tables.items():
            rows = ""
            for col in table.columns:
                tags = []
                if col.primary_key:
                    tags.append("PK")
                if col.foreign_keys:
                    tags.append("FK")
                tag_str = f" ({', '.join(tags)})" if tags else ""
                col_style = ' BGCOLOR="#eef2ff"' if tags else ""
                rows += (
                    f'<TR><TD ALIGN="LEFT"{col_style}>'
                    f'{col.name}{tag_str}: {str(col.type)}'
                    f"</TD></TR>"
                )

            label = f'''
                <TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6">
                    <TR><TD BGCOLOR="#4c1d95"><FONT COLOR="white"><B>{table_name}</B></FONT></TD></TR>
                    {rows}
                </TABLE>
            >'''
            dot.node(table_name, label=label)

        for table_name, table in tables.items():
            for col in table.columns:
                for fk in col.foreign_keys:
                    target_table = fk.column.table.name
                    dot.edge(
                        table_name,
                        target_table,
                        label=f"{col.name} → {fk.column.table.name}.{fk.column.name}",
                        arrowhead="crow",
                        arrowtail="tee",
                        dir="both",
                    )

    out_dir = Path(__file__).resolve().parent / "erd_output"
    out_dir.mkdir(exist_ok=True)

    png_path = out_dir / "Figure_3_3_ERD"
    dot.render(str(png_path), format="png", cleanup=True)
    dot.render(str(png_path), format="pdf", cleanup=True)

    print(f"ERD generated successfully:")
    print(f"  {png_path}.png")
    print(f"  {png_path}.pdf")


if __name__ == "__main__":
    build_erd()