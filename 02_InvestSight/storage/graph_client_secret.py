#!/usr/bin/env python3
"""
Microsoft Graph API - Client Secret 認證（自動化）
不需要瀏覽器登入，適合定時任務和自動化腳本
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
import json
import asyncio

load_dotenv()

# 配置（從 .env 讀取）
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
SCOPES = os.getenv('AZURE_GRAPH_SCOPES', '.default').split(' ')


class ClientSecretGraphClient:
    """Microsoft Graph API Client Secret 客戶端"""
    
    def __init__(self):
        self.credential = None
        self.graph_client = None
        self._token = None
        
    def authenticate(self):
        """
        使用 Client Secret 進行認證（不需要瀏覽器）
        
        Returns:
            bool: 認證是否成功
        """
        print("\n" + "=" * 60)
        print("🔐 Microsoft Graph API - Client Secret 認證")
        print("=" * 60)
        
        # 驗證配置是否存在
        if not all([CLIENT_ID, TENANT_ID, CLIENT_SECRET]):
            print("✗ 錯誤：缺少必要的配置")
            print("  請在 .env 文件中設置：")
            print("    AZURE_CLIENT_ID=your-client-id")
            print("    AZURE_TENANT_ID=your-tenant-id")
            print("    AZURE_CLIENT_SECRET=your-client-secret")
            return False
        
        try:
            # 創建 Client Secret Credential（不需要互動）
            self.credential = ClientSecretCredential(
                client_id=CLIENT_ID,
                tenant_id=TENANT_ID,
                client_secret=CLIENT_SECRET
            )
            
            # 創建 Graph 客戶端
            self.graph_client = GraphServiceClient(
                credentials=self.credential,
                scopes=SCOPES
            )
            
            print("✓ 认证成功！")
            print(f"  應用 ID: {CLIENT_ID[:20]}...")
            print(f"  租戶 ID: {TENANT_ID[:20]}...")
            return True
            
        except Exception as e:
            print(f"✗ 认证失敗：{e}")
            return False
    
    async def get_user_profile(self):
        """獲取當前應用關聯的用戶資料"""
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
    
    async def list_users(self, top: int = 10):
        """列出組織中的用戶（需要 Directory.Read.All 權限）"""
        if not self.graph_client:
            print("✗ 請先認證")
            return None
        
        try:
            users = await self.graph_client.users.get(
                query_parameters={'$top': top}
            )
            
            if users and users.value:
                result = []
                for user in users.value[:top]:
                    result.append({
                        'display_name': user.display_name,
                        'email': user.mail or user.user_principal_name,
                        'user_id': user.id,
                    })
                return result
            return []
            
        except Exception as e:
            print(f"✗ 獲取用戶列表失敗：{e}")
            return None
    
    async def get_organization_info(self):
        """獲取組織資訊"""
        if not self.graph_client:
            print("✗ 請先認證")
            return None
        
        try:
            org = await self.graph_client.organization.get()
            return {
                'display_name': org.display_name,
                'id': org.id,
            }
        except Exception as e:
            print(f"✗ 獲取組織資訊失敗：{e}")
            return None


# 測試函數
async def test_client_secret():
    """測試 Client Secret 認證"""
    client = ClientSecretGraphClient()
    
    # 認證（不需要瀏覽器）
    if not client.authenticate():
        print("\n⚠️ 認證失敗，請檢查 .env 配置")
        return
    
    # 測試 1: 獲取組織資訊
    print("\n" + "=" * 60)
    print("📋 測試 1: 獲取組織資訊")
    print("=" * 60)
    org = await client.get_organization_info()
    if org:
        print(f"✓ 組織：{org['display_name']}")
        print(f"✓ ID: {org['id']}")
    
    # 測試 2: 獲取用戶資料
    print("\n" + "=" * 60)
    print("📋 測試 2: 獲取用戶資料")
    print("=" * 60)
    user = await client.get_user_profile()
    if user:
        print(f"✓ 用戶：{user['display_name']}")
        print(f"✓ Email: {user['email']}")
    
    # 測試 3: 列出用戶（需要權限）
    print("\n" + "=" * 60)
    print("📋 測試 3: 列出組織用戶（前 5 位）")
    print("=" * 60)
    users = await client.list_users(top=5)
    if users:
        for i, u in enumerate(users, 1):
            print(f"{i}. {u['display_name']} - {u['email']}")
    
    print("\n" + "=" * 60)
    print("✅ Client Secret 認證測試完成！")
    print("=" * 60)
    print("\n💡 提示：此認證方式不需要瀏覽器，適合自動化腳本")
    print()


if __name__ == '__main__':
    asyncio.run(test_client_secret())
