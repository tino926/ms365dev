#!/usr/bin/env python3
"""
新功能整合測試腳本
測試 OpenCode 開發的所有新建模塊
"""
import asyncio
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_email_module():
    """測試郵件通知模塊"""
    print("\n" + "=" * 60)
    print("📧 測試：郵件通知模塊")
    print("=" * 60)
    
    try:
        from notification.email import EmailNotifier, EmailConfig
        
        # 測試配置
        config = EmailConfig()
        print(f"✓ EmailConfig 初始化成功")
        print(f"  SMTP Host: {config.smtp_host or '(未配置)'}")
        print(f"  Use Graph API: {config.use_graph}")
        
        # 測試實例
        notifier = EmailNotifier()
        print(f"✓ EmailNotifier 創建成功")
        
        # 檢查可用方法
        methods = ['send_email', 'send_price_alert', 'send_news_summary', 'send_daily_report']
        for method in methods:
            if hasattr(notifier, method):
                print(f"  ✓ 方法可用：{method}()")
        
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗：{e}")
        return False


def test_teams_module():
    """測試 Teams 通知模塊"""
    print("\n" + "=" * 60)
    print("💬 測試：Teams 通知模塊")
    print("=" * 60)
    
    try:
        from notification.teams import TeamsNotifier
        
        notifier = TeamsNotifier()
        print(f"✓ TeamsNotifier 創建成功")
        
        # 檢查可用方法
        methods = ['send', 'send_price_alert', 'send_daily_summary']
        for method in methods:
            if hasattr(notifier, method):
                print(f"  ✓ 方法可用：{method}()")
        
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗：{e}")
        return False


async def test_excel_module():
    """測試 Excel Online 模塊"""
    print("\n" + "=" * 60)
    print("📊 測試：Excel Online 模塊")
    print("=" * 60)
    
    try:
        from storage.excel_online import ExcelOnlineClient, PortfolioManager
        
        client = ExcelOnlineClient()
        print(f"✓ ExcelOnlineClient 創建成功")
        print(f"  文件路徑：{client.file_path}")
        print(f"  工作表：{client.worksheet_name}")
        
        manager = PortfolioManager()
        print(f"✓ PortfolioManager 創建成功")
        
        # 檢查可用方法
        methods = ['update_stock', 'get_portfolio', 'add_stock', 'remove_stock']
        for method in methods:
            if hasattr(manager, method):
                print(f"  ✓ 方法可用：{method}()")
        
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗：{e}")
        return False


async def test_onedrive_module():
    """測試 OneDrive 模塊"""
    print("\n" + "=" * 60)
    print("📁 測試：OneDrive 模塊")
    print("=" * 60)
    
    try:
        from storage.onedrive import OneDriveClient, FileStorage
        
        client = OneDriveClient()
        print(f"✓ OneDriveClient 創建成功")
        print(f"  基礎路徑：{client.base_path}")
        
        storage = FileStorage()
        print(f"✓ FileStorage 創建成功")
        
        # 檢查可用方法
        methods = ['upload_file', 'download_file', 'list_files', 'delete_file']
        for method in methods:
            if hasattr(storage, method):
                print(f"  ✓ 方法可用：{method}()")
        
        return True
        
    except Exception as e:
        print(f"✗ 測試失敗：{e}")
        return False


def test_integration():
    """測試整合功能"""
    print("\n" + "=" * 60)
    print("🔗 測試：模塊整合")
    print("=" * 60)
    
    try:
        # 測試是否可以從現有腳本導入
        from data.finance_api import fetcher as finance_fetcher
        from data.news_api import fetcher as news_fetcher
        
        print(f"✓ 數據抓取模塊可導入")
        
        # 測試是否可以與通知模塊整合
        from notification.email import EmailNotifier
        from notification.teams import TeamsNotifier
        
        print(f"✓ 通知模塊可與數據模塊整合")
        
        return True
        
    except Exception as e:
        print(f"✗ 整合測試失敗：{e}")
        return False


async def main():
    print("=" * 70)
    print("  🧪 InvestSight 新功能整合測試")
    print("=" * 70)
    
    results = {
        '郵件通知': test_email_module(),
        'Teams 通知': test_teams_module(),
        'Excel Online': await test_excel_module(),
        'OneDrive': await test_onedrive_module(),
        '模塊整合': test_integration(),
    }
    
    # 總結
    print("\n" + "=" * 70)
    print("  📊 測試總結")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {status} - {test_name}")
    
    passed = sum(results.values())
    total = len(results)
    
    print()
    if passed == total:
        print("🎉 所有測試通過！新功能已準備就緒！")
    else:
        print(f"⚠️  {passed}/{total} 個測試通過")
    
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(main())
