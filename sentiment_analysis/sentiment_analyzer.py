"""
고급 감성 분석 모듈
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from collections import Counter
import numpy as np
import pandas as pd
from datetime import datetime

# 감성 분석 라이브러리
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

# 한국어 감성 분석을 위한 추가 라이브러리 (선택사항)
try:
    from konlpy.tag import Okt
    KOREAN_SUPPORT = True
except ImportError:
    KOREAN_SUPPORT = False
    print("한국어 지원을 위해 konlpy를 설치하세요: pip install konlpy")

# 주식/기술 관련 감성 사전
STOCK_SENTIMENT_DICT = {
    # 긍정적 키워드
    'positive': [
        'bullish', 'growth', 'profit', 'gain', 'rise', 'increase', 'up', 'high',
        'success', 'breakthrough', 'innovation', 'advancement', 'improvement',
        'strong', 'robust', 'solid', 'excellent', 'outstanding', 'amazing',
        'buy', 'purchase', 'invest', 'opportunity', 'potential', 'promising',
        'earnings', 'revenue', 'dividend', 'return', 'yield', 'performance'
    ],
    # 부정적 키워드
    'negative': [
        'bearish', 'decline', 'loss', 'fall', 'drop', 'decrease', 'down', 'low',
        'failure', 'problem', 'issue', 'concern', 'risk', 'threat', 'danger',
        'weak', 'poor', 'terrible', 'awful', 'disappointing', 'concerning',
        'sell', 'short', 'avoid', 'warning', 'caution', 'volatile', 'uncertain',
        'debt', 'loss', 'bankruptcy', 'crisis', 'recession', 'crash'
    ],
    # 기술 관련 키워드
    'tech_positive': [
        'breakthrough', 'innovation', 'revolutionary', 'cutting-edge', 'advanced',
        'efficient', 'scalable', 'reliable', 'secure', 'fast', 'powerful',
        'ai', 'machine learning', 'automation', 'optimization', 'enhancement',
        'upgrade', 'improvement', 'development', 'progress', 'evolution'
    ],
    'tech_negative': [
        'bug', 'error', 'failure', 'crash', 'vulnerability', 'security issue',
        'outdated', 'obsolete', 'slow', 'inefficient', 'unreliable', 'unstable',
        'hack', 'breach', 'leak', 'malware', 'virus', 'attack', 'exploit'
    ]
}

class AdvancedSentimentAnalyzer:
    """고급 감성 분석기"""
    
    def __init__(self, language='en'):
        self.language = language
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # 한국어 지원
        if language == 'ko' and KOREAN_SUPPORT:
            self.okt = Okt()
        else:
            self.okt = None
        
        # 감성 사전 로드
        self.sentiment_dict = STOCK_SENTIMENT_DICT
        
        # 감성 점수 가중치
        self.weights = {
            'vader': 0.4,
            'textblob': 0.3,
            'keyword': 0.3
        }
    
    def analyze_text(self, text: str, context: str = 'general') -> Dict:
        """텍스트 감성 분석"""
        if not text or not text.strip():
            return self._get_neutral_sentiment()
        
        # 전처리
        cleaned_text = self._preprocess_text(text)
        
        # 다양한 방법으로 감성 분석
        vader_score = self._analyze_vader(cleaned_text)
        textblob_score = self._analyze_textblob(cleaned_text)
        keyword_score = self._analyze_keywords(cleaned_text, context)
        
        # 가중 평균 계산
        final_score = self._calculate_weighted_score(
            vader_score, textblob_score, keyword_score
        )
        
        return {
            'text': text,
            'cleaned_text': cleaned_text,
            'vader_score': vader_score,
            'textblob_score': textblob_score,
            'keyword_score': keyword_score,
            'final_score': final_score,
            'sentiment': self._classify_sentiment(final_score['compound']),
            'confidence': self._calculate_confidence(vader_score, textblob_score, keyword_score),
            'keywords_found': self._extract_sentiment_keywords(cleaned_text),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # URL 제거
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 특수 문자 정리
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 소문자 변환
        text = text.lower().strip()
        
        return text
    
    def _analyze_vader(self, text: str) -> Dict:
        """VADER 감성 분석"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            return {
                'compound': scores['compound'],
                'positive': scores['pos'],
                'neutral': scores['neu'],
                'negative': scores['neg']
            }
        except Exception as e:
            print(f"VADER 분석 오류: {e}")
            return {'compound': 0.0, 'positive': 0.0, 'neutral': 1.0, 'negative': 0.0}
    
    def _analyze_textblob(self, text: str) -> Dict:
        """TextBlob 감성 분석"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # polarity를 compound 점수로 변환
            compound = polarity
            
            return {
                'compound': compound,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'positive': max(0, polarity),
                'negative': max(0, -polarity),
                'neutral': 1 - abs(polarity)
            }
        except Exception as e:
            print(f"TextBlob 분석 오류: {e}")
            return {'compound': 0.0, 'polarity': 0.0, 'subjectivity': 0.5, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def _analyze_keywords(self, text: str, context: str) -> Dict:
        """키워드 기반 감성 분석"""
        words = text.split()
        positive_count = 0
        negative_count = 0
        total_words = len(words)
        
        if total_words == 0:
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
        
        # 컨텍스트별 키워드 선택
        if context == 'stock':
            pos_keywords = self.sentiment_dict['positive'] + self.sentiment_dict['tech_positive']
            neg_keywords = self.sentiment_dict['negative'] + self.sentiment_dict['tech_negative']
        elif context == 'tech':
            pos_keywords = self.sentiment_dict['tech_positive']
            neg_keywords = self.sentiment_dict['tech_negative']
        else:
            pos_keywords = self.sentiment_dict['positive']
            neg_keywords = self.sentiment_dict['negative']
        
        # 키워드 매칭
        for word in words:
            if word in pos_keywords:
                positive_count += 1
            elif word in neg_keywords:
                negative_count += 1
        
        # 점수 계산
        pos_ratio = positive_count / total_words
        neg_ratio = negative_count / total_words
        compound = pos_ratio - neg_ratio
        
        return {
            'compound': compound,
            'positive': pos_ratio,
            'negative': neg_ratio,
            'neutral': 1 - pos_ratio - neg_ratio
        }
    
    def _calculate_weighted_score(self, vader: Dict, textblob: Dict, keyword: Dict) -> Dict:
        """가중 평균 점수 계산"""
        compound = (
            vader['compound'] * self.weights['vader'] +
            textblob['compound'] * self.weights['textblob'] +
            keyword['compound'] * self.weights['keyword']
        )
        
        positive = (
            vader['positive'] * self.weights['vader'] +
            textblob['positive'] * self.weights['textblob'] +
            keyword['positive'] * self.weights['keyword']
        )
        
        negative = (
            vader['negative'] * self.weights['vader'] +
            textblob['negative'] * self.weights['textblob'] +
            keyword['negative'] * self.weights['keyword']
        )
        
        neutral = 1 - positive - negative
        
        return {
            'compound': compound,
            'positive': positive,
            'negative': negative,
            'neutral': neutral
        }
    
    def _classify_sentiment(self, compound_score: float) -> str:
        """감성 분류"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_confidence(self, vader: Dict, textblob: Dict, keyword: Dict) -> float:
        """신뢰도 계산"""
        # 각 방법의 일치도 계산
        vader_sentiment = self._classify_sentiment(vader['compound'])
        textblob_sentiment = self._classify_sentiment(textblob['compound'])
        keyword_sentiment = self._classify_sentiment(keyword['compound'])
        
        sentiments = [vader_sentiment, textblob_sentiment, keyword_sentiment]
        most_common = Counter(sentiments).most_common(1)[0][1]
        
        # 일치하는 방법의 비율
        confidence = most_common / len(sentiments)
        
        return confidence
    
    def _extract_sentiment_keywords(self, text: str) -> Dict:
        """감성 키워드 추출"""
        words = text.split()
        found_keywords = {
            'positive': [],
            'negative': [],
            'tech_positive': [],
            'tech_negative': []
        }
        
        for word in words:
            for category, keywords in self.sentiment_dict.items():
                if word in keywords:
                    found_keywords[category].append(word)
        
        return found_keywords
    
    def _get_neutral_sentiment(self) -> Dict:
        """중립 감성 반환"""
        return {
            'text': '',
            'cleaned_text': '',
            'vader_score': {'compound': 0.0, 'positive': 0.0, 'neutral': 1.0, 'negative': 0.0},
            'textblob_score': {'compound': 0.0, 'polarity': 0.0, 'subjectivity': 0.5, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0},
            'keyword_score': {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0},
            'final_score': {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0},
            'sentiment': 'neutral',
            'confidence': 0.0,
            'keywords_found': {'positive': [], 'negative': [], 'tech_positive': [], 'tech_negative': []},
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def analyze_batch(self, texts: List[str], contexts: List[str] = None) -> List[Dict]:
        """배치 감성 분석"""
        if contexts is None:
            contexts = ['general'] * len(texts)
        
        results = []
        for text, context in zip(texts, contexts):
            result = self.analyze_text(text, context)
            results.append(result)
        
        return results
    
    def get_sentiment_summary(self, results: List[Dict]) -> Dict:
        """감성 분석 결과 요약"""
        if not results:
            return {'error': 'No results to summarize'}
        
        sentiments = [r['sentiment'] for r in results]
        sentiment_counts = Counter(sentiments)
        
        total = len(results)
        positive_ratio = sentiment_counts.get('positive', 0) / total
        negative_ratio = sentiment_counts.get('negative', 0) / total
        neutral_ratio = sentiment_counts.get('neutral', 0) / total
        
        # 평균 점수
        avg_compound = np.mean([r['final_score']['compound'] for r in results])
        avg_confidence = np.mean([r['confidence'] for r in results])
        
        return {
            'total_texts': total,
            'sentiment_distribution': dict(sentiment_counts),
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'neutral_ratio': neutral_ratio,
            'average_compound_score': avg_compound,
            'average_confidence': avg_confidence,
            'overall_sentiment': self._classify_sentiment(avg_compound)
        }


def main():
    """테스트 함수"""
    analyzer = AdvancedSentimentAnalyzer()
    
    # 테스트 텍스트
    test_texts = [
        "This AI breakthrough is amazing! The stock price will definitely go up.",
        "The company reported terrible earnings and the stock crashed.",
        "The new machine learning algorithm shows promising results.",
        "Security vulnerability found in the system, investors are concerned.",
        "Neutral news about the technology sector."
    ]
    
    print("🔍 감성 분석 테스트")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. 텍스트: {text}")
        result = analyzer.analyze_text(text, context='stock')
        print(f"   감성: {result['sentiment']}")
        print(f"   점수: {result['final_score']['compound']:.3f}")
        print(f"   신뢰도: {result['confidence']:.3f}")
        print(f"   키워드: {result['keywords_found']}")
    
    # 배치 분석
    print("\n" + "=" * 50)
    print("📊 배치 분석 결과")
    
    batch_results = analyzer.analyze_batch(test_texts, ['stock'] * len(test_texts))
    summary = analyzer.get_sentiment_summary(batch_results)
    
    print(f"총 텍스트 수: {summary['total_texts']}")
    print(f"감성 분포: {summary['sentiment_distribution']}")
    print(f"긍정 비율: {summary['positive_ratio']:.1%}")
    print(f"부정 비율: {summary['negative_ratio']:.1%}")
    print(f"중립 비율: {summary['neutral_ratio']:.1%}")
    print(f"평균 점수: {summary['average_compound_score']:.3f}")
    print(f"전체 감성: {summary['overall_sentiment']}")


if __name__ == '__main__':
    main()

