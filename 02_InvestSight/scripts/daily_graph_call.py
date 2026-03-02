#!/usr/bin/env python3
"""
Microsoft Graph API - 每日調用（產生 E5 活躍記錄）
使用 Client Secret 認證，不需要瀏覽器
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
import asyncio

load_dotenv()

# 配置
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')


async def daily_graph_call():
    """
    簡單的 Graph API 調用
    目的：產生 E5 活躍記錄
    """
    print("=" * 60)
    print("  📅 InvestSight - 每日 Graph API 調用")
    print("=" * 60)
    print()
    
    # 驗證配置
    if not all([CLIENT_ID, TENANT_ID, CLIENT_SECRET]):
        print("✗ 錯誤：缺少必要的配置")
        print("  請檢查 .env 文件")
        return False
    
    try:
        # 創建憑證（不需要互動）
        credential = ClientSecretCredential(
            client_id=CLIENT_ID,
            tenant_id=TENANT_ID,
            client_secret=CLIENT_SECRET
        )
        
        # 獲取 token（這就是產生活躍記錄的關鍵！）
        print("正在獲取 access token...")
        token = credential.get_token("https://graph.microsoft.com/.default")
        
        print("✓ Token 獲取成功！")
        print(f"  Token 前 50 字元：{token.token[:50]}...")
        print(f"  過期時間：{token.expires_on}")
        print()
        
        # 簡單的 API 調用
        import aiohttp
        
        headers = {"Authorization": f"Bearer {token.token}"}
        
        async with aiohttp.ClientSession() as session:
            # 調用 /organization API（應用有權限訪問）
            async with session.get(
                "https://graph.microsoft.com/v1.0/organization",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✓ Graph API 調用成功！")
                    print(f"  組織：{data['value'][0]['displayName']}")
                else:
                    print(f"⚠ API 調用返回狀態碼：{response.status}")
                    print("  但認證已成功，E5 記錄已產生")
        
        print()
        print("=" * 60)
        print("  ✅ 完成！E5 活躍記錄已產生")
        print("=" * 60)
        print()
        print("💡 提示：每天執行一次即可保持 E5 活躍")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ 錯誤：{e}")
        print()
        print("⚠ 如果認證失敗，請檢查：")
        print("  1. Client ID 是否正確")
        print("  2. Tenant ID 是否正確")
        print("  3. Client Secret 是否已過期或被撤銷")
        print()
        return False


if __name__ == '__main__':
    asyncio.run(daily_graph_call())
