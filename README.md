# Sổ tay ĐGNL VinUni AI thực chiến

Một file HTML duy nhất (`index.html`), mở là dùng được, gồm hai phần:

1. **Sổ tay ôn tập**: lộ trình cấp tốc 6 ngày, cấu trúc đề ĐGNL, dạng bài hay gặp, công thức, ví dụ giải từng bước và bẫy thường gặp cho 4 phần: A Toán, B Lập trình, C AI và sản phẩm, D Logic và đạo đức.
2. **Luyện đề**: 32 bộ, 1.472 câu, có hẹn giờ. Nộp bài thì trắc nghiệm, điền số và đoán output được chấm ngay. Mỗi câu hiện đúng/sai, đáp án, cách giải, vì sao phương án sai, giải thích chi tiết và link tới mục cần ôn trong sổ tay. Câu code và tự luận tự chấm theo rubric.

| Bộ đề | Số bộ | Nguồn |
|---|---:|---|
| Đề sát thật | 2 | Tự soạn theo cấu trúc 4 phần, thang 20/30/32/18 |
| Luyện nhanh Toán tính tay, Code viết tay | 2 | Tự soạn, code mẫu đều đã chạy thử |
| Bộ đề anh Hiếu: ĐGNL-01…06, CĐ-01…12 | 18 | [hieubui2409/ai20k-exam-prep](https://github.com/hieubui2409/ai20k-exam-prep), dùng lại với sự cho phép của tác giả |
| AI-TEST | 10 | [hungbil/AI-TEST](https://github.com/hungbil/AI-TEST), giấy phép MIT © 2026 Henry Don |

> Tài liệu cộng đồng, không chính thức, không liên kết với VinUni và không phải đề thi thật.

## Dùng

Mở trang GitHub Pages của repo, hoặc tải `index.html` về rồi mở bằng trình duyệt. Công thức toán (MathJax) và sơ đồ (mermaid) tải từ cdnjs nên cần mạng. Tiến độ và đề tự thêm chỉ lưu trong trình duyệt của bạn.

## Thêm đề cho cả nhóm

1. Tạo `exams/<tên-bộ>/<tên-đề>.json`. Mỗi câu có `module` (A/B/C/D), `type` (`mcq`, `numeric`, `output`, `code`, `essay`), `points`, `prompt`.
   - `mcq`: `options` và `answer`; có thể thêm `distractors` (`{"B": "vì sao B sai"}`).
   - `numeric`: `answer` là số, `tol` là sai số cho phép.
   - `output`: `answer` là chuỗi in ra, `accept` là các cách ghi khác được chấp nhận.
   - `code`, `essay`: `modelAnswer` và `rubric` (chuỗi hoặc `{"criterion", "points"}`).
   - Tuỳ chọn: `explanation`, `long` (giải thích dài, hỗ trợ markdown, `$công thức$`, ```` ```mermaid ````), `level`, `section` (mã mục sổ tay để gắn link ôn tập).
2. Chạy `python src/build.py` để sinh lại `index.html`, rồi commit.
3. Cập nhật bộ đề anh Hiếu khi trang gốc thay đổi: `python src/import_hieubui.py`.

Chỉ thêm đề bạn tự soạn hoặc được phép chia sẻ lại.
