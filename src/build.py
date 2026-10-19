"""Build index.html: embed every exams/<bộ>/*.json into src/template.html.

Chạy: python src/build.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Thứ tự hiển thị các bộ đề: (thư mục, tên nhóm, ghi chú nguồn)
GROUPS = [
    ("sat-that", "Đề sát thật", "Đề tự soạn theo đúng cấu trúc 4 phần và thang điểm của đề ĐGNL."),
    ("luyen-nhanh", "Luyện nhanh Toán và Code tay", "Bài luyện tự soạn cho hai phần dễ mất điểm nhất."),
    ("hieubui", "Bộ đề anh Hiếu (hieubui2409)", "6 đề tổng hợp và 12 chuyên đề, dùng lại với sự cho phép của tác giả."),
    ("ai-test", "Bộ AI-TEST (cơ bản)", "10 đề mức nhận biết · giấy phép MIT © 2026 Henry Don."),
]
ORDER = {g[0]: i for i, g in enumerate(GROUPS)}

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
    right = next((o["text"] for o in q.get("options", []) if o["key"] == q["answer"]), "")
    text = " ".join([q["prompt"], right, " ".join(q.get("tags", []))])
    return next((s for pat, s in RULES[q["module"]] if re.search(pat, text)), DEFAULT[q["module"]])


def load_exam(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    qs = []
    for i, q in enumerate(d["questions"], 1):
        where = f"{path.name} câu {i}"
        assert q["module"] in "ABCD" and q["type"] in ("mcq", "numeric", "output", "code", "essay"), where
        assert q.get("prompt") and float(q.get("points", 1)) > 0, where
        out = {k: q[k] for k in ("id", "module", "type", "points", "prompt", "explanation", "modelAnswer", "level", "long", "mistakes") if k in q}
        if q["type"] == "numeric":
            assert isinstance(q["answer"], (int, float)), f"{where}: numeric cần answer là số"
            out["answer"] = q["answer"]
            for k in ("tol", "unit"):
                if k in q:
                    out[k] = q[k]
        elif q["type"] == "output":
            out["answer"] = str(q["answer"])
            out["accept"] = q.get("accept") or [out["answer"]]
            out["ignoreCase"] = bool(q.get("ignoreCase"))
        elif q["type"] == "mcq":
            keys = [o["key"] for o in q["options"]]
            assert q["answer"] in keys, f"{where}: answer không nằm trong options"
            out["options"], out["answer"] = q["options"], q["answer"]
            if q.get("distractors"):
                out["distractors"] = q["distractors"]
        else:
            out["rubric"] = q.get("rubric", [])
        out["section"] = q.get("section") or guess_section(q)
        qs.append(out)
    return {
        "id": f"{path.parent.name}/{path.stem}",
        "title": d.get("title", path.stem),
        "description": d.get("description", ""),
        "durationMinutes": d.get("durationMinutes", 90),
        "group": dict((g[0], g[1]) for g in GROUPS).get(path.parent.name, path.parent.name),
        "source": dict((g[0], g[2]) for g in GROUPS).get(path.parent.name, d.get("source", "")),
        **({"parts": d["parts"]} if d.get("parts") else {}),
        "questions": qs,
    }


def main():
    paths = sorted((ROOT / "exams").glob("*/*.json"), key=lambda p: (ORDER.get(p.parent.name, 99), p.name))
    exams = [load_exam(p) for p in paths]
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
