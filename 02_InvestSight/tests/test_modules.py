"""
單元測試：數據模組
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestFinanceDataFetcher:
    """測試金融數據抓取"""
    
    @patch('data.finance_api.yf.Ticker')
    def test_get_stock_price(self, mock_ticker):
        """測試獲取股票價格"""
        mock_instance = Mock()
        mock_instance.info = {
            'currentPrice': 150.0,
            'regularMarketChange': 2.5,
            'regularMarketChangePercent': 1.7
        }
        mock_ticker.return_value = mock_instance
        
        from data.finance_api import FinanceDataFetcher
        fetcher = FinanceDataFetcher()
        result = fetcher.get_stock_price('AAPL')
        
        assert result is not None
        assert result['symbol'] == 'AAPL'
        assert result['price'] == 150.0
    
    @patch('data.finance_api.yf.Ticker')
    def test_get_stock_price_error(self, mock_ticker):
        """測試股票價格獲取錯誤"""
        mock_ticker.side_effect = Exception("Network error")
        
        from data.finance_api import FinanceDataFetcher
        fetcher = FinanceDataFetcher()
        result = fetcher.get_stock_price('INVALID')
        
        assert result is None


class TestSentimentAnalyzer:
    """測試情感分析"""
    
    def test_analyze_text_positive(self):
        """測試正面情感"""
        from analysis.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze_text("Great earnings report, stock surges!")
        
        assert result['sentiment'] == 'positive'
        assert result['polarity'] > 0
    
    def test_analyze_text_negative(self):
        """測試負面情感"""
        from analysis.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze_text("Terrible losses, stock crashes!")
        
        assert result['sentiment'] == 'negative'
        assert result['polarity'] < 0
    
    def test_analyze_text_neutral(self):
        """測試中性情感"""
        from analysis.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        result = analyzer.analyze_text("The meeting is scheduled for tomorrow.")
        
        assert result['sentiment'] == 'neutral'
    
    def test_analyze_articles(self):
        """測試多篇文章分析"""
        from analysis.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        
        articles = [
            {'title': 'Good news', 'summary': 'Stock up'},
            {'title': 'Bad news', 'summary': 'Stock down'},
        ]
        
        result = analyzer.analyze_articles(articles)
        
        assert len(result) == 2
        assert 'sentiment' in result[0]
        assert 'sentiment' in result[1]


class TestNewsFetcher:
    """測試新聞抓取"""
    
    @patch('data.news_api.feedparser.parse')
    def test_fetch_rss(self, mock_parse):
        """測試 RSS 抓取"""
        mock_feed = Mock()
        mock_feed.entries = [
            Mock(title='Test News', link='http://test.com', 
                 published='2024-01-01', summary='Test summary')
        ]
        mock_feed.feed = {'title': 'Test Feed'}
        mock_parse.return_value = mock_feed
        
        from data.news_api import NewsFetcher
        fetcher = NewsFetcher()
        result = fetcher.fetch_rss('http://test.com')
        
        assert len(result) == 1
        assert result[0]['title'] == 'Test News'
    
    @patch('data.news_api.feedparser.parse')
    def test_fetch_all(self, mock_parse):
        """測試抓取所有新聞源"""
        mock_feed = Mock()
        mock_feed.entries = []
        mock_feed.feed = {'title': 'Test'}
        mock_parse.return_value = mock_feed
        
        from data.news_api import NewsFetcher
        fetcher = NewsFetcher()
        fetcher.rss_feeds = ['http://test.com']
        
        result = fetcher.fetch_all()
        
        assert isinstance(result, list)


class TestEmailConfig:
    """測試郵件配置"""
    
    def test_email_config_defaults(self):
        """測試預設配置"""
        from notification.email import EmailConfig
        
        config = EmailConfig()
        
        assert config.smtp_port == 587
        assert config.use_graph == True
    
    @patch.dict('os.environ', {'SMTP_HOST': 'smtp.test.com', 'SMTP_USER': 'test@test.com', 'SMTP_PASSWORD': 'pass'})
    def test_email_config_loaded(self):
        """測試環境變數加載"""
        from notification.email import EmailConfig
        
        config = EmailConfig()
        
        assert config.smtp_host == 'smtp.test.com'
        assert config.smtp_user == 'test@test.com'
        assert config.smtp_enabled == True


class TestTeamsWebhook:
    """測試 Teams Webhook"""
    
    def test_teams_webhook_not_configured(self):
        """測試未配置"""
        from notification.teams import TeamsWebhookSender
        
        sender = TeamsWebhookSender(webhook_url='')
        
        assert sender.is_configured == False
    
    def test_teams_webhook_configured(self):
        """測試已配置"""
        from notification.teams import TeamsWebhookSender
        
        sender = TeamsWebhookSender(webhook_url='https://test.webhook.com')
        
        assert sender.is_configured == True


class TestReportGenerator:
    """測試週報生成器"""
    
    def test_generate_text(self):
        """測試文字報告生成"""
        from report.weekly import WeeklyReportGenerator
        
        generator = WeeklyReportGenerator()
        generator.data = {
            'stocks': [
                {'symbol': 'AAPL', 'price': 150.0, 'change_percent': 1.5}
            ],
            'sentiment_summary': {
                'positive': 5, 'negative': 2, 'neutral': 3,
                'positive_pct': 50, 'negative_pct': 20, 'neutral_pct': 30
            },
            'week_summary': 'Test summary'
        }
        
        text = generator.generate_text()
        
        assert 'AAPL' in text
        assert '150.00' in text
        assert 'Test summary' in text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
