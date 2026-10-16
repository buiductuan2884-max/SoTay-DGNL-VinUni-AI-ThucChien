"""Build index.html: embed every exams/<bộ>/*.json into src/template.html.

Chạy: python src/build.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {"ai-test": "AI-TEST · MIT © 2026 Henry Don"}

# Câu nào không ghi "section" thì đoán mục sổ tay từ nội dung câu + đáp án đúng.
RULES = {
    "A": [(r"probability|conditional|[Xx]ác suất|P\(", "a-xs"), (r"statistics|[Mm]edian|trung vị", "a-tk"),
          (r"calculus|[Đđ]ạo hàm", "a-gt"), (r"vector|matrix|[Tt]ích vô hướng|ma trận", "a-dstt")],
    "B": [(r"Big-O|O\(|\bset\b", "b-np"), (r"NumPy|np\.", "b-np"), (r"Pandas|pd\.|df\b|df\[", "b-pd")],
    "C": [(r"[Pp]rompt injection|[Gg]uardrail", "d-sec"), (r"RAG|[Rr]etrieve|[Rr]erank|[Ee]mbedding", "c-rag"),
          (r"LLM|[Tt]emperature|token|[Cc]ontext window|[Hh]allucination|[Ff]ew-shot|[Ff]ine-tuning|\d+B\b", "c-llm"),
          (r"drift|[Mm]onitoring|production", "c-ops"), (r"A/B", "a-tk"),
          (r"chặn nhầm|[Pp]recision|[Rr]ecall|spam|độ tin cậy cao", "c-metric"),
          (r"[Bb]aseline|confidence|luồng an toàn", "c-pm")],
    "D": [(r"[Mm]ệnh đề|[Pp]hủ định|[Đđ]ây là|lỗi|[Kk]ết luận", "d-logic")],
}
DEFAULT = {"A": "a-tile", "B": "b-py", "C": "c-ml", "D": "d-eth"}


def guess_section(q):
    if q["type"] in ("code", "essay"):
        return "tu-luan"
    right = next((o["text"] for o in q["options"] if o["key"] == q["answer"]), "")
    text = " ".join([q["prompt"], right, " ".join(q.get("tags", []))])
    return next((s for pat, s in RULES[q["module"]] if re.search(pat, text)), DEFAULT[q["module"]])


def load_exam(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    qs = []
    for i, q in enumerate(d["questions"], 1):
        where = f"{path.name} câu {i}"
        assert q["module"] in "ABCD" and q["type"] in ("mcq", "code", "essay"), where
        assert q.get("prompt") and float(q.get("points", 1)) > 0, where
        out = {k: q[k] for k in ("module", "type", "points", "prompt", "explanation", "modelAnswer") if k in q}
        if q["type"] == "mcq":
            keys = [o["key"] for o in q["options"]]
            assert q["answer"] in keys, f"{where}: answer không nằm trong options"
            out["options"], out["answer"] = q["options"], q["answer"]
        else:
            out["rubric"] = [r if isinstance(r, str) else r.get("criterion", "") for r in q.get("rubric", [])]
        out["section"] = q.get("section") or guess_section(q)
        qs.append(out)
    return {
        "id": f"{path.parent.name}/{path.stem}",
        "title": d.get("title", path.stem),
        "description": d.get("description", ""),
        "durationMinutes": d.get("durationMinutes", 90),
        "source": d.get("source") or SOURCES.get(path.parent.name, path.parent.name),
        "questions": qs,
    }


def main():
    exams = [load_exam(p) for p in sorted((ROOT / "exams").glob("*/*.json"))]
    tpl = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
    known = set(re.findall(r'<(?:h3|section) id="([^"]+)"', tpl))
    bad = {q["section"] for e in exams for q in e["questions"]} - known
    assert not bad, f"section không có trong sổ tay: {bad}"
    data = json.dumps(exams, ensure_ascii=False).replace("</", "<\\/")  # giữ "</script>" trong dữ liệu không đóng thẻ
    assert tpl.count("/*EXAMS*/") == 1
    head = ('<!doctype html>\n<html lang="vi">\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n')
    (ROOT / "index.html").write_text(head + tpl.replace("/*EXAMS*/", data), encoding="utf-8")
    n = sum(len(e["questions"]) for e in exams)
    print(f"index.html: {len(exams)} đề, {n} câu")
    if "-v" in sys.argv:
        from collections import Counter
        print(Counter(q["section"] for e in exams for q in e["questions"]))


if __name__ == "__main__":
    main()
