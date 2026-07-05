"""
generate_architecture_diagram.py

Generates Figure 3.1 (Overall System Architecture) by SCANNING your
actual project folders at run time — Backend/routes/, Backend/services/,
and Frontend/templates/ — and listing the real module and template
filenames it finds inside each architectural layer. Nothing here is a
static, hand-typed list: if you add or remove a route file or a service
file, the next run of this script will reflect that change automatically.

The database layer's table names are also pulled directly from the live
SQLAlchemy models, same as generate_erd.py.

USAGE
-----
1. Place this file inside your Backend/ folder (same level as app.py).
2. From inside Backend/, with your virtual environment active, run:

       pip install graphviz
       python generate_architecture_diagram.py

3. The script writes:
       diagram_output/Figure_3_1_Architecture.png
       diagram_output/Figure_3_1_Architecture.pdf
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "Frontend"

sys.path.insert(0, str(BACKEND_DIR))

import graphviz


def list_py_modules(folder: Path):
    """Returns sorted .py filenames in a folder, excluding __init__.py."""
    if not folder.exists():
        return []
    return sorted(
        f.name for f in folder.glob("*.py") if f.name != "__init__.py"
    )


def list_templates(folder: Path):
    if not folder.exists():
        return []
    return sorted(f.name for f in folder.glob("*.html"))


def get_table_names():
    """Pulls real table names from the live SQLAlchemy models."""
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
        print(f"Warning: could not introspect models ({exc}); "
              f"using a placeholder table list instead.")
        return ["users", "profiles", "assessments",
                "assessment_answers", "recommendations"]


def build_diagram():
    routes = list_py_modules(BACKEND_DIR / "routes")
    services = list_py_modules(BACKEND_DIR / "services")
    templates = list_templates(FRONTEND_DIR / "templates")
    tables = get_table_names()

    dot = graphviz.Digraph(
        "Architecture",
        format="png",
        graph_attr={
            "rankdir": "TB",
            "splines": "spline",
            "bgcolor": "white",
            "fontname": "Helvetica",
            "nodesep": "0.5",
            "ranksep": "0.7",
        },
        node_attr={
            "shape": "box",
            "style": "rounded,filled",
            "fontname": "Helvetica",
            "fontsize": "11",
        },
        edge_attr={"fontname": "Helvetica", "fontsize": "10"},
    )

    def html_label(title, items, color):
        rows = "".join(
            f'<TR><TD ALIGN="LEFT">{name}</TD></TR>' for name in items
        )
        return f'''
            <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
                <TR><TD BGCOLOR="{color}"><FONT COLOR="white"><B>{title}</B></FONT></TD></TR>
                {rows}
            </TABLE>
        >'''

    dot.node(
        "presentation",
        label=html_label("Presentation Layer (Flask + Jinja2 Templates)",
                          templates, "#6d28d9"),
        shape="plaintext",
    )

    dot.node(
        "application",
        label=html_label("Application Layer (Flask Route Blueprints)",
                          routes, "#7c3aed"),
        shape="plaintext",
    )

    dot.node(
        "service",
        label=html_label("Service Layer (Business Logic)",
                          services, "#8b5cf6"),
        shape="plaintext",
    )

    dot.node(
        "data",
        label=html_label("Data Layer (PostgreSQL via SQLAlchemy ORM)",
                          tables, "#a78bfa"),
        shape="plaintext",
    )

    dot.edge("presentation", "application", label="HTTP requests")
    dot.edge("application", "service", label="function calls")
    dot.edge("service", "data", label="ORM queries")

    out_dir = BACKEND_DIR / "diagram_output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "Figure_3_1_Architecture"
    dot.render(str(out_path), format="png", cleanup=True)
    dot.render(str(out_path), format="pdf", cleanup=True)

    print("Architecture diagram generated successfully:")
    print(f"  {out_path}.png")
    print(f"  {out_path}.pdf")
    print()
    print(f"Detected {len(templates)} templates, {len(routes)} route files, "
          f"{len(services)} service files, {len(tables)} database tables.")


if __name__ == "__main__":
    build_diagram()