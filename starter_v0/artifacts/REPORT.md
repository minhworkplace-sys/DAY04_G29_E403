# Day 04 Lab v2 Report — Research Agent

## Team

- Team: G29
- Members: Vu Minh Quang (2A202601515)
- Provider/model: Gemini / `gemini-2.5-flash`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent hỗ trợ tìm kiếm tin tức trên web/mạng xã hội, tra cứu bài báo khoa học, kiểm tra thời tiết các thành phố, đọc nội dung URL và tổng hợp thành bản tin markdown digest theo các mẫu quy định.

**Link dùng thử (truy cập được trong showdown):**

> URL: http://localhost:8501 (Chạy bằng lệnh `streamlit run app.py`)

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin (handle, URL) hoặc xin xác nhận trước khi gửi | Không |
| timeline | Lấy các bài đăng mới nhất từ một tài khoản Twitter/X cụ thể | Không |
| social_search | Tìm kiếm bài đăng trên mạng xã hội theo từ khóa (Latest/Top) | Không |
| lookup | Tra cứu thông tin trên Web (tin tức/bài viết chung) | Không |
| fetch | Đọc và trích xuất nội dung văn bản từ một đường dẫn URL cụ thể | Không |
| format | Trình bày danh sách dữ liệu thu thập được thành định dạng Markdown Digest | Không |
| send | Gửi thông điệp lên kênh Telegram (cần xác nhận qua clarify trước) | Không |
| policy | Tra cứu quy định nội bộ công ty | Không |
| papers | Tìm kiếm bài báo khoa học trên arXiv | Không |
| paper_text | Tải và đọc trích xuất nội dung PDF bài báo arXiv | Không |
| weather | Tra cứu thời tiết hiện tại và dự báo 3 ngày cho thành phố bất kỳ | **Có (Must-have new tool)** |

## A3. Câu hỏi mẫu để thử

