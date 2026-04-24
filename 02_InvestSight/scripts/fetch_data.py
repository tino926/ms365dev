#!/usr/bin/env python3
"""
InvestSight 數據抓取腳本
"""
import sys
import os
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)
os.chdir(project_root)

from dotenv import load_dotenv
load_dotenv()

import argparse
from data.finance_api import FinanceDataFetcher
from data.news_api import NewsFetcher
from analysis.sentiment import analyzer as sentiment_analyzer
from config.settings import DEFAULT_STOCKS, RSS_FEEDS


def fetch_stocks(symbols: list = None):
    """抓取股票數據"""
    print("\n" + "=" * 50)
    print("📊 抓取金融數據...")
    print("=" * 50)
    
    fetcher = FinanceDataFetcher()
    if symbols:
        fetcher.stocks = symbols
    
    stocks = fetcher.fetch_all_stocks()
    
    for stock in stocks:
        change = stock.get('change_percent', 0)
        icon = '🟢' if change >= 0 else '🔴'
        print(f"{icon} {stock['symbol']:6} ${stock['price']:8.2f} ({change:+6.2f}%)")
    
    print(f"\n✅ 成功抓取 {len(stocks)} 支股票")
    return stocks


def fetch_news(sources: list = None):
    """抓取新聞數據"""
    print("\n" + "=" * 50)
    print("📰 抓取新聞...")
    print("=" * 50)
    
    fetcher = NewsFetcher()
    if sources:
        fetcher.rss_feeds = sources
    
    articles = fetcher.fetch_all()
    
    print(f"✅ 成功抓取 {len(articles)} 篇新聞")
    return articles


def analyze_sentiment(articles: list):
    """情感分析"""
    print("\n" + "=" * 50)
    print("🧠 情感分析...")
    print("=" * 50)
    
    analyzed = sentiment_analyzer.analyze_articles(articles[:10])
    
    positive = sum(1 for a in analyzed if a.get('sentiment', {}).get('sentiment') == 'positive')
    negative = sum(1 for a in analyzed if a.get('sentiment', {}).get('sentiment') == 'negative')
    neutral = len(analyzed) - positive - negative
    
    for article in analyzed[:5]:
        sent = article.get('sentiment', {})
        icon = '🟢' if sent.get('sentiment') == 'positive' else '🔴' if sent.get('sentiment') == 'negative' else '⚪'
        print(f"{icon} [{sent.get('sentiment', 'unknown'):8}] {article.get('title', '')[:50]}...")
    
    print(f"\n📊 統計: 🟢正面:{positive} | 🔴負面:{negative} | ⚪中性:{neutral}")
    return analyzed


def main():
    parser = argparse.ArgumentParser(
        description='InvestSight 數據抓取',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 抓取所有數據
  python scripts/fetch_data.py

  # 只抓取股票
  python scripts/fetch_data.py --stocks

  # 只抓取新聞
  python scripts/fetch_data.py --news

  # 抓取指定股票
  python scripts/fetch_data.py --stocks AAPL MSFT GOOGL

  # 抓取股票並發送郵件
  python scripts/fetch_data.py --stocks --email your@email.com
        """
    )
    
    parser.add_argument('--stocks', '-s', nargs='*', 
                        help='抓取股票數據，可指定股票代碼（如: AAPL MSFT GOOGL）')
    parser.add_argument('--news', '-n', action='store_true',
                        help='抓取新聞數據')
    parser.add_argument('--all', '-a', action='store_true',
                        help='抓取所有數據（股票+新聞+情感分析）')
    parser.add_argument('--email', '-e', type=str, default='',
                        help='發送郵件通知到指定地址')
    parser.add_argument('--config', '-c', type=str, default='',
                        help='使用自定義配置文件')
    
    args = parser.parse_args()
    
    # 預設：抓取所有數據
    fetch_all = not any([args.stocks, args.news])
    
    results = {
        'stocks': [],
        'articles': [],
        'summary': ''
    }
    
    # 股票
    if args.stocks is not None or fetch_all:
        symbols = args.stocks if args.stocks else DEFAULT_STOCKS
        results['stocks'] = fetch_stocks(symbols)
    
    # 新聞
    if args.news or fetch_all:
        results['articles'] = fetch_news()
    
    # 情感分析
    if results['articles']:
        analyze_sentiment(results['articles'])
    
    # 發送郵件
    if args.email and results['stocks']:
        try:
            from notification import send_daily_report
            total_change = sum(s.get('change_percent', 0) for s in results['stocks']) / len(results['stocks'])
            summary = f"今日投資組合平均漲跌幅: {total_change:+.2f}%"
            send_daily_report(args.email, results['stocks'], summary)
            print(f"\n✅ 郵件已發送到: {args.email}")
        except Exception as e:
            print(f"\n⚠️ 郵件發送失敗: {e}")
    
    print("\n✅ 完成！")


if __name__ == '__main__':
    main()
