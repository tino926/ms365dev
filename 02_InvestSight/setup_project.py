#!/usr/bin/env python3
"""
InvestSight 項目初始化腳本
執行後會自動創建所有目錄和文件
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# 目錄結構
DIRS = [
    'config', 'data', 'analysis', 'storage', 'report', 
    'notification', 'scripts', 'tests', 'logs'
]

# 文件內容
FILES = {
    'README.md': '''# InvestSight 📈

金融新聞匯整與投資分析系統

## 功能特色

- 📊 **金融數據抓取** - Yahoo Finance, Alpha Vantage
- 📰 **財經新聞聚合** - RSS, API 整合
- 🧠 **情感分析** - Azure Cognitive Services
- 💼 **投資組合追蹤** - Excel Online 整合
- 📈 **Power BI 儀表板** - 可視化分析
- 📧 **自動郵件報告** - 定期推送
- 💬 **Teams 通知** - 即時警報

## 快速開始

### 1. 環境設置

```bash
# 複製環境變數範例
cp .env.example .env

# 編輯 .env 填寫 API 密鑰
nano .env

# 安裝依賴
pip install -r requirements.txt
```

### 2. 配置 Microsoft 365

在 `.env` 中填寫：
```bash
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
```

### 3. 運行腳本

```bash
# 抓取數據
python scripts/fetch_data.py

# 分析數據
python scripts/analyze.py

# 生成報告
python scripts/generate_report.py
```

## Microsoft 365

本項目用於實際開發活動，學習 Microsoft 365 整合開發。
''',

    'requirements.txt': '''# Microsoft Graph SDK
msgraph-sdk==1.0.0
azure-identity==1.15.0

# 金融數據
yfinance==0.2.31
alpha-vantage==2.3.1

# 新聞數據
feedparser==6.0.10

# 數據處理
pandas==2.1.4
numpy==1.26.2

# 情感分析
textblob==0.17.1

# Excel 處理
openpyxl==3.1.2

# 環境變數
python-dotenv==1.0.0

# 日誌
colorlog==6.8.0

# HTTP 請求
requests==2.31.0

# 測試
pytest==7.4.3
''',

    '.env.example': '''# Microsoft 365
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret

# 金融數據 API
ALPHA_VANTAGE_KEY=your-api-key
YAHOO_FINANCE_ENABLED=true

# 新聞 API
RSS_FEEDS=https://finance.yahoo.com/news/rssindex

# 開發環境
ENVIRONMENT=development
DEBUG=true
''',

    '.gitignore': '''# Python
__pycache__/
*.py[cod]
.env
*.log
data/*.csv
data/*.json
*.xlsx
.DS_Store
''',

    'config/__init__.py': '',
    
    'config/settings.py': '''"""
InvestSight 配置設定
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Microsoft 365
TENANT_ID = os.getenv('TENANT_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# 金融數據
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY')
YAHOO_FINANCE_ENABLED = os.getenv('YAHOO_FINANCE_ENABLED', 'true').lower() == 'true'

# 新聞
RSS_FEEDS = os.getenv('RSS_FEEDS', '').split(',')

# 默認追蹤股票
DEFAULT_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

# 默認新聞關鍵詞
DEFAULT_KEYWORDS = ['Apple', 'Microsoft', 'AI', 'tech', 'stock market']
''',

    'data/__init__.py': '',
    
    'data/finance_api.py': '''"""
金融數據抓取模塊
"""
import yfinance as yf
from datetime import datetime
from typing import List, Dict, Optional

class FinanceDataFetcher:
    """金融數據抓取器"""
    
    def __init__(self):
        from ..config.settings import DEFAULT_STOCKS
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
''',

    'data/news_api.py': '''"""
新聞抓取模塊
"""
import feedparser
from datetime import datetime
from typing import List, Dict

class NewsFetcher:
    """新聞抓取器"""
    
    def __init__(self):
        from ..config.settings import RSS_FEEDS
        self.rss_feeds = RSS_FEEDS
    
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
''',

    'analysis/__init__.py': '',
    
    'analysis/sentiment.py': '''"""
情感分析模塊
"""
from textblob import TextBlob
from typing import List, Dict

class SentimentAnalyzer:
    """情感分析器"""
    
    def analyze_text(self, text: str) -> Dict:
        """分析文本情感"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            return {
                'polarity': polarity,
                'sentiment': sentiment,
            }
        except Exception as e:
            print(f"情感分析失敗：{e}")
            return {'polarity': 0, 'sentiment': 'neutral'}
    
    def analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """分析多篇新聞"""
        for article in articles:
            text = f"{article['title']} {article.get('summary', '')}"
            article['sentiment'] = self.analyze_text(text)
        return articles

analyzer = SentimentAnalyzer()
''',

    'storage/__init__.py': '',
    'report/__init__.py': '',
    'notification/__init__.py': '',
    'scripts/__init__.py': '',
    'tests/__init__.py': '',
    'logs/.gitkeep': '',

    'scripts/fetch_data.py': '''#!/usr/bin/env python3
"""
數據抓取腳本
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.finance_api import fetcher as finance_fetcher
from data.news_api import fetcher as news_fetcher

def main():
    print("=" * 50)
    print("📊 抓取金融數據...")
    print("=" * 50)
    stocks = finance_fetcher.fetch_all_stocks()
    for stock in stocks:
        print(f"{stock['symbol']}: ${stock['price']} ({stock['change_percent']:+.2f}%)")
    
    print("\\n" + "=" * 50)
    print("📰 抓取新聞...")
    print("=" * 50)
    articles = news_fetcher.fetch_all()
    for article in articles[:5]:
        print(f"[{article['source']}] {article['title']}")
    
    print("\\n✅ 完成！")

if __name__ == '__main__':
    main()
''',
}

def create_project():
    """創建項目結構"""
    print("🚀 開始設置 InvestSight 項目...")
    
    # 創建目錄
    print("\\n📁 創建目錄結構...")
    for dir_name in DIRS:
        dir_path = BASE_DIR / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_name}/")
    
    # 創建文件
    print("\\n📄 創建文件...")
    for file_path, content in FILES.items():
        full_path = BASE_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ {file_path}")
    
    print("\\n✅ 項目設置完成！")
    print("\\n📂 項目位置：當前目錄")
    print("\\n下一步：")
    print("1. cd 02_InvestSight")
    print("2. cp .env.example .env  # 編輯填寫 API 密鑰")
    print("3. pip install -r requirements.txt")
    print("4. python scripts/fetch_data.py")

if __name__ == '__main__':
    create_project()
