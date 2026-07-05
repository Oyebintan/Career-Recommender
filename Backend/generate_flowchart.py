"""
generate_flowchart.py

Generates Figure 3.2 (Career Recommendation and Skill Gap Flowchart).

Unlike generate_erd.py and generate_architecture_diagram.py, this
flowchart cannot be introspected automatically the same way, because it
depicts a sequence of RUNTIME LOGIC (the order operations happen in),
not static structure like tables or files. However, every box and label
below is named after the exact method it represents, taken directly
from your live services/recommendation_service.py and
services/skill_gap_service.py.

If you rename any of these methods, update the corresponding label
string in this script so the diagram stays in sync with your code.

USAGE
-----
1. Place this file inside your Backend/ folder (same level as app.py).
2. From inside Backend/, with your virtual environment active, run:

       pip install graphviz
       python generate_flowchart.py

3. The script writes:
       diagram_output/Figure_3_2_Flowchart.png
       diagram_output/Figure_3_2_Flowchart.pdf
"""

from pathlib import Path
import graphviz

BACKEND_DIR = Path(__file__).resolve().parent


def build_flowchart():
    dot = graphviz.Digraph(
        "Flowchart",
        format="png",
        graph_attr={
            "rankdir": "TB",
            "splines": "spline",
            "bgcolor": "white",
            "fontname": "Helvetica",
            "nodesep": "0.4",
            "ranksep": "0.5",
        },
        node_attr={"fontname": "Helvetica", "fontsize": "11"},
        edge_attr={"fontname": "Helvetica", "fontsize": "10"},
    )

    def start_end(name, label):
        dot.node(name, label, shape="ellipse", style="filled",
                  fillcolor="#4c1d95", fontcolor="white")

    def process(name, label):
        dot.node(name, label, shape="box", style="filled,rounded",
                  fillcolor="#ede9fe")

    def decision(name, label):
        dot.node(name, label, shape="diamond", style="filled",
                  fillcolor="#ddd6fe")

    def io(name, label):
        dot.node(name, label, shape="parallelogram", style="filled",
                  fillcolor="#f5f3ff")

    start_end("start", "User submits\nassessment answers")
    io("answers", "answers = {question_id: likert_value}")
    process("calc", "RecommendationService.calculate_scores()\n"
                    "raw_score += answer_value × weight\nfor every mapped career")
    process("norm", "RecommendationService.normalize_scores()\n"
                    "score% = (raw_score ÷ career's own max) × 100")
    process("rank", "RecommendationService.get_top_careers()\n"
                    "sort all careers by score%, descending")
    io("top3", "Top 3 careers + match %\nsaved to recommendations table")

    dot.edge("start", "answers")
    dot.edge("answers", "calc")
    dot.edge("calc", "norm")
    dot.edge("norm", "rank")
    dot.edge("rank", "top3")

    decision("choose", "User selects one\nrecommended career?")
    process("reqskills", "SkillGapService.get_required_skills()\n"
                         "fetch required skills for chosen career")
    io("userskills", "User enters their\nexisting skills")
    process("gap", "SkillGapService.analyze_skill_gap()\n"
                   "compare required vs. existing skills")
    process("readiness", "readiness% = (possessed ÷ required) × 100")
    start_end("end", "Display possessed skills,\nmissing skills, and readiness%")

    dot.edge("top3", "choose")
    dot.edge("choose", "reqskills", label="Yes")
    dot.edge("reqskills", "userskills")
    dot.edge("userskills", "gap")
    dot.edge("gap", "readiness")
    dot.edge("readiness", "end")
    dot.edge("choose", "end", label="No — view results only", style="dashed")

    out_dir = BACKEND_DIR / "diagram_output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "Figure_3_2_Flowchart"
    dot.render(str(out_path), format="png", cleanup=True)
    dot.render(str(out_path), format="pdf", cleanup=True)

    print("Flowchart generated successfully:")
    print(f"  {out_path}.png")
    print(f"  {out_path}.pdf")


if __name__ == "__main__":
    build_flowchart()