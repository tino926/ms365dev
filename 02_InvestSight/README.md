# InvestSight 📈

金融新聞匯整與投資分析系統

[![Status](https://img.shields.io/badge/status-stable-green)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## 📊 功能特色

### 核心功能
- 📊 **金融數據抓取** - Yahoo Finance 即時股價
- 📰 **財經新聞聚合** - RSS Feed 新聞抓取
- 🧠 **情感分析** - TextBlob 新聞情感分析（正面/負面/中性）
- 📈 **技術指標分析** - 7 種技術指標（RSI, MACD, MA, EMA, 布林帶，KD, ATR）
- 💡 **投資建議生成** - AI 投資顧問（買入/賣出/持有）

### Microsoft 365 整合
- 📧 **自動郵件報告** - Outlook 郵件發送（Graph API / SMTP）
- 💬 **Teams 通知** - 即時股價警報
- 📁 **雲端存儲** - OneDrive 文件備份
- 📊 **Excel Online** - 投資組合追蹤

### 新功能（v1.1）⭐
- 🚨 **股價警報** - 設定閾值自動通知
- 💼 **投資組合追蹤** - 記錄持股、計算損益
- 📊 **真實數據獲取** - yfinance 歷史數據

---

## 🚀 快速開始

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 配置環境
```bash
cp .env.example .env
nano .env  # 填寫 API 密鑰
```

### 3. 運行
```bash
# 基本抓取（股價 + 新聞 + 情感分析）
python scripts/fetch_data.py

# 進階投資分析（推薦）⭐
python scripts/analyze_stocks.py

# 投資組合追蹤
python scripts/portfolio_tracker.py

# 股價警報
python scripts/price_alert.py

# E5 續期
python scripts/daily_graph_call.py
```

---

## 📁 項目結構

```
02_InvestSight/
├── config/                  # 配置模塊
│   └── settings.py         # 環境變數配置
├── data/                    # 數據抓取
│   ├── finance_api.py      # Yahoo Finance 股價
│   ├── news_api.py         # RSS 新聞
│   └── historical_data.py  # 歷史數據（新增）⭐
├── analysis/                # 分析模塊
│   ├── sentiment.py        # 情感分析
│   ├── technical_indicators.py  # 技術指標（7 種）
│   └── investment_advisor.py    # 投資建議
├── storage/                 # 存儲模塊
│   ├── graph_api.py        # Graph API (Device Code)
│   ├── graph_client_secret.py  # Graph API (Client Secret)
│   ├── excel_online.py     # Excel Online
│   └── onedrive.py         # OneDrive
├── notification/            # 通知模塊
│   ├── email.py            # 郵件通知
│   └── teams.py            # Teams 通知
├── scripts/                 # 功能腳本
│   ├── fetch_data.py       # 基本數據抓取
│   ├── analyze_stocks.py   # 進階投資分析
│   ├── portfolio_tracker.py # 投資組合追蹤 ⭐
│   ├── price_alert.py      # 股價警報 ⭐
│   ├── daily_graph_call.py # E5 續期
│   └── test_new_features.py # 功能測試
├── report/                  # 報告模塊
├── tests/                   # 測試模塊
├── .env                     # 環境變數（不提交）
├── .env.example             # 環境變數範例
├── requirements.txt         # 依賴配置
├── README.md                # 本文件
└── DEVELOPER_NOTE.md        # 開發筆記
```

---

## 🛠️ 使用範例

### 投資分析
```python
from scripts.analyze_stocks import main
main()  # 執行完整投資分析
```

### 投資組合追蹤
```python
from scripts.portfolio_tracker import Portfolio

portfolio = Portfolio()
portfolio.add_holding('AAPL', 10, 150.0)  # 添加持股
portfolio.add_holding('MSFT', 5, 350.0)

report = portfolio.generate_report()  # 生成報告
print(report)
```

### 股價警報
```python
from scripts.price_alert import AlertManager

manager = AlertManager()
manager.add_alert('AAPL', 'above', 270)  # 股價超過 $270 時警報
manager.add_alert('MSFT', 'below', 390)  # 股價低於 $390 時警報

manager.check_all()  # 檢查是否觸發
```

### 技術指標分析
```python
from analysis.technical_indicators import TechnicalIndicators

indicators = TechnicalIndicators()
prices = [100, 102, 101, 103, 105, ...]  # 股價數據

ma = indicators.calculate_ma(prices, 20)  # 20 日移動平均
rsi = indicators.calculate_rsi(prices, 14)  # RSI
macd = indicators.calculate_macd(prices)  # MACD
```

---

## ⚙️ 環境變數

```bash
# Microsoft 365 (Client Secret 認證)
AZURE_CLIENT_ID=your-client-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_GRAPH_SCOPES=.default

# Microsoft 365 (Device Code 認證 - 可選)
AZURE_DEVICE_CLIENT_ID=your-device-client-id
AZURE_DEVICE_TENANT_ID=your-device-tenant-id

# 金融數據
ALPHA_VANTAGE_KEY=your-api-key
YAHOO_FINANCE_ENABLED=true
RSS_FEEDS=https://finance.yahoo.com/news/rssindex

# 郵件通知（可選）
USE_GRAPH_EMAIL=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password

# Excel / OneDrive（可選）
EXCEL_FILE_PATH=InvestSight/Portfolio.xlsx
ONEDRIVE_BASE_PATH=InvestSight
```

---

## 📊 已實現功能

| 功能 | 狀態 | 說明 |
|------|------|------|
| 股價抓取 | ✅ | Yahoo Finance API |
| 新聞抓取 | ✅ | RSS Feed |
| 情感分析 | ✅ | TextBlob |
| 技術指標 | ✅ | 7 種指標 |
| 投資建議 | ✅ | AI 生成 |
| Graph API | ✅ | 雙認證模式 |
| 郵件通知 | ✅ | SMTP + Graph |
| Teams 通知 | ✅ | Graph API |
| Excel Online | ✅ | Graph API |
| OneDrive | ✅ | Graph API |
| 股價警報 | ✅ | 新增 ⭐ |
| 投資組合 | ✅ | 新增 ⭐ |

---

## 📚 文檔

- [STATUS_REPORT.md](docs/STATUS_REPORT.md) - 現狀分析報告
- [DEVELOPER_NOTE.md](DEVELOPER_NOTE.md) - 開發筆記
- [HANDOVER.md](openspec/HANDOVER.md) - 交接筆記

---

## ⚠️ 免責聲明

**本項目僅供學習和研究使用，不構成任何投資建議。**

- 所有數據僅供參考，不保證準確性
- 投資有風險，入市需謹慎
- 請自行判斷並承擔投資風險

---

## 📄 License

MIT License

---

## 🙏 致謝

- [Yahoo Finance](https://finance.yahoo.com/) - 股價數據
- [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/) - Microsoft 365 整合
- [OpenSpec](https://github.com/fissionlabsio/openspec) - 規範驅動開發

---

**InvestSight** - 讓投資更智能！ 🚀
