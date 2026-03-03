#!/usr/bin/env python3
"""
數據抓取腳本
"""
import sys
import os
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)
os.chdir(project_root)

from dotenv import load_dotenv
load_dotenv()

from data.finance_api import fetcher as finance_fetcher
from data.news_api import fetcher as news_fetcher
from analysis.sentiment import analyzer as sentiment_analyzer


def fetch_and_notify(send_email_flag: bool = False, recipient: str = ""):
    """抓取數據並可選發送郵件通知"""
    results = {
        'stocks': [],
        'articles': [],
        'summary': ''
    }
    
    print("=" * 50)
    print("📊 抓取金融數據...")
    print("=" * 50)
    stocks = finance_fetcher.fetch_all_stocks()
    for stock in stocks:
        print(f"{stock['symbol']}: ${stock['price']} ({stock['change_percent']:+.2f}%)")
    results['stocks'] = stocks
    
    print("\n" + "=" * 50)
    print("📰 抓取新聞...")
    print("=" * 50)
    articles = news_fetcher.fetch_all()
    print(f"抓取到 {len(articles)} 篇新聞")
    
    if articles:
        print("\n" + "=" * 50)
        print("🧠 情感分析...")
        print("=" * 50)
        analyzed = sentiment_analyzer.analyze_articles(articles[:10])
        for article in analyzed[:5]:
            sentiment = article.get('sentiment', {})
            print(f"[{sentiment.get('sentiment', 'unknown')}] {article['title'][:50]}...")
        results['articles'] = analyzed
    
    total_change = sum(s.get('change_percent', 0) for s in stocks if s.get('change_percent'))
    avg_change = total_change / len(stocks) if stocks else 0
    results['summary'] = f"今日投資組合平均漲跌幅: {avg_change:+.2f}%"
    
    if send_email_flag and recipient:
        try:
            from notification import send_daily_report
            success = send_daily_report(recipient, stocks, results['summary'])
            if success:
                print(f"\n✅ 郵件已發送到: {recipient}")
            else:
                print(f"\n⚠️ 郵件發送失敗")
        except Exception as e:
            print(f"\n⚠️ 郵件發送錯誤: {e}")
    
    print("\n✅ 完成！")
    return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='InvestSight 數據抓取')
    parser.add_argument('--email', '-e', type=str, default='', 
                        help='發送郵件通知到指定地址')
    parser.add_argument('--smtp', '-s', action='store_true',
                        help='使用 SMTP 發送郵件（預設使用 Graph API）')
    
    args = parser.parse_args()
    
    send_email = bool(args.email)
    recipient = args.email
    
    fetch_and_notify(send_email, recipient)


if __name__ == '__main__':
    main()
