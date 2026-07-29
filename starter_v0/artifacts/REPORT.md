# Day 04 Lab v2 Report — Research Agent

## Team
- Team: G29
- Members: [ĐIỀN TÊN CÁC THÀNH VIÊN VÀO ĐÂY]
- Provider/model: Gemini / gemini-2.5-flash

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent: Có khả năng tra cứu tin tức thời sự mới nhất, đọc nội dung các trang web, tìm kiếm xu hướng hoặc theo dõi bài đăng của người nổi tiếng trên mạng xã hội, và tra cứu giá cổ phiếu (bằng Tool mới).

**Link dùng thử:**
URL: `http://localhost:8501` (Chạy local bằng lệnh `streamlit run app.py`)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| lookup | Tra cứu thông tin, tin tức trên web | không |
| timeline | Lấy bài đăng của một tài khoản cụ thể | không |
| social_search | Tìm xu hướng chung trên mạng xã hội | không |
| fetch | Lấy nội dung từ một đường link (URL) cụ thể | không |
| format | Trình bày, tổng hợp dữ liệu thành báo cáo | không |
| send | Gửi văn bản đi (yêu cầu xác nhận) | không |
| stock_price | Tra cứu giá cổ phiếu của một công ty dựa vào mã chứng khoán (Ticker) | **CÓ** |

## A3. Câu hỏi mẫu để thử

1. Tìm tin tức hôm nay về Apple và tóm tắt lại những điểm chính.
2. Sam Altman có dòng tweet nào mới không?
3. Giá cổ phiếu của Apple và Microsoft hiện tại là bao nhiêu?

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Nghiên cứu tin tức | `lookup` -> `format` | Ở v0, agent dùng bừa tool. Ở v1, agent dùng đúng `lookup` nhờ system_prompt rõ ràng. | transcript `v3_gemini...` |
| Bổ sung thông tin | `clarify` -> `fetch` | Agent không đoán mò URL mà biết hỏi lại người dùng. | transcript `v3_gemini...` |
| Tính năng xem giá cổ phiếu | `stock_price` | AI biết dùng `stock_price` để tra cứu giá theo mã thay vì tìm kiếm web chung chung. | (Thử trực tiếp trên Streamlit) |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Chạy file gốc không chỉnh sửa | tool_routing_accuracy | 0 | 0.7143 | v0_B_base_gemini_20260729T101625.json |
| v1 | system_prompt.md | Sửa prompt để chặn đoán bừa | tool_routing_accuracy | 0.7143 | 0.7857 | v1_B_base_gemini_20260729T103349229551.json |
| v2 | tools.yaml | Làm rõ mô tả timeline và social_search | tool_routing_accuracy | 0.7857 | 0.8889 | v2_B_base_gemini_20260729T104832168980.json |
| v3 | eval_group.json | Test bộ 10 câu hỏi riêng của nhóm | tool_routing_accuracy | 0.8889 | 0.7143 | v3_B_group_gemini_20260729T113049393115.json |

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R01_user_tweets | wrong_tool | `social_search` | Dùng `social_search` thay vì `timeline` cho tên "Sam Altman" | Sửa `tools.yaml` để nhấn mạnh `timeline` dùng khi biết rõ tên người nổi tiếng. |
| G05_send_boundary | wrong_boundary | `send(confirmed=true)` | Gửi tin nhắn mà không có sự xác nhận | Nhấn mạnh trong prompt và cờ `confirmed` bắt buộc `false` khi khởi tạo. |

## B3. Team eval cases

- 5 single-turn:
  - G01_math_trap: Hỏi toán ngoài phạm vi -> refuse
  - G02_news_trap: Tìm tin OpenAI -> lookup
  - G03_social_top: Tìm trend Gemini -> social_search
  - G04_missing_url: Thiếu link -> clarify
  - G05_send_boundary: Gửi tin -> send(confirmed=false)
- 5 multi-turn:
  - G06_multi_clarify_news: Hỏi mảng AI -> y tế -> lookup
  - G07_multi_switch_topic: Đang tìm tweet -> đổi sang tìm tin Tesla -> lookup
  - G08_multi_confirm_send: Xác nhận email -> đồng ý -> send(confirmed=true)
  - G09_multi_missing_info: 5 tweet gần nhất -> của BillGates -> timeline
  - G10_multi_url_summary: Hỏi link Google -> đổi sang link Apple -> fetch

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G02_news_trap | Phân luồng tìm tin tức theo thời gian | lookup | PASS |
| G04_missing_url | Phản xạ khi thiếu dữ liệu đầu vào | clarify | PASS |
| G08_multi_confirm_send| Lời nhắc xác nhận từ nhiều hội thoại| send(confirmed=true) | PASS |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Tìm tin tức AI | v3 | `lookup({"query": "AI", "timeframe": "day", "topic": "news"})` | v3_gemini_20260729T113400627476.transcript.json | PASS - Trả về 4 bài báo đúng như yêu cầu |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên (stock_price) | `tools/stock_price/tool.py` | Trả về đúng giá `150.25 USD` cho mã `AAPL` thông qua giao diện Streamlit | Code gọi trực tiếp API của Yahoo Finance để lấy giá realtime (Không dùng Mock). Xử lý tốt lỗi mạng (timeout) hoặc nhập sai mã (not_found). |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**
  Các quy tắc về hành vi tổng quát của trợ lý (từ chối câu hỏi ngoài phạm vi, không đoán mò thông tin, không làm toán phức tạp).
- **Which fixes belonged in `tools.yaml`?**
  Quy tắc phân biệt và chọn công cụ phù hợp khi có các tool tương tự nhau (ví dụ `timeline` so với `social_search`), và ý nghĩa chi tiết của từng tham số (như `confirmed` của tool `send`).
- **What would you improve next?**
  Xử lý lỗi Provider Error tốt hơn khi dùng vượt quá API Quota, và tối ưu khả năng suy luận (nhận diện tên riêng sang handle mạng xã hội).
