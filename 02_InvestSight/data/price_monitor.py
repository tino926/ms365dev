"""
價格監控模組
盤中價格變動監控與預警
"""
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Callable, Optional
from dotenv import load_dotenv

load_dotenv()


class PriceMonitor:
    """價格監控器"""
    
    def __init__(self, threshold_percent: float = 2.0):
        """
        初始化
        
        Args:
            threshold_percent: 價格變動閾值 (默認 2%)
        """
        self.threshold_percent = threshold_percent
        self.alerts = []
        self.callbacks = []
    
    def add_alert(self, symbol: str, price: float, condition: str = 'above'):
        """添加價格警示
        
        Args:
            symbol: 股票代碼
            price: 目標價格
            condition: 條件 ('above', 'below', 'change')
        """
        self.alerts.append({
            'symbol': symbol,
            'price': price,
            'condition': condition,
            'triggered': False
        })
    
    def add_callback(self, callback: Callable):
        """添加回調函數"""
        self.callbacks.append(callback)
    
    def check_price(self, symbol: str, current_price: float, prev_price: float = None) -> List[Dict]:
        """檢查價格並觸發警示"""
        triggered = []
        
        for alert in self.alerts:
            if alert['triggered'] or alert['symbol'] != symbol:
                continue
            
            condition = alert['condition']
            target = alert['price']
            
            if condition == 'above' and current_price > target:
                alert['triggered'] = True
                triggered.append({
                    'symbol': symbol,
                    'type': 'above',
                    'target': target,
                    'current': current_price,
                    'message': f'{symbol} 漲破 \${target:.2f} (現價 \${current_price:.2f})'
                })
            
            elif condition == 'below' and current_price < target:
                alert['triggered'] = True
                triggered.append({
                    'symbol': symbol,
                    'type': 'below',
                    'target': target,
                    'current': current_price,
                    'message': f'{symbol} 跌破 \${target:.2f} (現價 \${current_price:.2f})'
                })
            
            elif condition == 'change' and prev_price:
                change_pct = abs((current_price - prev_price) / prev_price * 100)
                if change_pct >= target:
                    alert['triggered'] = True
                    triggered.append({
                        'symbol': symbol,
                        'type': 'change',
                        'target': target,
                        'current': current_price,
                        'prev': prev_price,
                        'change_pct': change_pct,
                        'message': f'{symbol} 變動 {change_pct:.2f}% (從 \${prev_price:.2f} 到 \${current_price:.2f})'
                    })
        
        for t in triggered:
            self._notify(t)
        
        return triggered
    
    def _notify(self, alert: Dict):
        """觸發通知"""
        print(f"⚠️ 價格預警: {alert['message']}")
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"回調錯誤: {e}")
    
    def reset(self):
        """重置所有警示"""
        for alert in self.alerts:
            alert['triggered'] = False


class IntradayMonitor:
    """盤中實時監控"""
    
    def __init__(self, symbols: List[str], interval_seconds: int = 60):
        self.symbols = symbols
        self.interval_seconds = interval_seconds
        self.monitor = PriceMonitor()
        self.running = False
    
    def start(self, duration_minutes: int = None):
        """開始監控
        
        Args:
            duration_minutes: 監控時長（分鐘），None 為無限
        """
        from data.finance_api import FinanceDataFetcher
        import time
        
        fetcher = FinanceDataFetcher()
        self.running = True
        
        print(f"📈 開始盤中監控: {', '.join(self.symbols)}")
        print(f"   間隔: {self.interval_seconds}秒")
        print(f"   閾值: {self.monitor.threshold_percent}%")
        print()
        
        start_time = datetime.now()
        iteration = 0
        
        while self.running:
            iteration += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 檢查...")
            
            for symbol in self.symbols:
                data = fetcher.get_intraday_data(symbol, interval='15m', period='1d')
                
                if data is None or data.empty:
                    continue
                
                current = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2] if len(data) > 1 else current
                
                # 檢查變動
                triggered = self.monitor.check_price(symbol, current, prev)
                
                for t in triggered:
                    print(f"   ⚠️ {t['message']}")
            
            # 檢查時長
            if duration_minutes:
                elapsed = (datetime.now() - start_time).total_seconds() / 60
                if elapsed >= duration_minutes:
                    print(f"\n✅ 監控完成 (運行 {elapsed:.1f} 分鐘)")
                    break
            
            time.sleep(self.interval_seconds)
    
    def stop(self):
        """停止監控"""
        self.running = False


def setup_price_alerts(monitor: PriceMonitor, stocks: List[Dict]):
    """設置默認價格警示"""
    for stock in stocks:
        symbol = stock.get('symbol')
        price = stock.get('price', 0)
        
        # 監控 ±2% 變動
        monitor.add_alert(symbol, price * 1.02, 'above')
        monitor.add_alert(symbol, price * 0.98, 'below')


def send_alert_notification(alert: Dict):
    """發送警示通知"""
    try:
        from notification import send_price_alert
        
        symbol = alert['symbol']
        price = alert.get('current', 0)
        change = alert.get('change_pct', 0)
        
        # Teams 通知
        from notification import teams_notifier
        teams_notifier.send_price_alert(symbol, price, change)
        
    except Exception as e:
        print(f"通知失敗: {e}")


if __name__ == '__main__':
    print("=== 盤中價格監控 ===")
    print()
    
    from data.finance_api import FinanceDataFetcher
    fetcher = FinanceDataFetcher()
    
    # 獲取當前數據
    print("📊 當前市場數據:")
    results = fetcher.get_all_premarket_summary()
    
    for stock in results:
        change = stock['change_percent']
        icon = '🔴' if change < 0 else '🟢'
        print(f"   {icon} {stock['symbol']:6} \${stock['current_price']:7.2f} ({change:+6.2f}%)")
    
    print()
    print("監控功能可用:")
    print("  from data.finance_api import fetcher")
    print("  data = fetcher.get_intraday_data('AAPL', '15m')")
    print("  summary = fetcher.get_premarket_summary('AAPL')")
