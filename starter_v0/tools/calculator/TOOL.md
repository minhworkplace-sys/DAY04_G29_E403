---
name: calculator
track: custom
kind: utility
requires_env: []
inputs: [expression]
outputs: [expression, result]
side_effect: false
---
# calculator

Thực hiện phép tính toán học cơ bản một cách an toàn (cộng, trừ, nhân, chia, lũy thừa, chia lấy dư, chia lấy phần nguyên).

## Khi nào dùng
- Người dùng yêu cầu tính toán số học đơn giản trong ngữ cảnh nghiên cứu (ví dụ: so sánh tỷ lệ, tính phần trăm thay đổi).

## Khi nào KHÔNG dùng
- Câu hỏi hoàn toàn ngoài phạm vi nghiên cứu (ví dụ: "giải bài toán tích phân") → từ chối, không gọi tool.
- Biểu thức chứa hàm nâng cao (sin, cos, log) → trả lời rằng tool chỉ hỗ trợ phép tính cơ bản.

## Arguments
| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| expression | string | ✅ | Biểu thức toán học (ví dụ: `2 + 3 * 4`) |

## Quicktest
```python
from tools.calculator.tool import evaluate_math
print(evaluate_math("2 + 3 * 4"))   # {'tool': 'calculator', 'expression': '2 + 3 * 4', 'result': 14}
print(evaluate_math("100 / 3"))     # {'tool': 'calculator', 'expression': '100 / 3', 'result': 33.333...}
print(evaluate_math("2 ** 10"))     # {'tool': 'calculator', 'expression': '2 ** 10', 'result': 1024}
```
