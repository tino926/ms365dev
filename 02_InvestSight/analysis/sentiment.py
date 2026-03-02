"""
情感分析模塊
分析新聞情感（正面/負面/中性）
"""
from textblob import TextBlob
from typing import List, Dict

class SentimentAnalyzer:
    """情感分析器"""
    
    def analyze_text(self, text: str) -> Dict:
        """分析單段文本的情感"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 到 1
            
            # 判斷情感類別
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'polarity': polarity,
                'sentiment': sentiment,
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
    # 測試
    test_text = "Apple stock surges on strong earnings report"
    result = analyzer.analyze_text(test_text)
    print(f"情感：{result['sentiment']}, 極性：{result['polarity']:.2f}")
