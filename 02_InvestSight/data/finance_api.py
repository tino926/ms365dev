"""
金融數據抓取模塊
支持：Yahoo Finance, Alpha Vantage
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

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
    
    def get_intraday_data(self, symbol: str, interval: str = '15m', period: str = '1d') -> Optional[pd.DataFrame]:
        """獲取盤中日數據
        
        Args:
            symbol: 股票代碼
            interval: 數據間隔 (1m, 5m, 15m, 30m, 1h)
            period: 數據週期 (1d, 5d, 1wk, 1mo)
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            return data
        except Exception as e:
            print(f"獲取 {symbol} 日內數據失敗：{e}")
            return None
    
    def get_premarket_summary(self, symbol: str) -> Optional[Dict]:
        """獲取收盤前/盤中摘要"""
        try:
            data = self.get_intraday_data(symbol, interval='15m', period='1d')
            if data is None or data.empty:
                return None
            
            current_price = data['Close'].iloc[-1]
            prev_close = data['Open'].iloc[0] if len(data) > 0 else current_price
            
            # 計算變化
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close > 0 else 0
            
            # 獲取盤中最高/最低
            day_high = data['High'].max()
            day_low = data['Low'].min()
            
            # 獲取最後15分鐘數據
            last_15min = data.tail(1)
            pre_close = last_15min['Close'].values[0]
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'prev_close': prev_close,
                'change': change,
                'change_percent': change_pct,
                'day_high': day_high,
                'day_low': day_low,
                'premarket_close': pre_close,
                'volume': data['Volume'].sum(),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"獲取 {symbol} 摘要失敗：{e}")
            return None
    
    def get_all_premarket_summary(self) -> List[Dict]:
        """獲取所有股票的盤中摘要"""
        results = []
        for symbol in self.stocks:
            data = self.get_premarket_summary(symbol)
            if data:
                results.append(data)
        return results
    
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
