---
name: stock_price
track: custom
kind: utility
requires_env: []
inputs: [ticker]
outputs: [ticker, price, currency]
side_effect: false
---
# stock_price

Lấy giá cổ phiếu hiện tại của một công ty dựa trên mã chứng khoán (ticker).

## Khi nào dùng
- Người dùng yêu cầu xem giá cổ phiếu hoặc hỏi về tình hình cổ phiếu hiện tại của một công ty (ví dụ: "Giá cổ phiếu của Apple hiện tại là bao nhiêu?").

## Khi nào KHÔNG dùng
- Khi người dùng hỏi về tin tức kinh doanh chung mà không cụ thể hỏi giá cổ phiếu (Lúc đó hãy dùng tool `lookup` thay thế).

## Arguments
| Tên | Kiểu | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| ticker | string | ✅ | Mã chứng khoán của công ty (ví dụ: `AAPL`, `GOOGL`, `TSLA`). Bắt buộc là mã viết tắt trên sàn chứng khoán. |

## Quicktest
```python
from tools.stock_price.tool import get_stock_price
print(get_stock_price("AAPL"))   
# Result: {'tool': 'get_stock_price', 'ticker': 'AAPL', 'price': 150.25, 'currency': 'USD'}
```
