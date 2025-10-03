"""
기술 트렌드 분석 모듈
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import json
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class TrendAnalyzer:
    """기술 트렌드 분석기"""
    
    def __init__(self, data_source='mongodb'):
        self.data_source = data_source
        self.tech_keywords = [
            'AI', 'artificial intelligence', 'machine learning', 'deep learning',
            'NLP', 'computer vision', 'blockchain', 'cryptocurrency',
            'cloud computing', 'edge computing', 'quantum computing',
            'IoT', '5G', 'autonomous vehicles', 'robotics',
            'AR', 'VR', 'metaverse', 'NFT',
            'cybersecurity', 'data science', 'big data',
            'microservices', 'kubernetes', 'docker',
            'python', 'javascript', 'react', 'node.js',
            'tensorflow', 'pytorch', 'openai', 'chatgpt'
        ]
        
        self.stock_keywords = [
            'stock', 'share', 'equity', 'investment', 'portfolio',
            'earnings', 'revenue', 'profit', 'growth', 'valuation',
            'IPO', 'merger', 'acquisition', 'dividend', 'buyback'
        ]
    
    def load_data(self, collection_name: str, days: int = 7) -> pd.DataFrame:
        """데이터 로드"""
        if self.data_source == 'mongodb':
            return self._load_from_mongodb(collection_name, days)
        elif self.data_source == 'postgresql':
            return self._load_from_postgresql(collection_name, days)
        else:
            raise ValueError(f"Unsupported data source: {self.data_source}")
    
    def _load_from_mongodb(self, collection_name: str, days: int) -> pd.DataFrame:
        """MongoDB에서 데이터 로드"""
        from pymongo import MongoClient
        from datetime import datetime, timedelta
        
        client = MongoClient('mongodb://localhost:27017')
        db = client['stock_tech_trends']
        collection = db[collection_name]
        
        # 최근 N일 데이터 조회
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = {
            'crawled_at': {'$gte': start_date.isoformat()}
        }
        
        data = list(collection.find(query))
        client.close()
        
        return pd.DataFrame(data)
    
    def _load_from_postgresql(self, table_name: str, days: int) -> pd.DataFrame:
        """PostgreSQL에서 데이터 로드"""
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect('postgresql://user:password@localhost:5432/stock_trends')
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = f"""
            SELECT * FROM {table_name}
            WHERE crawled_at >= NOW() - INTERVAL '{days} days'
        """
        
        cursor.execute(query)
        data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return pd.DataFrame(data)
    
    def analyze_keyword_trends(self, data: pd.DataFrame, keyword_field: str = 'tech_keywords') -> Dict:
        """키워드 트렌드 분석"""
        # 모든 키워드 수집
        all_keywords = []
        for keywords in data[keyword_field].dropna():
            if isinstance(keywords, list):
                all_keywords.extend(keywords)
            elif isinstance(keywords, str):
                all_keywords.extend(keywords.split(','))
        
        # 키워드 빈도 계산
        keyword_counts = Counter(all_keywords)
        
        # 상위 키워드 추출
        top_keywords = dict(keyword_counts.most_common(20))
        
        return {
            'total_keywords': len(all_keywords),
            'unique_keywords': len(keyword_counts),
            'top_keywords': top_keywords,
            'keyword_distribution': dict(keyword_counts)
        }
    
    def analyze_sentiment_trends(self, data: pd.DataFrame) -> Dict:
        """감성 분석 트렌드"""
        if 'sentiment_score' not in data.columns:
            return {'error': 'Sentiment data not available'}
        
        # 감성 점수 추출
        sentiments = []
        for score in data['sentiment_score'].dropna():
            if isinstance(score, dict):
                sentiments.append(score.get('overall_sentiment', 'neutral'))
            elif isinstance(score, str):
                sentiments.append(score)
        
        # 감성 분포 계산
        sentiment_counts = Counter(sentiments)
        
        # 시간별 감성 트렌드
        data['date'] = pd.to_datetime(data['crawled_at']).dt.date
        daily_sentiment = data.groupby('date')['sentiment_score'].apply(
            lambda x: self._calculate_daily_sentiment(x)
        ).reset_index()
        
        return {
            'overall_sentiment_distribution': dict(sentiment_counts),
            'daily_sentiment_trend': daily_sentiment.to_dict('records'),
            'positive_ratio': sentiment_counts.get('positive', 0) / len(sentiments) if sentiments else 0,
            'negative_ratio': sentiment_counts.get('negative', 0) / len(sentiments) if sentiments else 0
        }
    
    def _calculate_daily_sentiment(self, sentiment_scores):
        """일별 감성 점수 계산"""
        sentiments = []
        for score in sentiment_scores:
            if isinstance(score, dict):
                sentiments.append(score.get('overall_sentiment', 'neutral'))
            elif isinstance(score, str):
                sentiments.append(score)
        
        if not sentiments:
            return 'neutral'
        
        sentiment_counts = Counter(sentiments)
        return sentiment_counts.most_common(1)[0][0]
    
    def analyze_engagement_trends(self, data: pd.DataFrame) -> Dict:
        """참여도 트렌드 분석"""
        engagement_metrics = {}
        
        # 점수/댓글 수 분석
        if 'score' in data.columns:
            engagement_metrics['avg_score'] = data['score'].mean()
            engagement_metrics['max_score'] = data['score'].max()
            engagement_metrics['high_engagement_posts'] = len(data[data['score'] > data['score'].quantile(0.8)])
        
        if 'num_comments' in data.columns:
            engagement_metrics['avg_comments'] = data['num_comments'].mean()
            engagement_metrics['max_comments'] = data['num_comments'].max()
            engagement_metrics['high_comment_posts'] = len(data[data['num_comments'] > data['num_comments'].quantile(0.8)])
        
        # 시간별 참여도 트렌드
        if 'crawled_at' in data.columns:
            data['hour'] = pd.to_datetime(data['crawled_at']).dt.hour
            hourly_engagement = data.groupby('hour').agg({
                'score': 'mean',
                'num_comments': 'mean'
            }).reset_index()
            
            engagement_metrics['hourly_engagement'] = hourly_engagement.to_dict('records')
        
        return engagement_metrics
    
    def generate_trend_report(self, collection_name: str, days: int = 7) -> Dict:
        """종합 트렌드 리포트 생성"""
        print(f"📊 {collection_name} 트렌드 분석 시작...")
        
        # 데이터 로드
        data = self.load_data(collection_name, days)
        
        if data.empty:
            return {'error': f'No data found for {collection_name}'}
        
        print(f"✅ {len(data)}개 데이터 로드 완료")
        
        # 분석 실행
        report = {
            'collection': collection_name,
            'period_days': days,
            'total_records': len(data),
            'analysis_date': datetime.now().isoformat(),
            'keyword_trends': self.analyze_keyword_trends(data),
            'sentiment_trends': self.analyze_sentiment_trends(data),
            'engagement_trends': self.analyze_engagement_trends(data)
        }
        
        return report
    
    def create_visualizations(self, report: Dict, output_dir: str = 'visualizations'):
        """시각화 생성"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        collection_name = report['collection']
        
        # 1. 키워드 트렌드 차트
        if 'keyword_trends' in report and 'top_keywords' in report['keyword_trends']:
            self._create_keyword_chart(report['keyword_trends']['top_keywords'], 
                                     f"{output_dir}/{collection_name}_keywords.png")
        
        # 2. 감성 분석 차트
        if 'sentiment_trends' in report and 'overall_sentiment_distribution' in report['sentiment_trends']:
            self._create_sentiment_chart(report['sentiment_trends']['overall_sentiment_distribution'],
                                       f"{output_dir}/{collection_name}_sentiment.png")
        
        # 3. 참여도 트렌드 차트
        if 'engagement_trends' in report and 'hourly_engagement' in report['engagement_trends']:
            self._create_engagement_chart(report['engagement_trends']['hourly_engagement'],
                                        f"{output_dir}/{collection_name}_engagement.png")
    
    def _create_keyword_chart(self, keywords: Dict, output_path: str):
        """키워드 차트 생성"""
        plt.figure(figsize=(12, 8))
        
        words = list(keywords.keys())[:15]
        counts = list(keywords.values())[:15]
        
        plt.barh(words, counts)
        plt.xlabel('Frequency')
        plt.title('Top Technology Keywords')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_sentiment_chart(self, sentiments: Dict, output_path: str):
        """감성 분석 차트 생성"""
        plt.figure(figsize=(8, 6))
        
        labels = list(sentiments.keys())
        sizes = list(sentiments.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('Sentiment Distribution')
        plt.axis('equal')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_engagement_chart(self, engagement_data: List, output_path: str):
        """참여도 차트 생성"""
        if not engagement_data:
            return
        
        df = pd.DataFrame(engagement_data)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 점수 트렌드
        ax1.plot(df['hour'], df['score'], marker='o')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Average Score')
        ax1.set_title('Hourly Score Trend')
        ax1.grid(True)
        
        # 댓글 수 트렌드
        ax2.plot(df['hour'], df['num_comments'], marker='s', color='orange')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Average Comments')
        ax2.set_title('Hourly Comments Trend')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """메인 실행 함수"""
    analyzer = TrendAnalyzer()
    
    # 분석할 컬렉션 목록
    collections = ['reddit_posts', 'hackernews_items', 'github_repos']
    
    for collection in collections:
        try:
            print(f"\n🔍 {collection} 분석 중...")
            report = analyzer.generate_trend_report(collection, days=7)
            
            if 'error' not in report:
                # 리포트 저장
                with open(f'reports/{collection}_trend_report.json', 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                
                # 시각화 생성
                analyzer.create_visualizations(report)
                
                print(f"✅ {collection} 분석 완료")
            else:
                print(f"⚠️ {collection}: {report['error']}")
                
        except Exception as e:
            print(f"❌ {collection} 분석 실패: {e}")


if __name__ == '__main__':
    main()
