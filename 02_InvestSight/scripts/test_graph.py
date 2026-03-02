#!/usr/bin/env python3
"""
測試 Microsoft Graph API 連接
使用 Device Code 認證 + Token 緩存
"""
import asyncio
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from storage.graph_api import test_graph_api


async def main():
    print("=" * 60)
    print("🚀 InvestSight - Microsoft Graph API 測試")
    print("=" * 60)
    print()
    print("此測試將：")
    print("1. 使用緩存的 token（如果有）或 Device Code 認證")
    print("2. 獲取您的用戶資料")
    print("3. 列出收件匣郵件")
    print()
    print("這會在 Microsoft Graph 產生調用記錄！")
    print()
    print("💡 提示：首次認證後，token 會保存到 pri/tokens.json")
    print("   後續使用不需要再打開瀏覽器！")
    print()
    
    await test_graph_api()


if __name__ == '__main__':
    asyncio.run(main())
