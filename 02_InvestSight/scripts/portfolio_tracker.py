#!/usr/bin/env python3
"""
投資組合追蹤模塊
記錄持股、計算損益、生成報告
"""
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from typing import Dict, List, Optional
from datetime import datetime
from data.finance_api import fetcher as finance_fetcher


class Holding:
    """持股記錄"""

    def __init__(self, symbol: str, shares: float, avg_cost: float, notes: str = ''):
        """
        初始化持股記錄

        Args:
            symbol: 股票代號
            shares: 股數
            avg_cost: 平均成本
            notes: 備註
        """
        self.symbol = symbol
        self.shares = shares
        self.avg_cost = avg_cost
        self.notes = notes
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def update(self, shares: Optional[float] = None, avg_cost: Optional[float] = None, notes: Optional[str] = None):
        """更新持股信息"""
        if shares is not None:
            self.shares = shares
        if avg_cost is not None:
            self.avg_cost = avg_cost
        if notes is not None:
            self.notes = notes
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            'symbol': self.symbol,
            'shares': self.shares,
            'avg_cost': self.avg_cost,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Holding':
        """從字典創建"""
        holding = cls(
            symbol=data['symbol'],
            shares=data['shares'],
            avg_cost=data['avg_cost'],
            notes=data.get('notes', '')
        )
        holding.created_at = data.get('created_at')
        holding.updated_at = data.get('updated_at')
        return holding


