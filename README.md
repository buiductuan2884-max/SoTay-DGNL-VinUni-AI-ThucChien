# Sổ tay ĐGNL VinUni AI thực chiến

Một file HTML duy nhất (`index.html`), mở là dùng được, gồm hai phần:

1. **Sổ tay ôn tập**: cấu trúc đề ĐGNL, dạng bài hay gặp, công thức, ví dụ giải từng bước và các bẫy thường gặp cho 4 phần: A Toán, B Lập trình, C AI và sản phẩm, D Logic và đạo đức.
2. **Luyện đề**: 10 đề AI-TEST (60 câu, 90 phút). Có hẹn giờ, nộp bài thì trắc nghiệm được chấm ngay. Mỗi câu hiện đúng/sai, đáp án, cách giải và link tới mục cần ôn trong sổ tay. Câu code và tự luận thì tự chấm theo rubric. Có thể thêm đề bằng file JSON ngay trên trang.

> Tài liệu cộng đồng, không chính thức, không liên kết với VinUni và không phải đề thi thật.

## Dùng

Mở trang GitHub Pages của repo, hoặc tải `index.html` về rồi mở bằng trình duyệt. Tiến độ và đề tự thêm chỉ lưu trong trình duyệt của bạn (localStorage).

## Thêm đề cho cả nhóm

1. Tạo `exams/<tên-bộ>/<tên-đề>.json` theo định dạng của `exams/ai-test/exam-01.json`. Mỗi câu có `module` (A/B/C/D), `type` (`mcq`/`code`/`essay`), `points`, `prompt`; câu `mcq` cần `options` và `answer`; nên có `explanation`, còn `code`/`essay` nên có `modelAnswer` và `rubric`.
2. Có thể thêm `"section": "<mã mục>"` để gắn link ôn tập (ví dụ `a-xs`, `c-rag`, `d-logic`; danh sách mã nằm trong phần "Thêm đề" trên trang). Không ghi thì `build.py` tự đoán.
3. Chạy `python src/build.py` để sinh lại `index.html`, rồi commit.

Chỉ thêm đề do bạn tự soạn hoặc có giấy phép cho phép chia sẻ lại.

## Nguồn

- Đề trong `exams/ai-test/` lấy từ [hungbil/AI-TEST](https://github.com/hungbil/AI-TEST), giấy phép MIT © 2026 Henry Don (xem `exams/ai-test/LICENSE`).
- Phần thống kê trong sổ tay có tham khảo [hieubui2409/ai20k-exam-prep](https://github.com/hieubui2409/ai20k-exam-prep). Câu hỏi của bộ này không được chép vào repo.
- Nội dung sổ tay và ví dụ được soạn mới.
