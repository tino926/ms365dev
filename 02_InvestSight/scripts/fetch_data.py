#!/usr/bin/env python3
"""
數據抓取腳本
"""
import sys
import os
from pathlib import Path

# 添加項目根目錄到路徑
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)
os.chdir(project_root)

from data.finance_api import fetcher as finance_fetcher
from data.news_api import fetcher as news_fetcher
from analysis.sentiment import analyzer as sentiment_analyzer

def main():
    print("=" * 50)
    print("📊 抓取金融數據...")
    print("=" * 50)
    stocks = finance_fetcher.fetch_all_stocks()
    for stock in stocks:
        print(f"{stock['symbol']}: ${stock['price']} ({stock['change_percent']:+.2f}%)")
    
    print("\n" + "=" * 50)
    print("📰 抓取新聞...")
    print("=" * 50)
    articles = news_fetcher.fetch_all()
    print(f"抓取到 {len(articles)} 篇新聞")
    
    # 情感分析
    if articles:
        print("\n" + "=" * 50)
        print("🧠 情感分析...")
        print("=" * 50)
        analyzed = sentiment_analyzer.analyze_articles(articles[:10])
        for article in analyzed[:5]:
            sentiment = article.get('sentiment', {})
            print(f"[{sentiment.get('sentiment', 'unknown')}] {article['title'][:50]}...")
    
    print("\n✅ 完成！")

if __name__ == '__main__':
    main()
