"""
郵件通知模組
支援 SMTP 和 Microsoft Graph API 發送郵件
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class EmailConfig:
    """郵件配置"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', '')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.smtp_from = os.getenv('SMTP_FROM', self.smtp_user)
        
        self.use_graph = os.getenv('USE_GRAPH_EMAIL', 'true').lower() == 'true'
    
    @property
    def smtp_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)


class EmailTemplate:
    """郵件範本"""
    
    def __init__(self, template_dir: Optional[Path] = None):
        if template_dir is None:
            template_dir = Path(__file__).parent / 'templates'
        self.template_dir = template_dir
    
    def render(self, template_name: str, variables: Dict) -> str:
        """渲染郵件範本"""
        template_path = self.template_dir / f"{template_name}.html"
        
        if not template_path.exists():
            return self._default_template(template_name, variables)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        
        return content
    
    def _default_template(self, name: str, variables: Dict) -> str:
        """預設範本"""
        if name == 'daily_report':
            return self._daily_report_template(variables)
        elif name == 'price_alert':
            return self._price_alert_template(variables)
        elif name == 'news_summary':
            return self._news_summary_template(variables)
        return variables.get('content', '')
    
    def _daily_report_template(self, vars: Dict) -> str:
        return f"""
<html>
<body>
<h2>📊 每日投資報告 - {vars.get('date', '')}</h2>
<h3>投資組合表現</h3>
<table border="1" cellpadding="5">
<tr><th>股票</th><th>價格</th><th>漲跌</th></tr>
{vars.get('stocks_html', '')}
</table>
<h3>總結</h3>
<p>{vars.get('summary', '')}</p>
<hr>
<small>由 InvestSight 自動產生</small>
</body>
</html>
"""
    
    def _price_alert_template(self, vars: Dict) -> str:
        return f"""
<html>
<body>
<h2>⚠️ 價格警報</h2>
<p><strong>{vars.get('symbol', '')}</strong> 價格變動達到閾值</p>
<ul>
<li>當前價格: ${vars.get('price', '')}</li>
<li>變動: {vars.get('change', '')}</li>
<li>時間: {vars.get('time', '')}</li>
</ul>
</body>
</html>
"""
    
    def _news_summary_template(self, vars: Dict) -> str:
        return f"""
<html>
<body>
<h2>📰 新聞摘要 - {vars.get('date', '')}</h2>
{vars.get('articles_html', '')}
<hr>
<small>由 InvestSight 自動產生</small>
</body>
</html>
"""


class SMTPEmailSender:
    """SMTP 郵件發送器"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
    
    def send(self, to: str, subject: str, body: str, html: bool = True) -> bool:
        """發送郵件"""
        if not self.config.smtp_enabled:
            print("⚠ SMTP 未配置")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.smtp_from
            msg['To'] = to
            msg['Subject'] = subject
            msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            if html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)
            
            print(f"✓ SMTP 郵件已發送到: {to}")
            return True
            
        except Exception as e:
            print(f"✗ SMTP 發送失敗: {e}")
            return False


class GraphEmailSender:
    """Microsoft Graph API 郵件發送器"""
    
    def __init__(self, graph_client=None):
        self.graph_client = graph_client
    
    async def send(self, to: str, subject: str, body: str, html: bool = True) -> bool:
        """通過 Graph API 發送郵件"""
        if not self.graph_client:
            print("⚠ Graph client 未初始化，嘗試使用現有客戶端")
            from storage.graph_api import get_graph_client
            self.graph_client = get_graph_client()
            self.graph_client.authenticate(use_cache=True)
        
        try:
            return await self.graph_client.send_email(subject, body, to)
        except Exception as e:
            print(f"✗ Graph API 發送失敗: {e}")
            return False


class EmailNotifier:
    """郵件通知器"""
    
    def __init__(self, graph_client=None):
        self.config = EmailConfig()
        self.template = EmailTemplate()
        self.smtp_sender = SMTPEmailSender(self.config)
        self.graph_sender = GraphEmailSender(graph_client)
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = True,
        use_smtp: bool = False
    ) -> bool:
        """發送郵件"""
        if use_smtp or not self.config.use_graph:
            return self.smtp_sender.send(to, subject, body, html)
        else:
            import asyncio
            return asyncio.run(self.graph_sender.send(to, subject, body, html))
    
    def send_daily_report(
        self,
        to: str,
        stocks: List[Dict],
        summary: str = ""
    ) -> bool:
        """發送每日報告"""
        stocks_html = "".join(
            f"<tr><td>{s['symbol']}</td><td>${s.get('price', 'N/A')}</td>"
            f"<td>{s.get('change_percent', 0):+.2f}%</td></tr>"
            for s in stocks
        )
        
        variables = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'stocks_html': stocks_html,
            'summary': summary or '今日市場波動較大，請關注您的投資組合。',
        }
        
        html = self.template.render('daily_report', variables)
        subject = f"📊 每日投資報告 - {variables['date']}"
        
        return self.send_email(to, subject, html)
    
    def send_price_alert(
        self,
        to: str,
        symbol: str,
        price: float,
        change: float
    ) -> bool:
        """發送價格警報"""
        variables = {
            'symbol': symbol,
            'price': f"{price:.2f}",
            'change': f"{change:+.2f}%",
            'time': datetime.now().strftime('%H:%M:%S'),
        }
        
        html = self.template.render('price_alert', variables)
        subject = f"⚠️ 價格警報: {symbol}"
        
        return self.send_email(to, subject, html)
    
    def send_news_summary(
        self,
        to: str,
        articles: List[Dict]
    ) -> bool:
        """發送新聞摘要"""
        articles_html = "".join(
            f"<li><a href='{a.get('link', '')}'>{a.get('title', '')}</a></li>"
            for a in articles[:10]
        )
        
        variables = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'articles_html': f"<ul>{articles_html}</ul>",
        }
        
        html = self.template.render('news_summary', variables)
        subject = f"📰 新聞摘要 - {variables['date']}"
        
        return self.send_email(to, subject, html)


notifier = EmailNotifier()


def send_email(to: str, subject: str, body: str) -> bool:
    """便捷函數"""
    return notifier.send_email(to, subject, body)


def send_daily_report(to: str, stocks: List[Dict], summary: str = "") -> bool:
    """便捷函數"""
    return notifier.send_daily_report(to, stocks, summary)


if __name__ == '__main__':
    print("📧 郵件通知模組測試")
    print(f"SMTP 配置: {'已配置' if EmailConfig().smtp_enabled else '未配置'}")
    print(f"Graph API: {'啟用' if EmailConfig().use_graph else '禁用'}")
