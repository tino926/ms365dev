"""
OneDrive 文件存儲模組
通過 Microsoft Graph API 管理 OneDrive 文件
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, BinaryIO
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class OneDriveClient:
    """OneDrive 客戶端"""
    
    def __init__(self, graph_client=None):
        self.graph_client = graph_client
        self.base_path = os.getenv('ONEDRIVE_BASE_PATH', 'InvestSight')
    
    def _ensure_client(self):
        """確保 Graph 客戶端已初始化"""
        if not self.graph_client:
            from storage.graph_api import get_graph_client
            self.graph_client = get_graph_client()
            self.graph_client.authenticate(use_cache=True)
    
    async def upload_file(self, local_path: str, remote_path: str = None) -> bool:
        """上傳文件"""
        self._ensure_client()
        
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                print(f"✗ 文件不存在: {local_path}")
                return False
            
            if remote_path is None:
                remote_path = f"{self.base_path}/{local_path.name}"
            
            remote_path = remote_path.lstrip('/')
            
            with open(local_path, 'rb') as f:
                content = f.read()
            
            await self.graph_client.me.drive.root.item_by_path(remote_path).content.put(content)
            
            print(f"✓ 已上傳: {remote_path}")
            return True
            
        except Exception as e:
            print(f"✗ 上傳失敗: {e}")
            return False
    
    async def upload_text(self, content: str, remote_path: str) -> bool:
        """上傳文本內容"""
        self._ensure_client()
        
        try:
            remote_path = remote_path.lstrip('/')
            
            await self.graph_client.me.drive.root.item_by_path(remote_path).content.put(
                content.encode('utf-8')
            )
            
            print(f"✓ 已上傳: {remote_path}")
            return True
            
        except Exception as e:
            print(f"✗ 上傳失敗: {e}")
            return False
    
    async def download_file(self, remote_path: str, local_path: str = None) -> bool:
        """下載文件"""
        self._ensure_client()
        
        try:
            remote_path = remote_path.lstrip('/')
            
            if local_path is None:
                local_path = Path.cwd() / Path(remote_path).name
            
            content = await self.graph_client.me.drive.root.item_by_path(remote_path).content.get()
            
            with open(local_path, 'wb') as f:
                f.write(content)
            
            print(f"✓ 已下載: {local_path}")
            return True
            
        except Exception as e:
            print(f"✗ 下載失敗: {e}")
            return False
    
    async def list_files(self, path: str = None) -> List[Dict]:
        """列出文件"""
        self._ensure_client()
        
        try:
            if path:
                path = path.lstrip('/')
                result = await self.graph_client.me.drive.root.item_by_path(path).children.get()
            else:
                result = await self.graph_client.me.drive.root.children.get()
            
            files = []
            if result and result.value:
                for item in result.value:
                    files.append({
                        'name': item.name,
                        'id': item.id,
                        'size': item.size,
                        'type': 'folder' if item.folder else 'file',
                        'created': item.created_date_time.isoformat() if item.created_date_time else None,
                        'modified': item.last_modified_date_time.isoformat() if item.last_modified_date_time else None,
                    })
            
            print(f"✓ 找到 {len(files)} 個項目")
            return files
            
        except Exception as e:
            print(f"✗ 列表失敗: {e}")
            return []
    
    async def delete_file(self, remote_path: str) -> bool:
        """刪除文件"""
        self._ensure_client()
        
        try:
            remote_path = remote_path.lstrip('/')
            
            await self.graph_client.me.drive.root.item_by_path(remote_path).delete()
            
            print(f"✓ 已刪除: {remote_path}")
            return True
            
        except Exception as e:
            print(f"✗ 刪除失敗: {e}")
            return False
    
    async def create_folder(self, path: str) -> bool:
        """創建文件夾"""
        self._ensure_client()
        
        try:
            from msgraph.generated.models.drive_item import DriveItem
            from msgraph.generated.models.folder import Folder
            
            path = path.lstrip('/')
            
            drive_item = DriveItem()
            drive_item.name = Path(path).name
            drive_item.folder = Folder()
            
            parent_path = str(Path(path).parent)
            if parent_path == '.':
                parent_path = self.base_path
            else:
                parent_path = f"{self.base_path}/{parent_path}"
            
            await self.graph_client.me.drive.root.item_by_path(parent_path).children.post(drive_item)
            
            print(f"✓ 已創建文件夾: {path}")
            return True
            
        except Exception as e:
            print(f"✗ 創建失敗: {e}")
            return False
    
    async def get_share_link(self, remote_path: str, type: str = "view") -> Optional[str]:
        """獲取分享連結"""
        self._ensure_client()
        
        try:
            from msgraph.generated.models.permission import Permission
            from msgraph.generated.models.link_type import LinkType
            from msgraph.generated.models.sharing_link import SharingLink
            
            remote_path = remote_path.lstrip('/')
            
            permission = Permission()
            permission.link = SharingLink()
            permission.link.type = LinkType(type)
            
            result = await self.graph_client.me.drive.root.item_by_path(remote_path).permissions.post(permission)
            
            if result and result.link and result.link.web_url:
                print(f"✓ 獲取分享連結成功")
                return result.link.web_url
            
            return None
            
        except Exception as e:
            print(f"✗ 獲取分享連結失敗: {e}")
            return None


class FileStorage:
    """文件存儲管理器"""
    
    def __init__(self, graph_client=None):
        self.client = OneDriveClient(graph_client)
        self.reports_path = os.getenv('ONEDRIVE_REPORTS_PATH', 'InvestSight/Reports')
    
    async def save_report(self, content: str, filename: str = None) -> bool:
        """保存報告"""
        if filename is None:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        path = f"{self.reports_path}/{filename}"
        return await self.client.upload_text(content, path)
    
    async def save_data(self, data: str, filename: str) -> bool:
        """保存數據"""
        path = f"{self.base_path}/Data/{filename}"
        return await self.client.upload_text(data, path)
    
    async def list_reports(self) -> List[Dict]:
        """列出報告"""
        return await self.client.list_files(self.reports_path)


async def upload_file(local_path: str, remote_path: str = None) -> bool:
    """便捷函數"""
    client = OneDriveClient()
    return await client.upload_file(local_path, remote_path)


async def download_file(remote_path: str, local_path: str = None) -> bool:
    """便捷函數"""
    client = OneDriveClient()
    return await client.download_file(remote_path, local_path)


if __name__ == '__main__':
    print("📁 OneDrive 文件存儲模組")
    client = OneDriveClient()
    print(f"基礎路徑: {client.base_path}")