class Portfolio:
    """投資組合管理器"""

    def __init__(self, portfolio_file: Optional[Path] = None):
        """
        初始化投資組合

        Args:
            portfolio_file: 投資組合文件路徑
        """
        if portfolio_file is None:
            portfolio_file = Path(__file__).parent.parent / 'config' / 'portfolio.json'
        
        self.portfolio_file = portfolio_file
        self.holdings: List[Holding] = []
        self.initial_capital = 0.0
        self.created_at = datetime.now().isoformat()
        
        # 加載現有投資組合
        self.load_portfolio()

    def add_holding(self, symbol: str, shares: float, avg_cost: float, notes: str = '') -> Holding:
        """
        添加持股

        Args:
            symbol: 股票代號
            shares: 股數
            avg_cost: 平均成本
            notes: 備註

        Returns:
            創建的持股對象
        """
        # 檢查是否已存在
        existing = self.get_holding(symbol)
        if existing:
            # 加碼：計算新的平均成本
            total_shares = existing.shares + shares
            total_cost = (existing.shares * existing.avg_cost) + (shares * avg_cost)
            new_avg_cost = total_cost / total_shares
            existing.update(shares=total_shares, avg_cost=new_avg_cost)
            self.save_portfolio()
            return existing
        else:
            # 新建持股
            holding = Holding(symbol, shares, avg_cost, notes)
            self.holdings.append(holding)
            self.save_portfolio()
            return holding

    def remove_holding(self, symbol: str) -> bool:
        """
        移除持股

        Args:
            symbol: 股票代號

        Returns:
            是否成功移除
        """
        for i, holding in enumerate(self.holdings):
            if holding.symbol == symbol:
                self.holdings.pop(i)
                self.save_portfolio()
                return True
        return False

    def get_holding(self, symbol: str) -> Optional[Holding]:
        """獲取持股"""
        for holding in self.holdings:
            if holding.symbol == symbol:
                return holding
        return None

    def get_portfolio_summary(self) -> Dict:
        """
        獲取投資組合摘要

        Returns:
            包含投資組合信息的字典
        """
        stocks = finance_fetcher.fetch_all_stocks()
        stock_prices = {s['symbol']: s.get('price', 0) for s in stocks}
        
        total_value = 0.0
        total_cost = 0.0
        total_gain_loss = 0.0
        total_gain_loss_percent = 0.0
        
        holdings_data = []
        
        for holding in self.holdings:
            current_price = stock_prices.get(holding.symbol, 0)
            market_value = current_price * holding.shares
            cost_basis = holding.avg_cost * holding.shares
            gain_loss = market_value - cost_basis
            gain_loss_percent = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
            
            total_value += market_value
            total_cost += cost_basis
            total_gain_loss += gain_loss
            
            holdings_data.append({
                'symbol': holding.symbol,
                'shares': holding.shares,
                'avg_cost': holding.avg_cost,
                'current_price': current_price,
                'market_value': market_value,
                'gain_loss': gain_loss,
                'gain_loss_percent': gain_loss_percent,
                'weight': (market_value / total_value * 100) if total_value > 0 else 0,
            })
        
        # 計算權重
        for holding in holdings_data:
            holding['weight'] = (holding['market_value'] / total_value * 100) if total_value > 0 else 0
        
        total_gain_loss_percent = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_value': total_value,
            'total_cost': total_cost,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent,
            'holdings_count': len(self.holdings),
            'holdings': holdings_data,
        }

    def generate_report(self) -> str:
        """
        生成投資組合報告

        Returns:
            格式化的報告字符串
        """
        summary = self.get_portfolio_summary()
        
        report = []
        report.append("=" * 70)
        report.append("  📊 投資組合報告")
        report.append("=" * 70)
        report.append(f"  生成時間：{summary['timestamp']}")
        report.append("")
        report.append("📈 總覽")
        report.append("-" * 70)
        report.append(f"  總市值：${summary['total_value']:,.2f}")
        report.append(f"  總成本：${summary['total_cost']:,.2f}")
        report.append(f"  總損益：${summary['total_gain_loss']:,.2f} ({summary['total_gain_loss_percent']:+.2f}%)")
        report.append(f"  持股數：{summary['holdings_count']}")
        report.append("")
        report.append("📋 持股明細")
        report.append("-" * 70)
        
        # 按權重排序
        sorted_holdings = sorted(summary['holdings'], key=lambda x: x['weight'], reverse=True)
        
        for i, h in enumerate(sorted_holdings, 1):
            report.append(f"  {i}. {h['symbol']}")
            report.append(f"     股數：{h['shares']}")
            report.append(f"     平均成本：${h['avg_cost']:.2f}")
            report.append(f"     當前價：${h['current_price']:.2f}")
            report.append(f"     市值：${h['market_value']:,.2f} ({h['weight']:.1f}%)")
            report.append(f"     損益：${h['gain_loss']:,.2f} ({h['gain_loss_percent']:+.2f}%)")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)

    def save_portfolio(self):
        """保存投資組合到文件"""
        self.portfolio_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'initial_capital': self.initial_capital,
            'created_at': self.created_at,
            'updated_at': datetime.now().isoformat(),
            'holdings': [h.to_dict() for h in self.holdings],
        }
        
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_portfolio(self):
        """從文件加載投資組合"""
        if not self.portfolio_file.exists():
            return
        
        try:
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.initial_capital = data.get('initial_capital', 0.0)
            self.created_at = data.get('created_at')
            self.holdings = [Holding.from_dict(h) for h in data.get('holdings', [])]
            print(f"✓ 已加載 {len(self.holdings)} 個持股")
        except Exception as e:
            print(f"⚠ 加載投資組合失敗：{e}")
            self.holdings = []


def main():
    """測試投資組合功能"""
    print("=" * 70)
    print("  📊 投資組合追蹤測試")
    print("=" * 70)
    print()
    
    # 創建投資組合
    portfolio = Portfolio()
    
    # 添加測試持股
    print("📈 添加持股...")
    portfolio.add_holding('AAPL', 10, 150.0, '長期持有')
    portfolio.add_holding('MSFT', 5, 350.0, '科技龍頭')
    portfolio.add_holding('GOOGL', 8, 280.0, 'AI 概念')
    
    print(f"當前持股：{len(portfolio.holdings)} 個")
    for holding in portfolio.holdings:
        print(f"  • {holding.symbol}: {holding.shares}股 @ ${holding.avg_cost:.2f}")
    print()
    
    # 生成報告
    print("📋 生成報告...")
    report = portfolio.generate_report()
    print(report)
    
    print()
    print("=" * 70)
    print("  ✅ 測試完成！")
    print("=" * 70)


if __name__ == '__main__':
    main()
