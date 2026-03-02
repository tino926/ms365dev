# InvestSight 開發筆記

**最後更新：** 2026-02-23

---

## 📋 項目概述

InvestSight 是一個**金融新聞匯整與投資分析系統**。

**主要目標：**
1. 金融數據抓取與分析
2. 新聞情感分析
3. 投資組合追蹤
4. 自動報告生成

---

## ✅ 已完成的功能

### 核心模塊
| 模塊 | 文件 | 狀態 |
|------|------|------|
| 配置管理 | `config/settings.py` | ✅ 完成 |
| 金融數據抓取 | `data/finance_api.py` | ✅ 完成 |
| 新聞抓取 | `data/news_api.py` | ✅ 完成 |
| 情感分析 | `analysis/sentiment.py` | ✅ 完成 |
| 主腳本 | `scripts/fetch_data.py` | ✅ 完成 |

### 測試狀態
```bash
# 已測試功能
python scripts/fetch_data.py  # 可以抓取股價和新聞
```

---

## 📅 下一步開發計劃

### 階段 1：Microsoft Graph API 整合（優先）
- [ ] 配置 Azure AD 應用
- [ ] 實現 OneDrive 文件存儲
- [ ] 實現 Outlook 郵件發送
- [ ] 實現 Teams 通知

### 階段 2：數據存儲
- [ ] Excel Online 投資組合追蹤
- [ ] SharePoint 新聞存檔
- [ ] 本地 SQLite 緩存

### 階段 3：報告與可視化
- [ ] Power BI 儀表板
- [ ] 自動郵件報告（每週）
- [ ] Teams 即時警報

### 階段 4：進階功能
- [ ] Azure Cognitive Services 情感分析
- [ ] 投資建議生成
- [ ] 自動化工作流（Power Automate）

---

## 🔧 環境配置

### .env 文件位置
```
02_InvestSight/.env
```

### 必要配置
```bash
# Microsoft 365（階段 1 需要）
TENANT_ID=your-tenant-id
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret

# 金融數據 API（免費）
ALPHA_VANTAGE_KEY=your-api-key  # 免費註冊取得
YAHOO_FINANCE_ENABLED=true

# 新聞 API（免費 RSS）
RSS_FEEDS=https://finance.yahoo.com/news/rssindex
```

### 安裝依賴
```bash
cd 02_InvestSight
pip install -r requirements.txt
```

---

## 📂 目錄結構

```
InvestSight/
├── config/
│   ├── __init__.py
│   └── settings.py          # 配置管理
├── data/
│   ├── __init__.py
│   ├── finance_api.py       # 金融數據抓取
│   └── news_api.py          # 新聞抓取
├── analysis/
│   ├── __init__.py
│   └── sentiment.py         # 情感分析
├── storage/                 # TODO: 存儲模塊
├── report/                  # TODO: 報告模塊
├── notification/            # TODO: 通知模塊
├── scripts/
│   ├── __init__.py
│   └── fetch_data.py        # 主腳本
├── tests/
├── logs/
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🚀 快速開始命令

```bash
# 1. 進入項目
cd 02_InvestSight

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 配置環境
cp .env.example .env
nano .env  # 編輯配置

# 4. 測試運行
python scripts/fetch_data.py

# 5. 查看結果
ls -la data/  # 查看抓取的數據
```

---

## 💡 開發提示

### 免費 API 推薦
1. **Yahoo Finance** - 股價數據（無需 API Key）
2. **Alpha Vantage** - 股價數據（免費 500 次/天）
3. **RSS Feeds** - 新聞（免費）

### Microsoft 365 整合活動
- ✅ Graph API 調用
- ✅ OneDrive 文件操作
- ✅ Outlook 郵件發送
- ✅ Teams 消息發送
- ✅ Power BI 報表創建
- ✅ Power Automate 流程

### 建議開發順序
1. 先測試免費 API（Yahoo Finance + RSS）
2. 配置 Microsoft Graph API
3. 實現基本存儲（Excel Online）
4. 添加通知功能（Email/Teams）
5. 進階分析（Azure Cognitive Services）

---

## 📝 待辦事項清單

### 立即要做
- [ ] 安裝依賴並測試
- [ ] 配置 .env 文件
- [ ] 測試 Yahoo Finance API
- [ ] 測試 RSS 新聞抓取

### 短期（1-2 週）
- [ ] Microsoft Graph API 整合
- [ ] Excel Online 存儲
- [ ] 郵件報告功能

### 中期（1 個月）
- [ ] Power BI 儀表板
- [ ] Teams 通知
- [ ] 自動化工作流

### 長期（2-3 個月）
- [ ] Azure Cognitive Services
- [ ] 投資建議生成
- [ ] 完整自動化系統

---

## 🔗 相關資源

- [Microsoft Graph API 文檔](https://learn.microsoft.com/en-us/graph/)
- [Yahoo Finance API](https://pypi.org/project/yfinance/)
- [Alpha Vantage API](https://www.alphavantage.co/)
- [Microsoft 365 Developer Program](https://developer.microsoft.com/en-us/microsoft-365/dev-program)

---

## 📞 需要幫助時

告訴新的 AI：
1. 「查看 DEVELOPER_NOTE.md 了解項目狀態」
2. 「繼續開發 [具體功能]」
3. 「參考 requirements.txt 安裝依賴」

---

**項目口號：** 實際開發，有效學習！ 🚀
