# InvestSight 📈

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
python scripts/fetch_data.py
```
