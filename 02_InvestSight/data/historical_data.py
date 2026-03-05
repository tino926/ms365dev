#!/usr/bin/env python3
"""
真實歷史數據獲取模塊
使用 yfinance 獲取真實的歷史股價數據
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def get_historical_data(symbol: str, period: str = '60d') -> Dict:
    """
    獲取歷史股價數據

    Args:
        symbol: 股票代號（如：AAPL, MSFT）
        period: 時間範圍（'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'）

    Returns:
        包含歷史數據的字典
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty:
            print(f"⚠️  無法獲取 {symbol} 的歷史數據")
            return {}

        # 提取數據
        data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'prices': hist['Close'].tolist(),
            'opens': hist['Open'].tolist(),
            'highs': hist['High'].tolist(),
            'lows': hist['Low'].tolist(),
            'volumes': hist['Volume'].tolist(),
            'dates': [d.strftime('%Y-%m-%d') for d in hist.index],
            'current_price': hist['Close'].iloc[-1],
            'change': hist['Close'].iloc[-1] - hist['Close'].iloc[0],
            'change_percent': ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100,
        }

        # 添加統計信息
        data['stats'] = {
            'high': hist['High'].max(),
            'low': hist['Low'].min(),
            'avg_volume': hist['Volume'].mean(),
            'volatility': hist['Close'].std(),
        }

        return data

    except Exception as e:
        print(f"✗ 獲取 {symbol} 歷史數據失敗：{e}")
        return {}


def get_multiple_symbols(symbols: List[str], period: str = '60d') -> Dict[str, Dict]:
    """
    批量獲取多支股票的歷史數據

    Args:
        symbols: 股票代號列表
        period: 時間範圍

    Returns:
        字典，鍵為股票代號，值為歷史數據
    """
    results = {}
    for symbol in symbols:
        data = get_historical_data(symbol, period)
        if data:
            results[symbol] = data
    return results


def get_stock_info(symbol: str) -> Dict:
    """
    獲取股票基本信息

    Args:
        symbol: 股票代號

    Returns:
        股票信息字典
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return {
            'symbol': symbol,
            'name': info.get('longName', info.get('shortName', symbol)),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
            '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
            'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
        }
    except Exception as e:
        print(f"✗ 獲取 {symbol} 信息失敗：{e}")
        return {}


if __name__ == '__main__':
    # 測試
    print("=" * 70)
    print("  📈 真實歷史數據測試")
    print("=" * 70)
    print()

    # 測試單支股票
    print("📊 測試：AAPL 歷史數據")
    print("-" * 70)
    data = get_historical_data('AAPL', '30d')
    if data:
        print(f"  股票：{data['symbol']}")
        print(f"  當前價：${data['current_price']:.2f}")
        print(f"  漲跌：{data['change']:+.2f} ({data['change_percent']:+.2f}%)")
        print(f"  數據點：{len(data['prices'])} 天")
        print(f"  最高：${data['stats']['high']:.2f}")
        print(f"  最低：${data['stats']['low']:.2f}")
        print(f"  波動率：${data['stats']['volatility']:.2f}")
    print()

    # 測試多支股票
    print("📊 測試：多支股票")
    print("-" * 70)
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    data = get_multiple_symbols(symbols, '30d')
    for symbol, stock_data in data.items():
        print(f"  {symbol}: ${stock_data['current_price']:.2f} ({stock_data['change_percent']:+.2f}%)")
    print()

    # 測試股票信息
    print("📊 測試：股票信息")
    print("-" * 70)
    info = get_stock_info('AAPL')
    if info:
        print(f"  名稱：{info['name']}")
        print(f"  行業：{info['sector']}")
        print(f"  市值：${info['market_cap']:,}" if isinstance(info['market_cap'], (int, float)) else f"  市值：{info['market_cap']}")
        print(f"  P/E: {info['pe_ratio']}")
    print()

    print("=" * 70)
    print("  ✅ 測試完成！")
    print("=" * 70)
