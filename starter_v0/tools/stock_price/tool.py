from __future__ import annotations

import urllib.request
import json
from typing import Any

def get_stock_price(ticker: str = "") -> dict[str, Any]:
    """Lấy giá cổ phiếu trực tiếp từ Yahoo Finance."""
    if not ticker.strip():
        return {"tool": "get_stock_price", "error": "missing_ticker", "message": "Ticker symbol is required."}
    
    ticker = ticker.strip().upper()
    
    try:
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            result = data.get('chart', {}).get('result', [])
            if not result:
                return {"tool": "get_stock_price", "error": "not_found", "message": f"Không tìm thấy dữ liệu cho mã chứng khoán {ticker}."}
            
            meta = result[0].get('meta', {})
            price = meta.get('regularMarketPrice')
            currency = meta.get('currency', 'USD')
            
            return {
                "tool": "get_stock_price",
                "ticker": ticker,
                "price": price,
                "currency": currency,
            }
    except Exception as e:
        return {
            "tool": "get_stock_price",
            "error": type(e).__name__,
            "message": f"Lỗi khi lấy dữ liệu cổ phiếu: {str(e)}"
        }
