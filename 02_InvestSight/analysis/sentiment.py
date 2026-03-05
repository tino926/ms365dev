"""
情感分析模塊
分析新聞情感（正面/負面/中性）
"""
from textblob import TextBlob
from typing import List, Dict

NEGATIVE_KEYWORDS = [
    'war', 'iran', 'israel', 'attack', 'conflict', 'crisis', 'fear',
    'plunge', 'crash', 'lose', 'fall', 'drop', 'miss', 'misses',
    'decline', 'decline', 'sinks', 'slump', 'slumps', 'tumble',
    'worse', 'worst', 'danger', 'threat', 'risk', 'warn', 'warning',
    'fail', 'failure', 'lose', 'loss', 'lost', 'death', 'dead',
    'recession', 'inflation', 'stagflation', 'bankruptcy', 'lawsuit',
    'scandal', 'fraud', 'investigation', 'probe', 'fired', 'layoff',
    'strike', 'terror', 'military', 'bomb', 'explosion', 'casualties',
    'geopolitical', 'tension', 'uncertainty', 'volatility', 'selloff',
    'sell-off', 'pullback', 'correction', 'bear market', 'recession'
]

POSITIVE_KEYWORDS = [
    'surge', 'surges', 'soar', 'soars', 'gain', 'gains', 'rise', 'rises',
    'grow', 'grows', 'growth', 'bull', 'rally', 'rallies', 'boom',
    'success', 'successful', 'beat', 'beats', 'exceed', 'exceeds',
    'record', 'high', 'highs', 'breakthrough', 'innovation', 'innovative',
    'profit', 'profits', 'up', 'higher', 'best', 'strong', 'strength',
    'opportunity', 'profit', 'winning', 'winner', 'upgrade', 'outperform'
]


class SentimentAnalyzer:
    """情感分析器"""
    
    def __init__(self, threshold: float = 0.05):
        self.threshold = threshold
    
    def _keyword_analysis(self, text: str) -> Dict:
        """基於關鍵詞的情感分析"""
        text_lower = text.lower()
        
        neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
        pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
        
        if neg_count > pos_count and neg_count >= 1:
            return {
                'sentiment': 'negative',
                'polarity': -0.3,
                'keyword_trigger': 'negative',
                'neg_count': neg_count,
                'pos_count': pos_count
            }
        elif pos_count > neg_count and pos_count >= 1:
            return {
                'sentiment': 'positive',
                'polarity': 0.3,
                'keyword_trigger': 'positive',
                'neg_count': neg_count,
                'pos_count': pos_count
            }
        
        return None
    
    def analyze_text(self, text: str) -> Dict:
        """分析單段文本的情感"""
        try:
            keyword_result = self._keyword_analysis(text)
            
            if keyword_result:
                return keyword_result
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > self.threshold:
                sentiment = 'positive'
            elif polarity < -self.threshold:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'polarity': polarity,
                'sentiment': sentiment,
                'keyword_trigger': None,
            }
        except Exception as e:
            print(f"情感分析失敗：{e}")
            return {'polarity': 0, 'sentiment': 'neutral'}
    
    def analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """分析多篇新聞的情感"""
        for article in articles:
            text = f"{article['title']} {article.get('summary', '')}"
            article['sentiment'] = self.analyze_text(text)
        return articles


analyzer = SentimentAnalyzer()


if __name__ == '__main__':
    test_cases = [
        "War in Middle East escalates, markets fall",
        "Stock surges to record high on earnings beat",
        "Mortgage rates jump as Iran strikes stoke inflation",
        "Best personal loans for March 2026",
        "Soybeans Falls Lower on Monday with Geopolitical Uncertainty",
        "Salesforce CEO touts company resilience amid software slump",
    ]
    
    for text in test_cases:
        result = analyzer.analyze_text(text)
        trigger = result.get('keyword_trigger', '')
        flag = '🔑' if trigger else ''
        print(f"{flag} [{result['sentiment']:8}] ({result['polarity']:+.2f}) {text[:50]}...")
