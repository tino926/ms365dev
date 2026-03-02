"""
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
