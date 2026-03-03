#!/usr/bin/env python3
"""
投資分析腳本（進階版）
整合技術指標、情感分析和投資建議
"""
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.finance_api import fetcher as finance_fetcher
from data.news_api import fetcher as news_fetcher
from analysis.sentiment import analyzer as sentiment_analyzer
from analysis.technical_indicators import analyze_stock
from analysis.investment_advisor import get_investment_advice


def main():
    print("=" * 70)
    print("  💡 InvestSight 進階投資分析")
    print("=" * 70)
    print()
    
    # 1. 抓取股價數據
    print("📊 步驟 1: 抓取股價數據...")
    stocks = finance_fetcher.fetch_all_stocks()
    
    if not stocks:
        print("  ✗ 無法獲取股價數據")
        return
    
    print(f"  ✓ 成功抓取 {len(stocks)} 支股票")
    print()
    
    # 2. 抓取新聞
    print("📰 步驟 2: 抓取新聞...")
    articles = news_fetcher.fetch_all()
    print(f"  ✓ 成功抓取 {len(articles)} 篇新聞")
    print()
    
    # 3. 分析每支股票
    print("📈 步驟 3: 分析股票...")
    print()
    
    for stock in stocks[:3]:  # 只分析前 3 支
        symbol = stock['symbol']
        current_price = stock.get('price')
        
        if not current_price:
            continue
        
        print("-" * 60)
        print(f"  {symbol} - ${current_price:.2f} ({stock.get('change_percent', 0):+.2f}%)")
        print("-" * 60)
        
        # 生成模擬價格數據（實際應用應該從歷史數據獲取）
        import random
        base_price = current_price * 0.95
        prices = [base_price + random.uniform(-5, 5) for _ in range(60)]
        prices[-1] = current_price  # 最後一個價格設為當前價格
        
        # 技術指標分析
        indicators = analyze_stock(symbol, prices)
        
        # 尋找相關新聞並分析情感
        stock_sentiment = None
        for article in articles[:5]:
            if symbol.lower() in article['title'].lower():
                stock_sentiment = sentiment_analyzer.analyze_text(article['title'])
                break
        
        # 生成投資建議
        advice = get_investment_advice(
            symbol=symbol,
            indicators=indicators,
            sentiment=stock_sentiment,
            price=current_price
        )
        
        # 顯示結果
        print(f"  技術評分：{advice['technical_analysis']['score']}")
        print(f"  技術建議：{advice['technical_analysis']['recommendation']}")
        
        if advice['sentiment_analysis']:
            print(f"  新聞情感：{advice['sentiment_analysis']['sentiment']} "
                  f"({advice['sentiment_analysis']['impact']:+.1f})")
        
        print(f"  最終建議：{advice['recommendation']}")
        print(f"  信心度：{advice['confidence']}%")
        print(f"  風險等級：{advice['risk_level']}")
        
        if advice['action_items']:
            print(f"  行動建議：")
            for item in advice['action_items'][:3]:
                print(f"    • {item}")
        
        print()
    
    print("=" * 70)
    print("  ✅ 分析完成！")
    print("=" * 70)
    print()
    print("⚠️  免責聲明：")
    print("   本分析僅供參考，不構成投資建議。")
    print("   投資有風險，入市需謹慎。")
    print()


if __name__ == '__main__':
    main()
