#!/usr/bin/env python3
"""
InvestSight 功能展示腳本
展示所有可用功能
"""
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)


def show_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_stock_prices():
    """展示 1: 股價抓取"""
    show_header("📊 功能展示 1: Yahoo Finance 股價抓取")
    
    from data.finance_api import fetcher as finance_fetcher
    
    print("\n抓取追蹤股票的即時股價：")
    stocks = finance_fetcher.fetch_all_stocks()
    
    for stock in stocks:
        price = stock.get('price', 'N/A')
        change = stock.get('change_percent', 0)
        symbol = stock['symbol']
        
        if isinstance(price, (int, float)):
            price_str = f"${price:.2f}"
        else:
            price_str = str(price)
        
        arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"  {arrow} {symbol}: {price_str} ({change:+.2f}%)")
    
    print(f"\n✅ 成功抓取 {len(stocks)} 支股票價格")


def demo_news_fetch():
    """展示 2: 新聞抓取"""
    show_header("📰 功能展示 2: RSS 新聞抓取")
    
    from data.news_api import fetcher as news_fetcher
    
    print("\n抓取最新財經新聞：")
    articles = news_fetcher.fetch_all()
    
    for i, article in enumerate(articles[:5], 1):
        title = article.get('title', '無標題')[:60]
        source = article.get('source', '未知來源')
        print(f"  {i}. [{source}] {title}...")
    
    print(f"\n✅ 成功抓取 {len(articles)} 篇新聞")


def demo_sentiment_analysis():
    """展示 3: 情感分析"""
    show_header("🧠 功能展示 3: 新聞情感分析")
    
    from data.news_api import fetcher as news_fetcher
    from analysis.sentiment import analyzer as sentiment_analyzer
    
    print("\n分析新聞情感（正面/負面/中性）：")
    articles = news_fetcher.fetch_all()
    
    if articles:
        analyzed = sentiment_analyzer.analyze_articles(articles[:10])
        
        sentiment_count = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in analyzed[:5]:
            sentiment = article.get('sentiment', {})
            sentiment_label = sentiment.get('sentiment', 'unknown')
            polarity = sentiment.get('polarity', 0)
            
            emoji = "😊" if sentiment_label == 'positive' else "😢" if sentiment_label == 'negative' else "😐"
            title = article.get('title', '無標題')[:50]
            
            # 確保 polarity 是數字
            if isinstance(polarity, (int, float)):
                print(f"  {emoji} [{sentiment_label} {polarity:+.2f}] {title}...")
            else:
                print(f"  {emoji} [{sentiment_label}] {title}...")
            sentiment_count[sentiment_label] = sentiment_count.get(sentiment_label, 0) + 1
        
        print(f"\n✅ 情感分佈：正面={sentiment_count['positive']}, 負面={sentiment_count['negative']}, 中性={sentiment_count['neutral']}")


def demo_user_info():
    """展示 4: Microsoft 365 用戶資訊"""
    show_header("👤 功能展示 4: Microsoft 365 用戶資訊")
    
    from storage.graph_api import get_graph_client
    import asyncio
    
    client = get_graph_client()
    
    if not client.authenticate(use_cache=True):
        print("\n⚠️ 無法認證，跳過此展示")
        return
    
    async def get_info():
        user = await client.get_user_profile()
        if user:
            print(f"\n  用戶：{user['display_name']}")
            print(f"  Email: {user['email']}")
            print(f"  ID: {user['user_id']}")
            print("\n✅ 成功獲取 Microsoft 365 用戶資訊")
        else:
            print("\n⚠️ 無法獲取用戶資訊")
    
    try:
        asyncio.run(get_info())
    except Exception as e:
        print(f"\n⚠️ 錯誤：{e}")


def demo_email_list():
    """展示 5: Outlook 郵件列表"""
    show_header("📧 功能展示 5: Outlook 收件匣郵件")
    
    from storage.graph_api import get_graph_client
    import asyncio
    
    client = get_graph_client()
    
    if not client.authenticate(use_cache=True):
        print("\n⚠️ 無法認證，跳過此展示")
        return
    
    async def get_emails():
        messages = await client.list_inbox_messages(top=5)
        if messages:
            print("\n最新 5 封郵件：")
            for i, msg in enumerate(messages, 1):
                status = "✓" if msg['is_read'] else "📭"
                subject = msg['subject'][:50]
                from_who = msg['from']
                received = msg['received']
                print(f"  {i}. {status} {subject}...")
                print(f"     從：{from_who} | 時間：{received}")
            print("\n✅ 成功獲取郵件列表")
        else:
            print("\n⚠️ 收件匣为空或無法獲取郵件")
    
    try:
        asyncio.run(get_emails())
    except Exception as e:
        print(f"\n⚠️ 錯誤：{e}")


def main():
    show_header("🚀 InvestSight 功能展示")
    
    print("\n本展示將展示以下功能：")
    print("  1. Yahoo Finance 股價抓取")
    print("  2. RSS 新聞抓取")
    print("  3. 新聞情感分析")
    print("  4. Microsoft 365 用戶資訊")
    print("  5. Outlook 收件匣郵件")
    
    input("\n按 Enter 開始展示...")
    
    # 功能 1: 股價抓取
    demo_stock_prices()
    
    # 功能 2: 新聞抓取
    demo_news_fetch()
    
    # 功能 3: 情感分析
    demo_sentiment_analysis()
    
    # 功能 4: 用戶資訊
    demo_user_info()
    
    # 功能 5: 郵件列表
    demo_email_list()
    
    show_header("✅ 展示完成")
    print("\n所有功能展示完畢！\n")


if __name__ == '__main__':
    main()