1. "Thời tiết hôm nay ở Hà Nội thế nào?" *(Thử tool mới weather)*
2. "Tin tức AI hôm nay có gì nổi bật?" *(Thử lookup tin tức)*
3. "Tóm tắt 5 tweet mới nhất giúp mình" *(Thử clarify hỏi bổ sung handle)*
4. "Đăng bản tin này lên Telegram giúp mình" *(Thử boundary xác nhận gửi)*

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Hỏi thời tiết Hà Nội | `weather(city='Hanoi')` | v0 chưa có tool weather -> v3 hỗ trợ tra cứu thời tiết thời gian thực qua API | `runs/v3_B_group_gemini_20260729T114859694985.json` |
| Tìm tin AI hôm nay | `lookup(query='AI', topic='news', timeframe='day')` | v0 tự ghép từ "news" vào query (`AI news`) -> v2 fix `tools.yaml` giúp trích đúng query thuần `AI` | `runs/v2_B_base_gemini_20260729T112037978575.json` |
| Thiếu handle tài khoản | `clarify(response_type='text')` -> `timeline(screenname='sama')` | v0 tự đoán tài khoản -> v3 thêm Strict Clarify Rules buộc hỏi lại người dùng | `runs/v3_B_base_gemini_20260729T112739962418.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version evidence

Dữ liệu thực tế từ `artifacts/version_log.csv` và `runs/*.json`:

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | Baseline chưa tối ưu | Đo hành vi gốc trước khi cải thiện | case_accuracy | N/A | 0.60 | `runs/v0_B_base_gemini_20260729T104100809207.json` |
| v1 | Rút ngắn prompt + thêm boundary/clarify rules | Prompt ngắn & rõ ràng hơn giúp routing và out-of-scope đúng hơn | case_accuracy | 0.60 | 0.65 | `runs/v1_B_base_gemini_20260729T111329211977.json` |
| v2 | Cải thiện tool descriptions trong `tools.yaml` (clarify, lookup, send, fetch) | Mô tả tham số query thuần & mục đích sử dụng chi tiết giúp tăng mạnh độ chính xác routing và args | case_accuracy | 0.65 | 0.85 | `runs/v2_B_base_gemini_20260729T112037978575.json` |
| v3 | Thêm STRICT clarify rules + guide phân biệt response_type | Hướng dẫn rõ khi nào chọn `text` vs `yes_no` để sửa lỗi thiếu thông tin và boundary | case_accuracy | 0.85 | 0.90 | `runs/v3_B_base_gemini_20260729T112739962418.json` |

## B2. Failure analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_tool` (v0) | `lookup(query='AI news')` | Model ghép từ "news" vào trường `query` thay vì đưa vào param `topic` | Cập nhật mô tả `lookup` trong `tools.yaml` yêu cầu `query` chỉ chứa từ khóa thuần |
| R08_out_of_scope | `out_of_scope` (v0) | `lookup(...)` | System prompt cũ bảo "tự đoán và gọi tool", agent gọi tool tra cứu toán tích phân | Sửa `system_prompt.md` thêm quy tắc từ chối thẳng các yêu cầu ngoài phạm vi research |
| R10_missing_handle | `missing_info` (v1) | `timeline(screenname='sama')` | Agent tự ý chọn tài khoản Sam Altman thay vì hỏi lại người dùng | Thêm quy tắc **STRICT clarify rules** trong v3 buộc gọi `clarify` khi thiếu thông tin |
| R12_confirm_before_send | `wrong_boundary` (v2) | `send(...)` trực tiếp | Agent tự động gửi tin nhắn mà không qua bước xác nhận | Thêm quy tắc bắt buộc gọi `clarify(response_type='yes_no')` trước khi gọi `send` |

## B3. Team eval cases

10 eval cases bổ sung trong `data/eval_group.json` (Đạt độ chính xác 10/10 = **100% PASS**):

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_lookup_news_today | Single-turn: Query từ khóa thuần 'DeepSeek', topic=news, timeframe=day | `lookup(query='DeepSeek', topic='news', timeframe='day')` | PASS |
| G02_social_search_top | Single-turn: Yêu cầu bài đăng phổ biến/trending | `social_search(query='ChatGPT', search_type='Top')` | PASS |
| G03_out_of_scope_translation | Single-turn: Yêu cầu dịch thuật ngoài phạm vi | `no_tool` (Từ chối / Giải thích) | PASS |
| G04_missing_url_clarify | Single-turn: Thiếu URL bài báo | `clarify(response_type='text')` | PASS |
| G05_weather_lookup | Single-turn: Hỏi thời tiết cụ thể ở Hà Nội (Tool mới) | `weather(city='Hanoi')` | PASS |
| G06_multi_switch_to_top | Multi-turn: Đổi ý sang bài trending ở turn sau | `social_search(query='Gemini AI', search_type='Top')` | PASS |
| G07_multi_carryover_handle | Multi-turn: Giữ nguyên handle `elonmusk` & cập nhật limit=10 | `timeline(screenname='elonmusk', limit=10)` | PASS |
| G08_multi_clarify_missing_handle | Multi-turn: Cung cấp handle sau câu hỏi của agent | `timeline(screenname='sundar_pichai')` | PASS |
| G09_multi_send_after_confirm | Multi-turn: Gọi send sau khi user xác nhận "Có" | `send(text='...', confirmed=True)` | PASS |
| G10_multi_url_provided_later | Multi-turn: Đọc URL sau khi user dán link ở turn 2 | `fetch(url='https://arxiv.org/abs/2303.08774')` | PASS |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Tra cứu thời tiết Hà Nội | v3 | `weather(city='Hanoi')` | UI Streamlit Session | Trả về thời tiết 26°C, mưa vừa và dự báo 3 ngày |
| Đọc bài báo từ URL | v3 | `fetch(url='https://openai.com/blog/gpt-5')` | UI Streamlit Session | Trích xuất thành công văn bản trang |
| Yêu cầu đăng bài Telegram | v3 | `clarify(question='...', response_type='yes_no')` | UI Streamlit Session | Agent dừng lại hỏi xin xác nhận trước khi gửi |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới (`weather`) | `tools/weather/tool.py`, `tools/weather/TOOL.md` | Tự động lấy dữ liệu thời tiết thời gian thực từ wttr.in theo tên thành phố | Cần validate tên thành phố hợp lệ |
| Baseline Core Tools | `tools/lookup/tool.py`, `tools/clarify/tool.py` | Web search trích xuất tham số tin tức & hỏi lại thông tin thiếu | Guardrail không tự đoán thông tin khi thiếu dữ liệu |

## B6. Reflection

- **Sửa trong `system_prompt.md`**: Phù hợp cho việc thiết lập các nguyên tắc chung (General behavior), quy định khi nào phải dừng lại từ chối (Out-of-scope) và các điều kiện bắt buộc phải hỏi xác nhận (`STRICT clarify rules`).
- **Sửa trong `tools.yaml`**: Cực kỳ hiệu quả trong việc định hướng tham số (Argument extraction), đưa ra ví dụ chuẩn hóa cho `query`, `topic`, `timeframe`, và phân định rõ ràng ranh giới khi nào gọi tool này thay vì tool khác.
- **Đánh giá thủ công vs Tự động**: Các trường hợp routing PASS nhưng nội dung args có thể lệch nhẹ chuẩn (ví dụ response_type trong clarify) cần review log thủ công để phát hiện đúng bản chất failure.
- **Hướng cải thiện tiếp theo**: Mở rộng thêm cache dữ liệu thời tiết/web search để giảm latency và hạn chế nguy cơ bị rate limit 429 từ Provider API.
