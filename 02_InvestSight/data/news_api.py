"""
新聞抓取模塊
支持：RSS Feeds
"""
import feedparser
from datetime import datetime
from typing import List, Dict

# 默認新聞源
DEFAULT_RSS_FEEDS = ['https://finance.yahoo.com/news/rssindex']

class NewsFetcher:
    """新聞抓取器"""

    def __init__(self):
        import os
        self.rss_feeds = os.getenv('RSS_FEEDS', '').split(',')
        if not self.rss_feeds or self.rss_feeds == ['']:
            self.rss_feeds = DEFAULT_RSS_FEEDS
    
    def fetch_rss(self, url: str, limit: int = 10) -> List[Dict]:
        """抓取 RSS 新聞"""
        try:
            feed = feedparser.parse(url)
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', datetime.now().isoformat()),
                    'source': feed.feed.get('title', 'Unknown'),
                    'summary': entry.get('summary', '')[:500],
                })
            return articles
        except Exception as e:
            print(f"抓取 RSS {url} 失敗：{e}")
            return []
    
    def fetch_all(self) -> List[Dict]:
        """抓取所有新聞源"""
        all_articles = []
        for feed_url in self.rss_feeds:
            if feed_url:
                articles = self.fetch_rss(feed_url)
                all_articles.extend(articles)
        return all_articles

fetcher = NewsFetcher()

if __name__ == '__main__':
    articles = fetcher.fetch_all()
    for article in articles[:5]:
        print(f"[{article['source']}] {article['title']}")
