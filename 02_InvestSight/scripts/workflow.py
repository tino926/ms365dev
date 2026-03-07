#!/usr/bin/env python3
"""
InvestSight 自動化工作流
每日/每週自動執行：數據抓取 → 報告生成 → 通知發送
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.chdir(Path(__file__).resolve().parent.parent)

import argparse
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def run_daily_workflow(send_email: bool = False, send_teams: bool = False, recipient: str = ""):
    """每日工作流"""
    print("=" * 60)
    print("📅 InvestSight 每日工作流")
    print(f"   時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'stocks': None,
        'news': None,
        'reports': None,
        'email': None,
        'teams': None,
    }
    
    # 1. 抓取股票數據
    print("\n[1/5] 📊 抓取股票數據...")
    try:
        from data.finance_api import fetcher
        stocks = fetcher.fetch_all_stocks()
        results['stocks'] = {
            'count': len(stocks),
            'data': stocks
        }
        for s in stocks:
            print(f"   {s['symbol']:6} \${s['price']:7.2f} {s['change_percent']:+6.2f}%")
        print(f"   ✅ 成功抓取 {len(stocks)} 支股票")
    except Exception as e:
        print(f"   ❌ 失敗: {e}")
    
    # 2. 抓取新聞
    print("\n[2/5] 📰 抓取新聞...")
    try:
        from data.news_api import fetcher
        articles = fetcher.fetch_all()
        results['news'] = {
            'count': len(articles),
            'data': articles
        }
        print(f"   ✅ 成功抓取 {len(articles)} 篇新聞")
    except Exception as e:
        print(f"   ❌ 失敗: {e}")
    
    # 3. 情感分析
    print("\n[3/5] 🧠 情感分析...")
    try:
        from analysis.sentiment import analyzer
        if articles:
            analyzed = analyzer.analyze_articles(articles)
            positive = sum(1 for a in analyzed if a.get('sentiment', {}).get('sentiment') == 'positive')
            negative = sum(1 for a in analyzed if a.get('sentiment', {}).get('sentiment') == 'negative')
            neutral = len(analyzed) - positive - negative
            print(f"   ✅ 正面: {positive} | 負面: {negative} | 中性: {neutral}")
            
            if positive > negative:
                summary = "市場情緒偏向正面"
            elif negative > positive:
                summary = "市場情緒偏向負面"
            else:
                summary = "市場情緒中性"
            print(f"   📝 總結: {summary}")
    except Exception as e:
        print(f"   ❌ 失敗: {e}")
    
    # 4. 生成報告
    print("\n[4/5] 📈 生成報告...")
    try:
        from report import generate_weekly_report
        report_files = generate_weekly_report()
        results['reports'] = report_files
        print(f"   ✅ 報告已生成: {report_files.get('html', 'N/A')}")
    except Exception as e:
        print(f"   ❌ 失敗: {e}")
    
    # 5. 發送通知
    if send_email or send_teams:
        print("\n[5/5] 📧 發送通知...")
        
        if send_email and recipient:
            try:
                from notification import send_daily_report
                success = send_daily_report(recipient, stocks or [], summary)
                results['email'] = 'success' if success else 'failed'
                print(f"   ✅ 郵件已發送" if success else f"   ❌ 郵件發送失敗")
            except Exception as e:
                print(f"   ❌ 郵件錯誤: {e}")
                results['email'] = f'error: {e}'
        
        if send_teams:
            try:
                from notification import teams_notifier
                teams_notifier.send_daily_summary(stocks or [])
                results['teams'] = 'success'
                print(f"   ✅ Teams 通知已發送")
            except Exception as e:
                print(f"   ❌ Teams 錯誤: {e}")
                results['teams'] = f'error: {e}'
    else:
        print("\n[5/5] ⏭️ 跳過通知（未配置）")
    
    # 完成
    print("\n" + "=" * 60)
    print("✅ 每日工作流完成!")
    print("=" * 60)
    
    return results


def run_weekly_workflow():
    """每週工作流"""
    print("=" * 60)
    print("📅 InvestSight 每週工作流")
    print(f"   時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
    }
    
    # 1. 完整數據抓取
    print("\n[1/4] 📊 抓取一週數據...")
    from data.finance_api import fetcher
    stocks = fetcher.fetch_all_stocks()
    from data.news_api import fetcher
    articles = fetcher.fetch_all()
    print(f"   ✅ 股票: {len(stocks)}, 新聞: {len(articles)}")
    results['data'] = {'stocks': len(stocks), 'news': len(articles)}
    
    # 2. 技術分析
    print("\n[2/4] 📈 技術指標分析...")
    from analysis.technical_indicators import analyze_stock
    for stock in stocks[:3]:
        try:
            indicators = analyze_stock(stock['symbol'])
            print(f"   {stock['symbol']}: RSI={indicators.get('rsi', 'N/A')}")
        except:
            pass
    print("   ✅ 分析完成")
    
    # 3. 生成週報
    print("\n[3/4] 📋 生成每週報告...")
    from report import generate_weekly_report
    report_files = generate_weekly_report()
    print(f"   ✅ 報告: {report_files.get('html', 'N/A')}")
    results['reports'] = report_files
    
    # 4. 發送每週摘要
    print("\n[4/4] 📧 發送每週摘要...")
    from notification import teams_notifier
    try:
        teams_notifier.send_daily_summary(stocks)
        print("   ✅ Teams 通知已發送")
    except Exception as e:
        print(f"   ⚠️ Teams 未配置: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 每週工作流完成!")
    print("=" * 60)
    
    return results


def save_results(results: dict, workflow_type: str = "daily"):
    """保存結果到 JSON"""
    output_dir = Path("data/logs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{workflow_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"📁 結果已保存: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description='InvestSight 自動化工作流')
    parser.add_argument('--type', '-t', choices=['daily', 'weekly', 'both'], 
                        default='daily', help='工作流類型')
    parser.add_argument('--email', '-e', type=str, default='',
                        help='發送郵件到指定地址')
    parser.add_argument('--teams', '-T', action='store_true',
                        help='發送 Teams 通知')
    parser.add_argument('--save', '-s', action='store_true',
                        help='保存結果到 JSON')
    
    args = parser.parse_args()
    
    recipient = args.email
    send_email = bool(recipient)
    send_teams = args.teams
    
    if args.type in ['daily', 'both']:
        results = run_daily_workflow(send_email, send_teams, recipient)
        if args.save:
            save_results(results, 'daily')
    
    if args.type in ['weekly', 'both']:
        results = run_weekly_workflow()
        if args.save:
            save_results(results, 'weekly')


if __name__ == '__main__':
    main()
