#!/usr/bin/env python3
"""
技術指標分析模塊
提供常見的股票技術指標：MA, MACD, RSI, Bollinger Bands 等
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class TechnicalIndicators:
    """技術指標計算器"""

    def __init__(self):
        pass

    def calculate_ma(self, prices: List[float], period: int = 20) -> List[float]:
        """
        計算移動平均線 (Moving Average)

        Args:
            prices: 收盤價列表
            period: 週期（預設 20 日）

        Returns:
            MA 值列表
        """
        if len(prices) < period:
            return []

        ma_values = []
        for i in range(len(prices) - period + 1):
            ma = sum(prices[i:i + period]) / period
            ma_values.append(ma)

        # 前面補 NaN 以保持長度一致
        return [np.nan] * (period - 1) + ma_values

    def calculate_ema(self, prices: List[float], period: int = 20) -> List[float]:
        """
        計算指數移動平均線 (Exponential Moving Average)

        Args:
            prices: 收盤價列表
            period: 週期

        Returns:
            EMA 值列表
        """
        if len(prices) < period:
            return []

        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]  # 第一個 EMA 用 SMA

        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])

        return [np.nan] * (period - 1) + ema

    def calculate_macd(self, prices: List[float], 
                       fast_period: int = 12, 
                       slow_period: int = 26, 
                       signal_period: int = 9) -> Dict[str, List[float]]:
        """
        計算 MACD (Moving Average Convergence Divergence)

        Args:
            prices: 收盤價列表
            fast_period: 快線週期（預設 12）
            slow_period: 慢線週期（預設 26）
            signal_period: 訊號線週期（預設 9）

        Returns:
            包含 MACD 線、訊號線、柱狀圖的字典
        """
        if len(prices) < slow_period:
            return {'macd': [], 'signal': [], 'histogram': []}

        # 計算快慢 EMA
        ema_fast = self.calculate_ema(prices, fast_period)
        ema_slow = self.calculate_ema(prices, slow_period)

        # 計算 MACD 線
        macd_line = [f - s if not (np.isnan(f) or np.isnan(s)) else np.nan 
                     for f, s in zip(ema_fast, ema_slow)]

        # 計算訊號線 (MACD 的 EMA)
        macd_valid = [m for m in macd_line if not np.isnan(m)]
        signal_line = self.calculate_ema(macd_valid, signal_period) if macd_valid else []

        # 填充 NaN
        signal_line = [np.nan] * (len(macd_line) - len(signal_line)) + signal_line

        # 計算柱狀圖
        histogram = [m - s if not (np.isnan(m) or np.isnan(s)) else np.nan 
                    for m, s in zip(macd_line, signal_line)]

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    def calculate_rsi(self, prices: List[float], period: int = 14) -> List[float]:
        """
        計算 RSI (Relative Strength Index)

        Args:
            prices: 收盤價列表
            period: 週期（預設 14）

        Returns:
            RSI 值列表（0-100）
        """
        if len(prices) < period + 1:
            return []

        # 計算價格變化
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]

        rsi_values = []
        for i in range(len(deltas) - period + 1):
            window = deltas[i:i + period]
            gains = [d for d in window if d > 0]
            losses = [-d for d in window if d < 0]

            if not losses:
                rsi = 100
            else:
                avg_gain = sum(gains) / period
                avg_loss = sum(losses) / period
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        return [np.nan] * period + rsi_values

    def calculate_bollinger_bands(self, prices: List[float], 
                                   period: int = 20, 
                                   std_dev: float = 2.0) -> Dict[str, List[float]]:
        """
        計算布林帶 (Bollinger Bands)

        Args:
            prices: 收盤價列表
            period: 週期（預設 20）
            std_dev: 標準差倍數（預設 2）

        Returns:
            包含上軌、中軌、下軌的字典
        """
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}

        upper, middle, lower = [], [], []

        for i in range(len(prices) - period + 1):
            window = prices[i:i + period]
            ma = sum(window) / period
            std = np.std(window)

            middle.append(ma)
            upper.append(ma + std_dev * std)
            lower.append(ma - std_dev * std)

        # 填充 NaN
        nan_count = period - 1
        return {
            'upper': [np.nan] * nan_count + upper,
            'middle': [np.nan] * nan_count + middle,
            'lower': [np.nan] * nan_count + lower
        }

    def calculate_stochastic(self, highs: List[float], 
                             lows: List[float], 
                             closes: List[float], 
                             k_period: int = 14, 
                             d_period: int = 3) -> Dict[str, List[float]]:
        """
        計算 KD 指標 (Stochastic Oscillator)

        Args:
            highs: 最高價列表
            lows: 最低價列表
            closes: 收盤價列表
            k_period: %K 週期（預設 14）
            d_period: %D 週期（預設 3）

        Returns:
            包含 %K 和 %D 的字典
        """
        if len(closes) < k_period:
            return {'k': [], 'd': []}

        k_values = []
        for i in range(len(closes) - k_period + 1):
            window_high = max(highs[i:i + k_period])
            window_low = min(lows[i:i + k_period])
            
            if window_high == window_low:
                k = 50
            else:
                k = ((closes[i + k_period - 1] - window_low) / 
                     (window_high - window_low)) * 100
            k_values.append(k)

        # 計算 %D (%K 的 MA)
        d_values = []
        for i in range(len(k_values) - d_period + 1):
            d = sum(k_values[i:i + d_period]) / d_period
            d_values.append(d)

        return {
            'k': [np.nan] * (k_period - 1) + k_values,
            'd': [np.nan] * (k_period + d_period - 2) + d_values
        }

    def calculate_atr(self, highs: List[float], 
                      lows: List[float], 
                      closes: List[float], 
                      period: int = 14) -> List[float]:
        """
        計算 ATR (Average True Range)

        Args:
            highs: 最高價列表
            lows: 最低價列表
            closes: 收盤價列表
            period: 週期（預設 14）

        Returns:
            ATR 值列表
        """
        if len(closes) < period + 1:
            return []

        # 計算 True Range
        tr_values = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],  # 當日高低差
                abs(highs[i] - closes[i - 1]),  # 當日高與昨日收盤差
                abs(lows[i] - closes[i - 1])   # 當日低與昨日收盤差
            )
            tr_values.append(tr)

        # 計算 ATR
        atr_values = []
        for i in range(len(tr_values) - period + 1):
            atr = sum(tr_values[i:i + period]) / period
            atr_values.append(atr)

        return [np.nan] * period + atr_values

    def get_all_indicators(self, 
                           prices: List[float],
                           highs: Optional[List[float]] = None,
                           lows: Optional[List[float]] = None,
                           closes: Optional[List[float]] = None) -> Dict:
        """
        一次性獲取所有技術指標

        Args:
            prices: 收盤價列表
            highs: 最高價列表（可選）
            lows: 最低價列表（可選）
            closes: 收盤價列表（可選，用於 KD）

        Returns:
            包含所有指標的字典
        """
        if highs is None:
            highs = prices
        if lows is None:
            lows = prices
        if closes is None:
            closes = prices

        result = {
            'ma20': self.calculate_ma(prices, 20),
            'ma60': self.calculate_ma(prices, 60),
            'ema12': self.calculate_ema(prices, 12),
            'ema26': self.calculate_ema(prices, 26),
            'rsi14': self.calculate_rsi(prices, 14),
        }

        # MACD
        macd = self.calculate_macd(prices)
        result.update(macd)

        # 布林帶
        bb = self.calculate_bollinger_bands(prices)
        result.update(bb)

        # KD 指標
        if len(closes) >= 14:
            kd = self.calculate_stochastic(highs, lows, closes)
            result.update(kd)

        # ATR
        if len(closes) >= 15:
            result['atr'] = self.calculate_atr(highs, lows, closes)

        return result


# 快捷函數
def analyze_stock(symbol: str, prices: List[float]) -> Dict:
    """
    快速分析股票技術指標

    Args:
        symbol: 股票代號
        prices: 收盤價列表

    Returns:
        分析結果字典
    """
    indicators = TechnicalIndicators()
    result = indicators.get_all_indicators(prices)

    # 添加股票資訊
    result['symbol'] = symbol
    result['timestamp'] = datetime.now().isoformat()
    result['price_count'] = len(prices)
    result['latest_price'] = prices[-1] if prices else None

    return result


if __name__ == '__main__':
    # 測試
    import random

    print("=" * 60)
    print("  📈 技術指標測試")
    print("=" * 60)

    # 生成模擬數據
    base_price = 100
    prices = [base_price + random.uniform(-5, 5) for _ in range(60)]
    highs = [p + random.uniform(0, 3) for p in prices]
    lows = [p - random.uniform(0, 3) for p in prices]

    indicators = TechnicalIndicators()

    # 測試各個指標
    print("\nMA (20 日):")
    ma = indicators.calculate_ma(prices, 20)
    print(f"  最新 MA20: {ma[-1]:.2f}" if ma else "  數據不足")

    print("\nRSI (14 日):")
    rsi = indicators.calculate_rsi(prices, 14)
    if rsi and not np.isnan(rsi[-1]):
        rsi_val = rsi[-1]
        signal = "超買" if rsi_val > 70 else "超賣" if rsi_val < 30 else "中性"
        print(f"  最新 RSI: {rsi_val:.2f} ({signal})")
    else:
        print("  數據不足")

    print("\nMACD:")
    macd = indicators.calculate_macd(prices)
    if macd['macd'] and not np.isnan(macd['macd'][-1]):
        print(f"  MACD 線：{macd['macd'][-1]:.2f}")
        print(f"  訊號線：{macd['signal'][-1]:.2f}")
        print(f"  柱狀圖：{macd['histogram'][-1]:.2f}")
    else:
        print("  數據不足")

    print("\n布林帶:")
    bb = indicators.calculate_bollinger_bands(prices)
    if bb['middle'] and not np.isnan(bb['middle'][-1]):
        print(f"  上軌：{bb['upper'][-1]:.2f}")
        print(f"  中軌：{bb['middle'][-1]:.2f}")
        print(f"  下軌：{bb['lower'][-1]:.2f}")
        print(f"  當前價：{prices[-1]:.2f}")
    else:
        print("  數據不足")

    print("\n✅ 所有指標計算完成！")
