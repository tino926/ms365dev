"""
Excel Online 投資組合模組
通過 Microsoft Graph API 讀寫 OneDrive/SharePoint 上的 Excel 文件
"""
import os
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ExcelOnlineClient:
    """Excel Online 客戶端"""
    
    def __init__(self, graph_client=None):
        self.graph_client = graph_client
        self.file_path = os.getenv('EXCEL_FILE_PATH', 'InvestSight/Portfolio.xlsx')
        self.worksheet_name = os.getenv('EXCEL_WORKSHEET', 'Portfolio')
    
    def _ensure_client(self):
        """確保 Graph 客戶端已初始化"""
        if not self.graph_client:
            from storage.graph_api import get_graph_client
            self.graph_client = get_graph_client()
            self.graph_client.authenticate(use_cache=True)
    
    async def get_or_create_file(self) -> Optional[str]:
        """獲取或創建 Excel 文件"""
        self._ensure_client()
        
        try:
            from msgraph.generated.models.workbook import Workbook
            from msgraph.generated.models.workbook_application import WorkbookApplication
            
            file_id = await self._find_file()
            if file_id:
                print(f"✓ 找到現有文件: {self.file_path}")
                return file_id
            
            print("⚠️ Excel 文件不存在，請先在 OneDrive 創建")
            return None
            
        except Exception as e:
            print(f"✗ 獲取文件失敗: {e}")
            return None
    
    async def _find_file(self) -> Optional[str]:
        """查找文件並返回 ID"""
        try:
            result = await self.graph_client.me.drive.root.children.get()
            if result and result.value:
                for item in result.value:
                    if item.name == Path(self.file_path).name:
                        return item.id
            return None
        except Exception as e:
            print(f"✗ 搜索文件失敗: {e}")
            return None
    
    async def read_worksheet(self, file_id: str) -> List[Dict]:
        """讀取工作表數據"""
        self._ensure_client()
        
        try:
            from msgraph.generated.models.o_data_errors.o_data_error import ODataError
            
            worksheet = await self.graph_client.me.drive.items[file_id].workbook.worksheets.by_worksheet_id(
                self.worksheet_name
            ).get()
            
            range_result = await worksheet.range(address="A:Z").get()
            
            data = []
            if range_result and range_result.values:
                headers = range_result.values[0] if range_result.values else []
                
                for row in range_result.values[1:]:
                    if any(row):
                        item = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
                        data.append(item)
            
            print(f"✓ 讀取 {len(data)} 行數據")
            return data
            
        except ODataError as e:
            print(f"✗ 讀取工作表失敗: {e.error.message if e.error else e}")
            return []
        except Exception as e:
            print(f"✗ 讀取失敗: {e}")
            return []
    
    async def write_worksheet(self, file_id: str, data: List[Dict]) -> bool:
        """寫入數據到工作表"""
        self._ensure_client()
        
        try:
            if not data:
                print("⚠️ 無數據可寫入")
                return False
            
            headers = list(data[0].keys())
            values = [headers]
            
            for row in data:
                values.append([row.get(h, '') for h in headers])
            
            from msgraph.generated.models.json import JSON
            json_body = JSON(values=values)
            
            await self.graph_client.me.drive.items[file_id].workbook.worksheets.by_worksheet_id(
                self.worksheet_name
            ).range(address="A1").patch(json_body)
            
            print(f"✓ 寫入 {len(data)} 行數據")
            return True
            
        except Exception as e:
            print(f"✗ 寫入失敗: {e}")
            return False
    
    async def append_rows(self, file_id: str, data: List[Dict]) -> bool:
        """追加數據行"""
        self._ensure_client()
        
        try:
            if not data:
                return True
            
            existing = await self.read_worksheet(file_id)
            start_row = len(existing) + 2
            
            headers = list(data[0].keys())
            values = []
            
            for row in data:
                values.append([row.get(h, '') for h in headers])
            
            from msgraph.generated.models.json import JSON
            
            address = f"A{start_row}:{chr(65 + len(headers) - 1)}{start_row + len(values) - 1}"
            json_body = JSON(values=values)
            
            await self.graph_client.me.drive.items[file_id].workbook.worksheets.by_worksheet_id(
                self.worksheet_name
            ).range(address=address).patch(json_body)
            
            print(f"✓ 追加 {len(data)} 行數據")
            return True
            
        except Exception as e:
            print(f"✗ 追加失敗: {e}")
            return False
    
    async def sync_portfolio(self, stocks: List[Dict]) -> bool:
        """同步投資組合數據"""
        try:
            file_id = await self.get_or_create_file()
            if not file_id:
                return False
            
            await self.append_rows(file_id, stocks)
            return True
            
        except Exception as e:
            print(f"✗ 同步失敗: {e}")
            return False


class PortfolioManager:
    """投資組合管理器"""
    
    def __init__(self, graph_client=None):
        self.excel_client = ExcelOnlineClient(graph_client)
        self.stocks = []
    
    async def load_from_excel(self) -> List[Dict]:
        """從 Excel 加載投資組合"""
        import asyncio
        file_id = await self.excel_client.get_or_create_file()
        if not file_id:
            return []
        
        return await self.excel_client.read_worksheet(file_id)
    
    async def save_to_excel(self, stocks: List[Dict]) -> bool:
        """保存到 Excel"""
        import asyncio
        
        data = []
        for stock in stocks:
            data.append({
                'Symbol': stock.get('symbol', ''),
                'Price': stock.get('price', 0),
                'Change': stock.get('change', 0),
                'Change %': stock.get('change_percent', 0),
                'Updated': datetime.now().isoformat(),
            })
        
        return await self.excel_client.sync_portfolio(data)
    
    async def update_with_prices(self, stocks: List[Dict]) -> bool:
        """更新現有投資組合的價格"""
        import asyncio
        
        current = await self.load_from_excel()
        
        stock_map = {s['symbol']: s for s in stocks}
        
        for item in current:
            symbol = item.get('Symbol', '')
            if symbol in stock_map:
                stock = stock_map[symbol]
                item['Price'] = stock.get('price', item.get('Price', 0))
                item['Change'] = stock.get('change', item.get('Change', 0))
                item['Change %'] = stock.get('change_percent', item.get('Change %', 0))
                item['Updated'] = datetime.now().isoformat()
        
        return await self.excel_client.write_worksheet(
            await self.excel_client.get_or_create_file(),
            current
        ) if current else await self.save_to_excel(stocks)


async def sync_portfolio(stocks: List[Dict]) -> bool:
    """便捷函數：同步投資組合"""
    manager = PortfolioManager()
    return await manager.save_to_excel(stocks)


if __name__ == '__main__':
    print("📊 Excel Online 投資組合模組")
    print(f"文件路徑: {os.getenv('EXCEL_FILE_PATH', 'InvestSight/Portfolio.xlsx')}")
    print(f"工作表: {os.getenv('EXCEL_WORKSHEET', 'Portfolio')}")
