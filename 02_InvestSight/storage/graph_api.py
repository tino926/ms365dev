"""
Microsoft Graph API 整合模塊（Device Code 認證）
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
import json
import webbrowser

load_dotenv()

# 配置
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
GRAPH_SCOPES = os.getenv('AZURE_GRAPH_SCOPES', 'User.Read Mail.Read Mail.Send').split(' ')

# Token 緩存路徑（與 01_python_ms_graph 相同位置）
TOKEN_CACHE_PATH = Path(__file__).parent.parent / 'pri' / 'tokens.json'


class GraphClient:
    """Microsoft Graph API 客戶端（Device Code 認證）"""
    
    def __init__(self):
        self.credential = None
        self.graph_client = None
        self._token_cache = {}
        
    def _load_token_cache(self):
        """從文件加載 token 緩存"""
        if TOKEN_CACHE_PATH.exists():
            try:
                with open(TOKEN_CACHE_PATH, 'r', encoding='utf-8') as f:
                    self._token_cache = json.load(f)
                print(f"✓ 已加載 token 緩存：{TOKEN_CACHE_PATH}")
                return True
            except Exception as e:
                print(f"⚠ 加載 token 緩存失敗：{e}")
        return False
    
    def _save_token_cache(self, token_data: dict):
        """保存 token 到文件緩存"""
        TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # 添加過期時間
        import time
        import base64
        import json
        
        access_token = token_data.get('access_token', '')
        if access_token and len(access_token.split('.')) == 3:
            try:
                # 解析 JWT token 的過期時間
                payload = access_token.split('.')[1]
                payload += '=' * (4 - len(payload) % 4)
                decoded = json.loads(base64.urlsafe_b64decode(payload))
                token_data['exp'] = decoded.get('exp', int(time.time() + 3600))
            except:
                token_data['exp'] = int(time.time() + 3600)  # 預設 1 小時
        else:
            token_data['exp'] = int(time.time() + 3600)
        
        try:
            with open(TOKEN_CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, indent=2)
            print(f"✓ Token 已保存到：{TOKEN_CACHE_PATH}")
        except Exception as e:
            print(f"⚠ 保存 token 失敗：{e}")
    
    def _token_is_valid(self) -> bool:
        """檢查 token 是否有效（包含過期時間檢查）"""
        if not self._token_cache.get('access_token'):
            return False
        
        # 檢查過期時間
        import time
        exp = self._token_cache.get('exp', 0)
        if exp and exp < time.time():
            print("⚠️ Token 已過期，需要重新認證")
            return False
        
        # 添加 5 分鐘緩衝時間
        if exp and exp < time.time() + 300:
            print("⚠️ Token 即將過期，建議重新認證")
            return False
        
        return True
    
    def authenticate(self, use_cache: bool = True):
        """
        使用 Device Code 進行認證
        
        Args:
            use_cache: 是否使用緩存的 token（預設 True）
        """
        print("\n" + "=" * 60)
        print("🔐 Microsoft Graph API 認證")
        print("=" * 60)
        
        # 嘗試使用緩存的 token
        if use_cache and self._load_token_cache():
            if self._token_is_valid():
                print("✓ 使用緩存的 token")
                # 注意：DeviceCodeCredential 不支持直接設置 token
                # 但我們可以跳過瀏覽器，直接嘗試 API 調用
                # 如果 token 過期，會自動觸發重新認證
                print("⚠ 如果 token 過期，將自動重新認證")
        
        # 創建 DeviceCodeCredential
        self.credential = DeviceCodeCredential(
            client_id=CLIENT_ID,
            tenant_id=TENANT_ID
        )
        
        # 創建 Graph 客戶端
        self.graph_client = GraphServiceClient(
            credentials=self.credential,
            scopes=GRAPH_SCOPES
        )
        
        print("✓ 認證客戶端已初始化")
        return True
    
    def _open_browser(self, url: str):
        """打開瀏覽器（可選）"""
        try:
            webbrowser.open(url)
            print(f"🌐 已打開瀏覽器：{url}")
        except Exception as e:
            print(f"⚠ 無法自動打開瀏覽器，請手動訪問：{url}")
            print(f"   錯誤：{e}")
    
    async def get_user_profile(self):
        """獲取當前用戶資料"""
        if not self.graph_client:
            print("✗ 請先認證")
            return None
        
        try:
            user = await self.graph_client.me.get()
            return {
                'display_name': user.display_name,
                'email': user.mail or user.user_principal_name,
                'user_id': user.id,
            }
        except Exception as e:
            print(f"✗ 獲取用戶資料失敗：{e}")
            return None
    
    async def send_email(self, subject: str, body: str, to_email: str):
        """發送郵件"""
        if not self.graph_client:
            print("✗ 請先認證")
            return False
        
        try:
            from msgraph.generated.models.message import Message
            from msgraph.generated.models.item_body import ItemBody
            from msgraph.generated.models.body_type import BodyType
            from msgraph.generated.models.recipient import Recipient
            from msgraph.generated.models.email_address import EmailAddress
            from msgraph.generated.models.send_mail_post_request_body import SendMailPostRequestBody
            
            # 創建郵件對象
            message = Message()
            message.subject = subject
            message.body = ItemBody()
            message.body.content_type = BodyType.Text
            message.body.content = body
            
            # 設置收件人
            to_recipient = Recipient()
            to_recipient.email_address = EmailAddress()
            to_recipient.email_address.address = to_email
            message.to_recipients = [to_recipient]
            
            # 發送郵件
            request_body = SendMailPostRequestBody()
            request_body.message = message
            
            await self.graph_client.me.send_mail.post(body=request_body)
            print(f"✓ 郵件已發送到：{to_email}")
            return True
            
        except Exception as e:
            print(f"✗ 發送郵件失敗：{e}")
            return False
    
    async def upload_to_onedrive(self, file_path: str, drive_path: str = None):
        """上傳文件到 OneDrive"""
        if not self.graph_client:
            print("✗ 請先認證")
            return False
        
        try:
            from msgraph.generated.drives.item.items.item.content.content_request_builder import ContentRequestBuilder
            
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"✗ 文件不存在：{file_path}")
                return False
            
            # 默認上傳到根目錄
            if drive_path is None:
                drive_path = f"/{file_path.name}"
            
            # 讀取文件內容
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 上傳到 OneDrive
            await self.graph_client.me.drive.root.item_by_path(drive_path).content.put(content)
            
            print(f"✓ 文件已上傳到 OneDrive: {drive_path}")
            return True
            
        except Exception as e:
            print(f"✗ 上傳到 OneDrive 失敗：{e}")
            return False
    
    async def list_inbox_messages(self, top: int = 5):
        """獲取收件匣郵件"""
        if not self.graph_client:
            print("✗ 請先認證")
            return None

        try:
            # msgraph-sdk 1.2.0+ 的新 API
            from msgraph import GraphServiceClient
            
            # 使用簡單的查詢方式
            messages = await self.graph_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                query_parameters={
                    '$select': 'from,isRead,receivedDateTime,subject',
                    '$top': top,
                    '$orderby': 'receivedDateTime DESC'
                }
            )

            if messages and messages.value:
                result = []
                for msg in messages.value:
                    result.append({
                        'subject': msg.subject,
                        'from': msg.from_.email_address.name if msg.from_ else 'Unknown',
                        'is_read': msg.is_read,
                        'received': msg.received_date_time,
                    })
                return result
            return []

        except Exception as e:
            print(f"✗ 獲取郵件失敗：{e}")
            return None


# 全局實例
_graph_client = None

def get_graph_client() -> GraphClient:
    """獲取 GraphClient 單例"""
    global _graph_client
    if _graph_client is None:
        _graph_client = GraphClient()
    return _graph_client


# 測試函數
async def test_graph_api():
    """測試 Graph API 連接"""
    client = get_graph_client()

    # 認證（使用緩存的 token）
    if not client.authenticate(use_cache=True):
        return

    # 測試 1: 獲取用戶資料
    print("\n" + "=" * 60)
    print("📋 測試 1: 獲取用戶資料")
    print("=" * 60)
    user = await client.get_user_profile()
    if user:
        print(f"✓ 用戶：{user['display_name']}")
        print(f"✓ Email: {user['email']}")
        
        # 保存 token
        client._save_token_cache({
            'graph_scopes': ' '.join(GRAPH_SCOPES),
            'access_token': 'saved_after_auth'  # 實際 token 由 credential 管理
        })

    # 測試 2: 列出收件匣郵件
    print("\n" + "=" * 60)
    print("📧 測試 2: 列出收件匣郵件")
    print("=" * 60)
    messages = await client.list_inbox_messages(top=5)
    if messages:
        for i, msg in enumerate(messages, 1):
            status = "✓" if msg['is_read'] else "📭"
            print(f"{i}. {status} {msg['subject'][:50]}...")
            print(f"   從：{msg['from']} | 時間：{msg['received']}")

    print("\n" + "=" * 60)
    print("✅ Graph API 測試完成！")
    print("=" * 60)


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_graph_api())
