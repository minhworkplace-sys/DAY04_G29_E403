# Tool: `weather`

## Mục đích
Lấy thông tin thời tiết hiện tại hoặc dự báo cho một địa điểm bất kỳ.

## Khi nào dùng
- Dùng khi user hỏi về thời tiết: "thời tiết Hà Nội hôm nay", "nhiệt độ ở Tokyo", "trời Đà Nẵng có mưa không?"
- Dùng để cung cấp context thời tiết kèm theo nghiên cứu (ví dụ: "tình hình lũ lụt ở miền Trung")

## Khi nào KHÔNG dùng
- Không dùng cho câu hỏi tổng quát về khí hậu dài hạn (dùng `lookup` thay thế)
- Không dùng khi user hỏi về tin thời tiết (news) — dùng `lookup` với topic="news"
- Không có side effect, không cần xác nhận

## Arguments
| Tham số | Kiểu | Mặc định | Mô tả |
|---------|------|---------|-------|
| `city` | string | `""` | Tên thành phố (tiếng Anh hoặc tiếng Việt) |
| `units` | string | `"metric"` | Đơn vị: `"metric"` (°C, km/h) hoặc `"imperial"` (°F, mph) |

## Output
Trả về dict với: `city`, `temp_c`, `feels_like_c`, `description`, `humidity`, `wind_kmph`, `forecast` (3 ngày).

## Implementation
`tools/weather/tool.py` — dùng wttr.in JSON API (miễn phí, không cần API key).

## Quicktest
```python
from tools import TOOL_FUNCTIONS
result = TOOL_FUNCTIONS["weather"](city="Hanoi")
print(result)
# Expected: {'tool': 'weather', 'city': 'Hanoi', 'temp_c': '...', 'description': '...'}
```
