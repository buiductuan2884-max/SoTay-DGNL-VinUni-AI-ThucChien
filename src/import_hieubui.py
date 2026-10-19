"""Chép 18 đề của hieubui2409/ai20k-exam-prep (được tác giả cho phép dùng lại) sang exams/hieubui/*.json.

Chạy: python src/import_hieubui.py            (tải trang gốc)
      python src/import_hieubui.py index.html (dùng file đã tải)
"""
import json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://hieubui2409.github.io/ai20k-exam-prep/"
LEVEL_PARTS = {"A": "Nhận biết", "B": "Thông hiểu", "C": "Vận dụng", "D": "Vận dụng cao"}

# Chuyên đề → mục sổ tay mặc định, kèm từ khoá để chỉnh cho từng câu
TOPIC = {"T01": "a-dstt", "T02": "a-gt", "T03": "a-xs", "T04": "a-tk", "T05": "b-py", "T06": "b-pd",
         "T07": "b-np", "T08": "b-sql", "T09": "c-ml", "T10": "c-rag", "T11": "c-ops", "T12": "d-logic"}
REFINE = {
    "T09": [(r"[Pp]recision|[Rr]ecall|F1|AUC|nhầm lẫn|ngưỡng|MAE|RMSE", "c-metric")],
    "T10": [(r"[Aa]gent|tool|ReAct|injection", "c-agent"), (r"attention|token|[Tt]emperature|KV|BPE|top-p", "c-llm")],
    "T12": [(r"OWASP|LLM\d\d|injection", "d-sec"),
            (r"dữ liệu cá nhân|công bằng|AI Act|đồng ý|ẩn danh|parity|tác động|nhạy cảm|minh bạch|GDPR|model card|thiên lệch tự động", "d-eth")],
}
BY_MODULE = {
    "A": [(r"ma trận|vector|trị riêng|PCA|SVD|cosine|định thức|embedding", "a-dstt"),
          (r"đạo hàm|gradient|learning rate|softmax|loss|Hessian|momentum|Adam|logits", "a-gt"),
          (r"A/B|p-value|khoảng tin cậy|trung vị|p95|p50|cỡ mẫu|kiểm định|SLO", "a-tk"),
          (r"xác suất|Bayes|Poisson|kỳ vọng|phương sai|dương tính|gắn cờ", "a-xs")],
    "B": [(r"SQL|SELECT", "b-sql"), (r"pandas|pd\.|\bdf\b|DataFrame", "b-pd"),
          (r"np\.|NumPy|O\(|độ phức tạp|\bset\b|heap", "b-np"),
          (r"review|\bCL\b|kiểm thử|test|idempot|cache|retry|replica|hàng đợi|rate limit|backoff", "b-se")],
    "C": [(r"[Aa]gent|tool|ReAct", "c-agent"),
          (r"RAG|chunk|truy xuất|truy hồi|BM25|rerank|[Ff]aithfulness|HNSW|NDCG|DCG|[Rr]ecall@", "c-rag"),
          (r"drift|canary|shadow|rollback|PSI|DVC|Docker|GPU|judge|golden|eval gate", "c-ops"),
          (r"LLM|token|TTFT|[Tt]emperature|lượng tử|quantiz|cache|max_tokens|prompt", "c-llm"),
          (r"[Pp]recision|[Rr]ecall|F1|AUC|ngưỡng|nhầm lẫn|MAE|RMSE", "c-metric"),
          (r"RICE|ROI|A/B|gợi ý|cold start|copilot|hoàn vốn", "c-pm")],
    "D": [(r"OWASP|LLM\d\d|injection|chữ trắng|ẩn \(|dòng ẩn", "d-sec"),
          (r"Nếu|phủ định|mệnh đề|ngụy biện|lời khai|tương đương|[Kk]ết luận nào|hợp lệ", "d-logic")],
}
DEFAULT = {"A": "a-tile", "B": "b-py", "C": "c-ml", "D": "d-eth"}


def pick(rules, text, default):
    return next((s for pat, s in rules if re.search(pat, text)), default)


def section(exam_id, q):
    if q["type"] in ("code", "essay"):
        return "tu-luan"
    text = q["prompt"] + " " + " ".join(q.get("tags") or [])
    if exam_id in TOPIC:
        return pick(REFINE.get(exam_id, []), text, TOPIC[exam_id])
    return pick(BY_MODULE[q["module"]], text, DEFAULT[q["module"]])


def convert(e):
    qs = []
    for q in e["questions"]:
        out = {"id": q["id"], "module": q["module"], "type": q["type"], "points": q["points"],
               "level": q.get("level"), "prompt": q["prompt"], "explanation": q.get("explanation") or "",
               "section": section(e["id"], q)}
        for k in ("long", "distractors", "mistakes"):
            if q.get(k):
                out[k] = q[k]
        if q["type"] == "mcq":
            out["options"], out["answer"] = q["options"], q["answer"]
        elif q["type"] == "numeric":
            out["answer"], out["tol"] = q["value"], q.get("tol") or 0
            if q.get("unit"):
                out["unit"] = q["unit"]
        elif q["type"] == "output":
            out["answer"] = q["value"]
            out["accept"] = [q["value"]] + [a for a in (q.get("accept") or []) if a != q["value"]]
            out["ignoreCase"] = bool(q.get("ignore_case"))
        else:
            out["modelAnswer"] = q.get("model_answer") or ""
            out["rubric"] = q.get("rubric") or []
        qs.append(out)
    topic = e.get("kind") == "topic"
    desc = e.get("desc") or {}
    return {
        "title": f"{e['code']} · {e['title']}",
        "description": (" · ".join(desc.get("bullets", [])) if isinstance(desc, dict) else str(desc))[:400],
        "durationMinutes": e.get("duration_minutes", 90),
        "source": "Bộ đề hieubui2409/ai20k-exam-prep · dùng lại với sự cho phép của tác giả",
        "parts": LEVEL_PARTS if topic else None,
        "questions": qs,
    }


def main():
    html = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else \
        urllib.request.urlopen(URL, timeout=60).read().decode("utf-8")
    i = html.index("const EXAMS=") + len("const EXAMS=")
    exams, _ = json.JSONDecoder().raw_decode(html, i)
    out_dir = ROOT / "exams" / "hieubui"
    out_dir.mkdir(parents=True, exist_ok=True)
    for e in exams:
        d = convert(e)
        if d["parts"] is None:
            del d["parts"]
        name = ("1-" if e["id"].startswith("E") else "2-") + e["id"].lower() + ".json"
        (out_dir / name).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(exams)} đề → {out_dir}")


if __name__ == "__main__":
    main()
