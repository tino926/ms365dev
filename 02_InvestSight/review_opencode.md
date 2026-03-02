# InvestSight 程式碼審查報告

> 審查日期: 2026-03-02
> 審查範圍: 02_InvestSight/

---

## 總體評估

| 項目 | 評分 | 說明 |
|------|------|------|
| 程式碼結構 | ⭐⭐⭐⭐ | 模組化設計良好 |
| 錯誤處理 | ⭐⭐⭐ | 基本覆蓋，可改進 |
| 安全性 | ⭐⭐⭐ | 需注意敏感資訊處理 |
| 文件完整性 | ⭐⭐⭐⭐ | 結構完整，部分模組空置 |

---

## 🔴 嚴重問題

### 1. storage/graph_api.py - 未定義的屬性存取

**位置**: `storage/graph_api.py:143-144`

```python
self.device_code_credential.token = tokens.get('access_token')
self.logger.info(f"Loaded access token: {self.device_code_credential.token}")
```

**問題**: `self.logger` 未定義，會導致 `AttributeError`。

**建議修復**:
```python
# 移除 logger 引用或添加
import logging
self.logger = logging.getLogger(__name__)
```

---

### 2. storage/graph_api.py - Token 驗證過於簡單

**位置**: `storage/graph_api.py:53-58`

```python
def _token_is_valid(self) -> bool:
    if not self._token_cache.get('access_token'):
        return False
    return True
```

**問題**: 
- 只檢查 token 是否存在，無過期時間驗證
- JWT token 有 `exp` 宣告但未解析驗證

**建議修復**:
```python
import time

def _token_is_valid(self) -> bool:
    token = self._token_cache.get('access_token')
    if not token:
        return False
    
    # 解析 JWT 驗證過期時間
    try:
        payload = token.split('.')[1]
        # Base64 URL decode and parse
        import base64, json
        padded = payload + '=' * (4 - len(payload) % 4)
        exp = json.loads(base64.urlsafe_b64decode(padded)).get('exp', 0)
        return time.time() < exp
    except:
        return False
```

---

### 3. config/settings.py - 環境變數無驗證

**位置**: `config/settings.py:13-15`

```python
TENANT_ID = os.getenv('TENANT_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
```

**問題**: 環境變數為 `None` 時可能導致後續程式崩潰，無明確錯誤訊息。

**建議修復**:
```python
TENANT_ID = os.getenv('TENANT_ID')
if not TENANT_ID:
    raise ValueError("TENANT_ID is required")
```

---

### 4. 依賴版本過舊

**位置**: `setup_project.py:76`

```python
msgraph-sdk==1.0.0
```

**問題**: 根據 `01_python_ms_graph/graph.py:53-54` 註解，SDK 存在相容性問題需回退到 `1.2.0`。

---

## 🟡 中等問題

### 5. 模組級別的全域實例

**位置**: 多個模組

- `data/finance_api.py:41`
- `data/news_api.py:43`
- `analysis/sentiment.py:40`

```python
fetcher = FinanceDataFetcher()  # 模組級別
```

**問題**: 
- 測試困難
- 狀態共享可能造成非預期行為
- 配置固定，彈性不足

**建議**: 改用工廠函數或依賴注入。

---

### 6. 異常處理過於廣泛

**位置**: 多處

```python
except Exception as e:
    print(f"獲取 {symbol} 股價失敗：{e}")
    return None
```

**問題**: 
- 吞掉所有異常，難以Debug
- 不區分可恢復與不可恢復錯誤

**建議**: 針對特定異常處理，或記錄詳細日誌。

---

### 7. 未完成的模組

**位置**: 
- `notification/__init__.py` - 空模組
- `report/__init__.py` - 空模組

**問題**: 功能不完整，README 描述的功能未實作。

---

### 8. 缺少統一的 Graph API 封裝

**問題**: 
- `01_python_ms_graph/graph.py` 與 `02_InvestSight/storage/graph_api.py` 功能高度重複
- 代碼維護困難

**建議**: 提取共同邏輯到共享模組。

---

## 🟢 良好實踐

### 9. 值得肯定之處

| 項目 | 說明 |
|------|------|
| 類型提示 | 廣泛使用 `typing` 模組 |
| 異步編程 | 正確使用 `async/await` |
| 配置管理 | 使用 `.env` 隔離敏感資訊 |
| 專案結構 | 清晰的目錄結構與模組劃分 |
| 依賴管理 | `requirements.txt` 完整 |

---

## 📋 優先修復清單

| 優先級 | 問題 | 檔案 |
|--------|------|------|
| P0 | `self.logger` 未定義 | storage/graph_api.py |
| P0 | Token 驗證缺失 | storage/graph_api.py |
| P1 | 環境變數驗證 | config/settings.py |
| P1 | SDK 版本更新 | setup_project.py |
| P2 | 全域實例重構 | 各模組 |
| P2 | 完成空模組 | notification/, report/ |
| P3 | 重構 Graph API | 跨目錄 |

---

## 測試建議

```bash
# 建議添加測試
pip install pytest pytest-asyncio

# 執行現有測試
pytest tests/
```

---

*報告結束*
