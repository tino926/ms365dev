"""
金融數據抓取模塊
支持：Yahoo Finance, Alpha Vantage
"""
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Optional

# 默認追蹤股票
DEFAULT_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

class FinanceDataFetcher:
    """金融數據抓取器"""

    def __init__(self):
        self.stocks = DEFAULT_STOCKS
    
    def get_stock_price(self, symbol: str) -> Optional[Dict]:
        """獲取股票當前價格"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                'symbol': symbol,
                'price': info.get('currentPrice', info.get('regularMarketPrice')),
                'change': info.get('regularMarketChange'),
                'change_percent': info.get('regularMarketChangePercent'),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"獲取 {symbol} 股價失敗：{e}")
            return None
    
    def fetch_all_stocks(self) -> List[Dict]:
        """抓取所有追蹤股票的數據"""
        results = []
        for symbol in self.stocks:
            data = self.get_stock_price(symbol)
            if data:
                results.append(data)
        return results

fetcher = FinanceDataFetcher()

if __name__ == '__main__':
    data = fetcher.fetch_all_stocks()
    for stock in data:
        print(f"{stock['symbol']}: ${stock['price']} ({stock['change_percent']:+.2f}%)")
