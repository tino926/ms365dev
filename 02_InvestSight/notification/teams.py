"""
Teams 通知模組
支援 Webhook 和 Graph API 發送通知
"""
import os
import json
import requests
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class TeamsWebhookSender:
    """Teams Incoming Webhook 發送器"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv('TEAMS_WEBHOOK_URL', '')
    
    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
    def send(self, message: str, title: str = "InvestSight") -> bool:
        """發送簡單訊息"""
        if not self.is_configured:
            print("⚠️ Teams Webhook 未配置")
            return False
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "facts": [],
                "markdown": True
            }],
            "text": message
        }
        
        return self._send_payload(payload)
    
    def send_card(self, title: str, text: str, facts: List[Dict] = None,
                  theme_color: str = "0076D7", buttons: List[Dict] = None) -> bool:
        """發送卡片訊息"""
        if not self.is_configured:
            print("⚠️ Teams Webhook 未配置")
            return False
        
        section = {
            "activityTitle": title,
            "activitySubtitle": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "markdown": True,
        }
        
        if facts:
            section["facts"] = [{"name": k, "value": v} for k, v in facts]
        
        if text:
            section["text"] = text
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": theme_color,
            "summary": title,
            "sections": [section],
        }
        
        if buttons:
            payload["potentialAction"] = [
                {
                    "@type": "OpenUri",
                    "name": btn["name"],
                    "targets": [{"os": "default", "uri": btn["url"]}]
                }
                for btn in buttons
            ]
        
        return self._send_payload(payload)
    
    def send_adaptive_card(self, card: dict) -> bool:
        """發送 Adaptive Card"""
        if not self.is_configured:
            print("⚠️ Teams Webhook 未配置")
            return False
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card
            }]
        }
        
        return self._send_payload(payload)
    
    def _send_payload(self, payload: dict) -> bool:
        """發送 payload"""
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✓ Teams 訊息已發送")
                return True
            else:
                print(f"✗ Teams 發送失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Teams 發送錯誤: {e}")
            return False
    
    def send_price_alert(self, symbol: str, price: float, change: float) -> bool:
        """發送價格警報"""
        color = "FF0000" if change < 0 else "00FF00"
        facts = [
            ("股票", symbol),
            ("價格", f"${price:.2f}"),
            ("變動", f"{change:+.2f}%"),
            ("時間", datetime.now().strftime("%H:%M:%S")),
        ]
        
        return self.send_card(
            title=f"⚠️ 價格警報: {symbol}",
            text=f"{symbol} 價格變動達到閾值",
            facts=facts,
            theme_color=color
        )
    
    def send_daily_summary(self, stocks: List[Dict]) -> bool:
        """發送每日摘要"""
        facts = []
        for stock in stocks[:5]:
            change = stock.get('change_percent', 0)
            symbol = stock.get('symbol', '')
            price = stock.get('price', 0)
            facts.append((symbol, f"${price:.2f} ({change:+.2f}%)"))
        
        return self.send_card(
            title="📊 每日投資摘要",
            text="今日市場概覽",
            facts=facts,
            theme_color="0076D7"
        )
    
    def send_news_alert(self, title: str, link: str, sentiment: str = "neutral") -> bool:
        """發送新聞警報"""
        colors = {
            "positive": "00FF00",
            "negative": "FF0000", 
            "neutral": "FFFF00"
        }
        
        return self.send_card(
            title=f"📰 新聞: {title[:50]}...",
            text="點擊查看詳情",
            theme_color=colors.get(sentiment, "0076D7"),
            buttons=[{"name": "查看新聞", "url": link}]
        )


class TeamsGraphSender:
    """Teams Graph API 發送器"""
    
    def __init__(self, graph_client=None):
        self.graph_client = graph_client
    
    def _ensure_client(self):
        if not self.graph_client:
            from storage.graph_api import get_graph_client
            self.graph_client = get_graph_client()
            self.graph_client.authenticate(use_cache=True)
    
    async def send_to_channel(self, team_id: str, channel_id: str, 
                                message: str) -> bool:
        """發送到頻道"""
        self._ensure_client()
        
        try:
            from msgraph.generated.models.chat_message import ChatMessage
            from msgraph.generated.models.item_body import ItemBody
            from msgraph.generated.models.body_type import BodyType
            
            chat_message = ChatMessage()
            chat_message.body = ItemBody()
            chat_message.body.content_type = BodyType.Html
            chat_message.body.content = message
            
            await self.graph_client.teams.by_team_id(team_id).channels.by_channel_id(
                channel_id
            ).messages.post(chat_message)
            
            print(f"✓ Teams 訊息已發送到頻道")
            return True
            
        except Exception as e:
            print(f"✗ Teams 發送失敗: {e}")
            return False
    
    async def send_to_chat(self, chat_id: str, message: str) -> bool:
        """發送到聊天"""
        self._ensure_client()
        
        try:
            from msgraph.generated.models.chat_message import ChatMessage
            from msgraph.generated.models.item_body import ItemBody
            from msgraph.generated.models.body_type import BodyType
            
            chat_message = ChatMessage()
            chat_message.body = ItemBody()
            chat_message.body.content_type = BodyType.Text
            chat_message.body.content = message
            
            await self.graph_client.chats.by_chat_id(chat_id).messages.post(chat_message)
            
            print(f"✓ Teams 訊息已發送到聊天")
            return True
            
        except Exception as e:
            print(f"✗ Teams 發送失敗: {e}")
            return False


class TeamsNotifier:
    """Teams 通知器"""
    
    def __init__(self, graph_client=None):
        self.webhook = TeamsWebhookSender()
        self.graph = TeamsGraphSender(graph_client)
    
    def send(self, message: str, title: str = "InvestSight") -> bool:
        """發送訊息"""
        return self.webhook.send(message, title)
    
    def send_card(self, title: str, text: str, facts: List[Dict] = None) -> bool:
        """發送卡片"""
        return self.webhook.send_card(title, text, facts)
    
    def send_price_alert(self, symbol: str, price: float, change: float) -> bool:
        """發送價格警報"""
        return self.webhook.send_price_alert(symbol, price, change)
    
    def send_daily_summary(self, stocks: List[Dict]) -> bool:
        """發送每日摘要"""
        return self.webhook.send_daily_summary(stocks)


notifier = TeamsNotifier()


def send_teams(message: str, title: str = "InvestSight") -> bool:
    """便捷函數"""
    return notifier.send(message, title)


def send_price_alert(symbol: str, price: float, change: float) -> bool:
    """便捷函數"""
    return notifier.send_price_alert(symbol, price, change)


if __name__ == '__main__':
    print("💬 Teams 通知模組")
    notifier = TeamsNotifier()
    print(f"Webhook: {'已配置' if notifier.webhook.is_configured else '未配置'}")
