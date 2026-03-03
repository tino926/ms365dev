#!/usr/bin/env python3
"""
投資建議生成模塊
基於技術指標和情感分析生成投資建議
"""
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np


class InvestmentAdvisor:
    """投資建議生成器"""

    def __init__(self):
        self.rsi_levels = {
            'overbought': 70,
            'oversold': 30
        }

    def analyze_technical(self, indicators: Dict) -> Dict:
        """
        分析技術指標並給出評分

        Args:
            indicators: 技術指標字典

        Returns:
            技術分析結果
        """
        score = 0  # -100 (強烈賣出) 到 +100 (強烈買入)
        signals = []

        # RSI 分析
        rsi = indicators.get('rsi14', [])
        if rsi and len(rsi) > 0:
            latest_rsi = rsi[-1]
            if not np.isnan(latest_rsi):
                if latest_rsi < self.rsi_levels['oversold']:
                    score += 30
                    signals.append('RSI 超賣，可能反彈')
                elif latest_rsi < 40:
                    score += 10
                    signals.append('RSI 偏低，偏多')
                elif latest_rsi > self.rsi_levels['overbought']:
                    score -= 30
                    signals.append('RSI 超買，可能回調')
                elif latest_rsi > 60:
                    score -= 10
                    signals.append('RSI 偏高，偏空')

        # MACD 分析
        macd = indicators.get('macd', [])
        signal_line = indicators.get('signal', [])
        if macd and signal_line and len(macd) > 1 and len(signal_line) > 1:
            latest_macd = macd[-1]
            prev_macd = macd[-2]
            latest_signal = signal_line[-1]
            prev_signal = signal_line[-2]

            if not (np.isnan(latest_macd) or np.isnan(latest_signal)):
                # 黃金交叉
                if prev_macd <= prev_signal and latest_macd > latest_signal:
                    score += 20
                    signals.append('MACD 黃金交叉')
                # 死亡交叉
                elif prev_macd >= prev_signal and latest_macd < latest_signal:
                    score -= 20
                    signals.append('MACD 死亡交叉')

                # MACD 柱狀圖分析
                histogram = indicators.get('histogram', [])
                if histogram and len(histogram) > 1:
                    latest_hist = histogram[-1]
                    prev_hist = histogram[-2]
                    if not np.isnan(latest_hist) and not np.isnan(prev_hist):
                        if prev_hist < 0 and latest_hist > 0:
                            score += 15
                            signals.append('MACD 柱狀圖由負轉正')
                        elif prev_hist > 0 and latest_hist < 0:
                            score -= 15
                            signals.append('MACD 柱狀圖由正轉負')

        # 布林帶分析
        bb_upper = indicators.get('upper', [])
        bb_lower = indicators.get('lower', [])
        bb_middle = indicators.get('middle', [])
        current_price = indicators.get('current_price')

        if all([bb_upper, bb_lower, bb_middle, current_price]):
            latest_upper = bb_upper[-1]
            latest_lower = bb_lower[-1]
            latest_middle = bb_middle[-1]

            if not (np.isnan(latest_upper) or np.isnan(latest_lower) or np.isnan(latest_middle)):
                if current_price < latest_lower:
                    score += 25
                    signals.append('股價跌破布林帶下軌，可能反彈')
                elif current_price > latest_upper:
                    score -= 25
                    signals.append('股價突破布林帶上軌，可能回調')
                elif current_price < latest_middle:
                    score -= 5
                    signals.append('股價在中軌下方，偏空')
                elif current_price > latest_middle:
                    score += 5
                    signals.append('股價在中軌上方，偏多')

        # 移動平均線分析
        ma20 = indicators.get('ma20', [])
        ma60 = indicators.get('ma60', [])

        if ma20 and current_price:
            latest_ma20 = ma20[-1]
            if not np.isnan(latest_ma20):
                if current_price > latest_ma20:
                    score += 10
                    signals.append('股價在 MA20 上方')
                else:
                    score -= 10
                    signals.append('股價在 MA20 下方')

        # 確定建議
        if score >= 50:
            recommendation = '強烈買入'
            confidence = min(score, 100)
        elif score >= 20:
            recommendation = '買入'
            confidence = score
        elif score >= -20:
            recommendation = '持有'
            confidence = 50 + score
        elif score >= -50:
            recommendation = '賣出'
            confidence = 50 + score
        else:
            recommendation = '強烈賣出'
            confidence = max(0, 50 + score)

        return {
            'score': score,
            'recommendation': recommendation,
            'confidence': round(confidence, 2),
            'signals': signals,
            'timestamp': datetime.now().isoformat()
        }

    def analyze_sentiment(self, sentiment_data: Dict) -> Dict:
        """
        分析情感數據

        Args:
            sentiment_data: 情感分析數據

        Returns:
            情感分析結果
        """
        if not sentiment_data:
            return {
                'sentiment': 'neutral',
                'score': 0,
                'impact': 0
            }

        sentiment = sentiment_data.get('sentiment', 'neutral')
        polarity = sentiment_data.get('polarity', 0)

        # 計算情感影響分數
        if sentiment == 'positive':
            impact = min(polarity * 20, 30)  # 最多 +30 分
        elif sentiment == 'negative':
            impact = max(polarity * 20, -30)  # 最多 -30 分
        else:
            impact = 0

        return {
            'sentiment': sentiment,
            'score': round(polarity, 3),
            'impact': round(impact, 2)
        }

    def generate_recommendation(self, 
                                symbol: str,
                                indicators: Dict,
                                sentiment_data: Optional[Dict] = None,
                                current_price: Optional[float] = None) -> Dict:
        """
        生成完整的投資建議

        Args:
            symbol: 股票代號
            indicators: 技術指標字典
            sentiment_data: 情感分析數據（可選）
            current_price: 當前價格（可選）

        Returns:
            完整的投資建議
        """
        # 添加當前價格到指標
        if current_price:
            indicators['current_price'] = current_price

        # 技術分析
        technical_analysis = self.analyze_technical(indicators)

        # 情感分析
        sentiment_analysis = self.analyze_sentiment(sentiment_data) if sentiment_data else None

        # 綜合評分
        final_score = technical_analysis['score']
        if sentiment_analysis:
            final_score += sentiment_analysis['impact']

        # 調整最終建議
        if final_score >= 50:
            final_recommendation = '強烈買入'
        elif final_score >= 20:
            final_recommendation = '買入'
        elif final_score >= -20:
            final_recommendation = '持有'
        elif final_score >= -50:
            final_recommendation = '賣出'
        else:
            final_recommendation = '強烈賣出'

        # 生成報告
        report = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'current_price': current_price,
            'technical_analysis': technical_analysis,
            'sentiment_analysis': sentiment_analysis,
            'final_score': round(final_score, 2),
            'recommendation': final_recommendation,
            'confidence': round(min(100, max(0, 50 + final_score)), 2),
            'risk_level': self._assess_risk(indicators),
            'action_items': self._generate_action_items(final_recommendation, technical_analysis)
        }

        return report

    def _assess_risk(self, indicators: Dict) -> str:
        """評估風險等級"""
        rsi = indicators.get('rsi14', [])
        
        if rsi and len(rsi) > 0:
            latest_rsi = rsi[-1]
            if not np.isnan(latest_rsi):
                if latest_rsi > 80 or latest_rsi < 20:
                    return '高風險'
                elif latest_rsi > 60 or latest_rsi < 40:
                    return '中風險'
        
        return '正常風險'

    def _generate_action_items(self, recommendation: str, technical_analysis: Dict) -> List[str]:
        """生成行動建議"""
        actions = []

        if '買入' in recommendation:
            actions.append('考慮建立部位')
            actions.append('設定停損點')
            actions.append('分批進場降低風險')
        elif '賣出' in recommendation:
            actions.append('考慮減碼或出清')
            actions.append('設定停利點')
            actions.append('注意市場變化')
        elif '持有' in recommendation:
            actions.append('繼續觀察')
            actions.append('維持現有部位')
            actions.append('等待更明確訊號')

        # 添加技術分析的具体建議
        for signal in technical_analysis.get('signals', [])[:3]:
            actions.append(f'注意：{signal}')

        return actions[:5]  # 最多 5 個建議


