#!/usr/bin/env python3
"""
股價警報系統
監控股價並在被觸發時發送通知
"""
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from typing import Dict, List, Optional
from datetime import datetime
from data.finance_api import fetcher as finance_fetcher
from notification.email import EmailNotifier
from notification.teams import TeamsNotifier


class PriceAlert:
    """股價警報"""

    def __init__(self, symbol: str, condition: str, target_price: float, enabled: bool = True):
        """
        初始化股價警報

        Args:
            symbol: 股票代號
            condition: 條件 ('above' 或 'below')
            target_price: 目標價格
            enabled: 是否啟用
        """
        self.symbol = symbol
        self.condition = condition
        self.target_price = target_price
        self.enabled = enabled
        self.created_at = datetime.now().isoformat()
        self.triggered_at = None
        self.triggered_price = None

    def check(self, current_price: float) -> bool:
        """
        檢查是否觸發警報

        Args:
            current_price: 當前股價

        Returns:
            是否觸發
        """
        if not self.enabled:
            return False

        triggered = False
        if self.condition == 'above' and current_price >= self.target_price:
            triggered = True
        elif self.condition == 'below' and current_price <= self.target_price:
            triggered = True

        if triggered:
            self.triggered_at = datetime.now().isoformat()
            self.triggered_price = current_price

        return triggered

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            'symbol': self.symbol,
            'condition': self.condition,
            'target_price': self.target_price,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'triggered_at': self.triggered_at,
            'triggered_price': self.triggered_price,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PriceAlert':
        """從字典創建"""
        alert = cls(
            symbol=data['symbol'],
            condition=data['condition'],
            target_price=data['target_price'],
            enabled=data.get('enabled', True)
        )
        alert.created_at = data.get('created_at')
        alert.triggered_at = data.get('triggered_at')
        alert.triggered_price = data.get('triggered_price')
        return alert


class AlertManager:
    """警報管理器"""

    def __init__(self, alerts_file: Optional[Path] = None):
        """
        初始化警報管理器

        Args:
            alerts_file: 警報配置文件路徑
        """
        if alerts_file is None:
            alerts_file = Path(__file__).parent.parent / 'config' / 'alerts.json'
        
        self.alerts_file = alerts_file
        self.alerts: List[PriceAlert] = []
        self.email_notifier = EmailNotifier()
        self.teams_notifier = TeamsNotifier()
        
        # 加載現有警報
        self.load_alerts()

    def add_alert(self, symbol: str, condition: str, target_price: float) -> PriceAlert:
        """
        添加新警報

        Args:
            symbol: 股票代號
            condition: 條件 ('above' 或 'below')
            target_price: 目標價格

        Returns:
            創建的警報對象
        """
        alert = PriceAlert(symbol, condition, target_price)
        self.alerts.append(alert)
        self.save_alerts()
        return alert

    def remove_alert(self, index: int) -> bool:
        """
        移除警報

        Args:
            index: 警報索引

        Returns:
            是否成功移除
        """
        if 0 <= index < len(self.alerts):
            self.alerts.pop(index)
            self.save_alerts()
            return True
        return False

    def list_alerts(self) -> List[PriceAlert]:
        """列出所有警報"""
        return self.alerts

    def check_all(self) -> List[PriceAlert]:
        """
        檢查所有警報是否觸發

        Returns:
            觸發的警報列表
        """
        triggered_alerts = []
        
        # 獲取所有股票價格
        stocks = finance_fetcher.fetch_all_stocks()
        stock_prices = {s['symbol']: s.get('price') for s in stocks if s.get('price')}
        
        for alert in self.alerts:
            if not alert.enabled:
                continue
            
            current_price = stock_prices.get(alert.symbol)
            if current_price is None:
                continue
            
            if alert.check(current_price):
                triggered_alerts.append(alert)
                print(f"🚨 警報觸發！{alert.symbol} {alert.condition} ${alert.target_price:.2f}")
                print(f"   當前價：${current_price:.2f}")
                
                # 發送通知
                self._send_notification(alert, current_price)
                
                # 禁用已觸發的警報（避免重複通知）
                alert.enabled = False
        
        if triggered_alerts:
            self.save_alerts()
        
        return triggered_alerts

    def _send_notification(self, alert: PriceAlert, current_price: float):
        """
        發送警報通知

        Args:
            alert: 觸發的警報
            current_price: 當前價格
        """
        subject = f"🚨 股價警報：{alert.symbol}"
        message = f"""
        <h2>股價警報觸發</h2>
        <p><strong>股票：</strong> {alert.symbol}</p>
        <p><strong>條件：</strong> {alert.condition} ${alert.target_price:.2f}</p>
        <p><strong>當前價：</strong> ${current_price:.2f}</p>
        <p><strong>觸發時間：</strong> {alert.triggered_at}</p>
        <hr>
        <small>InvestSight 自動警報系統</small>
        """
        
        # 發送郵件
        try:
            self.email_notifier.send_email(
                to_email='',  # 使用預設收件人
                subject=subject,
                body=message
            )
            print("  ✓ 郵件通知已發送")
        except Exception as e:
            print(f"  ⚠ 郵件發送失敗：{e}")
        
        # 發送 Teams 通知
        try:
            self.teams_notifier.send_price_alert(
                symbol=alert.symbol,
                condition=alert.condition,
                target_price=alert.target_price,
                current_price=current_price
            )
            print("  ✓ Teams 通知已發送")
        except Exception as e:
            print(f"  ⚠ Teams 發送失敗：{e}")

    def save_alerts(self):
        """保存警報到文件"""
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'alerts': [alert.to_dict() for alert in self.alerts],
            'updated_at': datetime.now().isoformat()
        }
        
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_alerts(self):
        """從文件加載警報"""
        if not self.alerts_file.exists():
            return
        
        try:
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.alerts = [PriceAlert.from_dict(a) for a in data.get('alerts', [])]
            print(f"✓ 已加載 {len(self.alerts)} 個警報")
        except Exception as e:
            print(f"⚠ 加載警報失敗：{e}")
            self.alerts = []


def main():
    """測試警報系統"""
    print("=" * 70)
    print("  🚨 股價警報系統測試")
    print("=" * 70)
    print()
    
    # 創建警報管理器
    manager = AlertManager()
    
    # 添加測試警報
    print("📊 添加測試警報...")
    manager.add_alert('AAPL', 'above', 270)
    manager.add_alert('MSFT', 'below', 390)
    manager.add_alert('GOOGL', 'above', 310)
    
    print(f"當前警報：{len(manager.alerts)} 個")
    for i, alert in enumerate(manager.alerts):
        status = "✓" if alert.enabled else "✗"
        print(f"  {i+1}. {status} {alert.symbol} {alert.condition} ${alert.target_price:.2f}")
    print()
    
    # 檢查是否觸發
    print("🔍 檢查警報...")
    triggered = manager.check_all()
    
    if triggered:
        print(f"\n🚨 {len(triggered)} 個警報觸發！")
    else:
        print("\n✓ 沒有警報觸發")
    
    print()
    print("=" * 70)
    print("  ✅ 測試完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