# 快捷函數
def get_investment_advice(symbol: str, 
                          indicators: Dict, 
                          sentiment: Optional[Dict] = None,
                          price: Optional[float] = None) -> Dict:
    """
    快速獲取投資建議

    Args:
        symbol: 股票代號
        indicators: 技術指標字典
        sentiment: 情感分析數據（可選）
        price: 當前價格（可選）

    Returns:
        投資建議字典
    """
    advisor = InvestmentAdvisor()
    return advisor.generate_recommendation(symbol, indicators, sentiment, price)


if __name__ == '__main__':
    # 測試
    import random
    import sys
    from pathlib import Path
    
    # 添加項目根目錄到路徑
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    
    # 生成模擬數據
    base_price = 100
    prices = [base_price + random.uniform(-5, 5) for _ in range(60)]
    
    # 計算技術指標
    from analysis.technical_indicators import TechnicalIndicators
    indicators_calc = TechnicalIndicators()
    
    indicators = {
        'rsi14': indicators_calc.calculate_rsi(prices, 14),
        'macd': indicators_calc.calculate_macd(prices)['macd'],
        'signal': indicators_calc.calculate_macd(prices)['signal'],
        'histogram': indicators_calc.calculate_macd(prices)['histogram'],
        'upper': indicators_calc.calculate_bollinger_bands(prices)['upper'],
        'lower': indicators_calc.calculate_bollinger_bands(prices)['lower'],
        'middle': indicators_calc.calculate_bollinger_bands(prices)['middle'],
        'ma20': indicators_calc.calculate_ma(prices, 20),
        'ma60': indicators_calc.calculate_ma(prices, 60),
        'current_price': prices[-1]
    }

    # 模擬情感數據
    sentiment = {
        'sentiment': 'positive',
        'polarity': 0.3
    }

    # 生成建議
    advisor = InvestmentAdvisor()
    report = advisor.generate_recommendation('AAPL', indicators, sentiment, prices[-1])

    print(f"\n📈 股票：{report['symbol']}")
    print(f"💰 當前價格：${report['current_price']:.2f}")
    print()
    print("📊 技術分析:")
    print(f"  評分：{report['technical_analysis']['score']}")
    print(f"  建議：{report['technical_analysis']['recommendation']}")
    print(f"  信心度：{report['technical_analysis']['confidence']}%")
    print()
    print("📰 情感分析:")
    if report['sentiment_analysis']:
        print(f"  情感：{report['sentiment_analysis']['sentiment']}")
        print(f"  影響：{report['sentiment_analysis']['impact']}")
    print()
    print("💡 最終建議:")
    print(f"  綜合評分：{report['final_score']}")
    print(f"  建議：{report['recommendation']}")
    print(f"  信心度：{report['confidence']}%")
    print(f"  風險等級：{report['risk_level']}")
    print()
    print("📋 行動建議:")
    for i, action in enumerate(report['action_items'], 1):
        print(f"  {i}. {action}")
    print()
    print("=" * 60)
    print("  ✅ 投資建議生成完成！")
    print("=" * 60)
