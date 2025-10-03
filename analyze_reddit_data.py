"""
Reddit 데이터 분석 스크립트
"""

import json
import pandas as pd
from collections import Counter
from datetime import datetime
from utils.stock_ticker_extractor import StockTickerExtractor

def load_reddit_data(json_file):
    """JSON 파일에서 Reddit 데이터 로드"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def analyze_keywords(df):
    """키워드 트렌드 분석"""
    print("\n" + "="*60)
    print("📊 키워드 트렌드 분석")
    print("="*60)
    
    all_keywords = []
    for keywords in df['tech_keywords'].dropna():
        if isinstance(keywords, list):
            all_keywords.extend(keywords)
    
    keyword_counts = Counter(all_keywords)
    top_keywords = keyword_counts.most_common(20)
    
    print(f"\n총 키워드 수: {len(all_keywords)}")
    print(f"고유 키워드 수: {len(keyword_counts)}")
    print("\n상위 20개 키워드:")
    for i, (keyword, count) in enumerate(top_keywords, 1):
        print(f"  {i:2d}. {keyword:30s} : {count:4d}회")
    
    return dict(top_keywords)

def analyze_sentiment(df):
    """감성 분석"""
    print("\n" + "="*60)
    print("😊 감성 분석")
    print("="*60)
    
    sentiments = []
    for score in df['sentiment_score'].dropna():
        if isinstance(score, dict):
            sentiments.append(score.get('overall_sentiment', 'neutral'))
    
    sentiment_counts = Counter(sentiments)
    
    print(f"\n총 분석된 포스트: {len(sentiments)}")
    for sentiment, count in sentiment_counts.most_common():
        percentage = (count / len(sentiments)) * 100
        print(f"  {sentiment:10s}: {count:4d}개 ({percentage:5.1f}%)")
    
    return dict(sentiment_counts)

def analyze_subreddits(df):
    """서브레딧별 통계"""
    print("\n" + "="*60)
    print("📱 서브레딧별 통계")
    print("="*60)
    
    subreddit_counts = df['subreddit'].value_counts()
    
    print(f"\n총 서브레딧 수: {len(subreddit_counts)}")
    print("\n상위 15개 서브레딧:")
    for i, (subreddit, count) in enumerate(subreddit_counts.head(15).items(), 1):
        print(f"  {i:2d}. r/{subreddit:30s} : {count:4d}개")
    
    return dict(subreddit_counts.head(15))

def analyze_engagement(df):
    """참여도 분석"""
    print("\n" + "="*60)
    print("🔥 참여도 분석")
    print("="*60)
    
    avg_score = df['score'].mean()
    avg_comments = df['num_comments'].mean()
    avg_upvote_ratio = df['upvote_ratio'].mean()
    
    print(f"\n평균 점수 (Score): {avg_score:.1f}")
    print(f"평균 댓글 수: {avg_comments:.1f}")
    print(f"평균 추천 비율: {avg_upvote_ratio:.2%}")
    
    # 인기 포스트 Top 10
    print("\n🌟 인기 포스트 Top 10 (점수 기준):")
    top_posts = df.nlargest(10, 'score')[['title', 'score', 'num_comments', 'subreddit']]
    for i, row in enumerate(top_posts.itertuples(), 1):
        print(f"\n  {i}. [{row.subreddit}] {row.title[:70]}...")
        print(f"     ⬆️  Score: {row.score} | 💬 Comments: {row.num_comments}")
    
    return {
        'avg_score': float(avg_score),
        'avg_comments': float(avg_comments),
        'avg_upvote_ratio': float(avg_upvote_ratio)
    }

def analyze_stock_tickers(df, mode='aggressive'):
    """
    주식 티커 분석
    
    Args:
        df: Reddit 데이터 DataFrame
        mode: 'aggressive' (모든 티커 추출) 또는 'strict' (알려진 티커만)
    """
    print("\n" + "="*60)
    print("📈 주식 티커 분석")
    print("="*60)
    
    if mode == 'aggressive':
        print("🔓 AGGRESSIVE 모드: 모든 주식 티커 추출 (스타트업 포함)")
    else:
        print("🔒 STRICT 모드: 알려진 주요 주식만 추출")
    
    # 티커 추출기 초기화
    extractor = StockTickerExtractor(mode=mode)
    
    # 모든 티커 수집
    all_tickers = []
    ticker_posts = []  # 티커별 포스트 정보
    
    for idx, row in df.iterrows():
        # stock_tickers 컬럼이 있으면 사용, 없으면 추출
        if 'stock_tickers' in row and row['stock_tickers']:
            if isinstance(row['stock_tickers'], list):
                tickers = row['stock_tickers']
            else:
                tickers = []
        else:
            # 텍스트에서 티커 추출
            text = str(row.get('title', '')) + ' ' + str(row.get('content', ''))
            tickers = extractor.extract_tickers(text)
        
        all_tickers.extend(tickers)
        
        # 각 티커에 대한 포스트 정보 저장
        for ticker in tickers:
            ticker_posts.append({
                'ticker': ticker,
                'score': row.get('score', 0),
                'num_comments': row.get('num_comments', 0),
                'subreddit': row.get('subreddit', ''),
                'title': row.get('title', ''),
                'sentiment': row.get('sentiment_score', {}).get('overall_sentiment', 'neutral') if isinstance(row.get('sentiment_score'), dict) else 'neutral'
            })
    
    if not all_tickers:
        print("\n⚠️  추출된 주식 티커가 없습니다.")
        return {}
    
    # 티커별 카운트
    ticker_counts = Counter(all_tickers)
    top_tickers = ticker_counts.most_common(30)
    
    print(f"\n총 티커 멘션 수: {len(all_tickers)}")
    print(f"고유 티커 수: {len(ticker_counts)}")
    print("\n🔝 상위 30개 언급된 주식:")
    
    # 티커별 상세 정보 계산
    ticker_details = {}
    for ticker, count in top_tickers:
        ticker_data = [p for p in ticker_posts if p['ticker'] == ticker]
        
        avg_score = sum(p['score'] for p in ticker_data) / len(ticker_data)
        avg_comments = sum(p['num_comments'] for p in ticker_data) / len(ticker_data)
        
        # 감성 분석
        sentiments = [p['sentiment'] for p in ticker_data]
        sentiment_counts = Counter(sentiments)
        dominant_sentiment = sentiment_counts.most_common(1)[0][0]
        
        # 카테고리
        category = extractor.get_ticker_category(ticker)
        
        ticker_details[ticker] = {
            'count': count,
            'avg_score': avg_score,
            'avg_comments': avg_comments,
            'sentiment': dominant_sentiment,
            'category': category,
            'subreddits': list(set(p['subreddit'] for p in ticker_data))
        }
    
    # 출력
    for i, (ticker, count) in enumerate(top_tickers, 1):
        details = ticker_details[ticker]
        sentiment_emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😢'}.get(details['sentiment'], '😐')
        
        print(f"  {i:2d}. ${ticker:6s} : {count:4d}회 | "
              f"평균 점수: {details['avg_score']:6.1f} | "
              f"평균 댓글: {details['avg_comments']:5.1f} | "
              f"{sentiment_emoji} {details['sentiment']:8s} | "
              f"{details['category']}")
    
    # 카테고리별 분석
    print("\n📊 카테고리별 언급 빈도:")
    category_counts = Counter()
    for ticker, details in ticker_details.items():
        category_counts[details['category']] += details['count']
    
    for category, count in category_counts.most_common():
        print(f"  {category:20s}: {count:4d}회")
    
    return dict(ticker_details)

def create_visualizations(keyword_data, sentiment_data, subreddit_data, stock_ticker_data, output_dir='visualizations'):
    """시각화 생성 (matplotlib 필요)"""
    try:
        import matplotlib.pyplot as plt
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. 키워드 차트
        plt.figure(figsize=(14, 8))
        keywords = list(keyword_data.keys())[:15]
        counts = list(keyword_data.values())[:15]
        
        plt.barh(range(len(keywords)), counts, color='skyblue')
        plt.yticks(range(len(keywords)), keywords)
        plt.xlabel('Frequency', fontsize=12)
        plt.title('Top Technology Keywords (Top 15)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/keywords.png', dpi=300, bbox_inches='tight')
        print(f"\n✅ 키워드 차트 저장: {output_dir}/keywords.png")
        plt.close()
        
        # 2. 감성 분석 차트
        plt.figure(figsize=(10, 8))
        labels = list(sentiment_data.keys())
        sizes = list(sentiment_data.values())
        colors = {'positive': '#66ff99', 'neutral': '#99ccff', 'negative': '#ff9999'}
        chart_colors = [colors.get(label, '#cccccc') for label in labels]
        
        plt.pie(sizes, labels=labels, colors=chart_colors, autopct='%1.1f%%', 
                startangle=90, textprops={'fontsize': 12})
        plt.title('Sentiment Distribution', fontsize=14, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/sentiment.png', dpi=300, bbox_inches='tight')
        print(f"✅ 감성 분석 차트 저장: {output_dir}/sentiment.png")
        plt.close()
        
        # 3. 서브레딧 차트
        plt.figure(figsize=(14, 8))
        subreddits = list(subreddit_data.keys())
        counts = list(subreddit_data.values())
        
        plt.barh(range(len(subreddits)), counts, color='coral')
        plt.yticks(range(len(subreddits)), [f'r/{s}' for s in subreddits])
        plt.xlabel('Number of Posts', fontsize=12)
        plt.title('Posts by Subreddit (Top 15)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/subreddits.png', dpi=300, bbox_inches='tight')
        print(f"✅ 서브레딧 차트 저장: {output_dir}/subreddits.png")
        plt.close()
        
        # 4. 주식 티커 차트
        if stock_ticker_data:
            plt.figure(figsize=(16, 10))
            # 상위 20개만 표시
            sorted_tickers = sorted(stock_ticker_data.items(), 
                                   key=lambda x: x[1]['count'], 
                                   reverse=True)[:20]
            
            tickers = [f"${t[0]}" for t in sorted_tickers]
            counts = [t[1]['count'] for t in sorted_tickers]
            
            # 감성에 따른 색상
            colors_list = []
            for ticker, data in sorted_tickers:
                sentiment = data.get('sentiment', 'neutral')
                if sentiment == 'positive':
                    colors_list.append('#66ff99')
                elif sentiment == 'negative':
                    colors_list.append('#ff9999')
                else:
                    colors_list.append('#99ccff')
            
            bars = plt.barh(range(len(tickers)), counts, color=colors_list)
            plt.yticks(range(len(tickers)), tickers)
            plt.xlabel('Mention Count', fontsize=12)
            plt.title('Top 20 Most Mentioned Stock Tickers', fontsize=14, fontweight='bold')
            
            # 범례 추가
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#66ff99', label='Positive'),
                Patch(facecolor='#99ccff', label='Neutral'),
                Patch(facecolor='#ff9999', label='Negative')
            ]
            plt.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout()
            plt.savefig(f'{output_dir}/stock_tickers.png', dpi=300, bbox_inches='tight')
            print(f"✅ 주식 티커 차트 저장: {output_dir}/stock_tickers.png")
            plt.close()
            
            # 5. 카테고리별 차트
            category_counts = {}
            for ticker, data in stock_ticker_data.items():
                category = data.get('category', 'Other')
                category_counts[category] = category_counts.get(category, 0) + data['count']
            
            if category_counts:
                plt.figure(figsize=(12, 8))
                categories = list(category_counts.keys())
                counts = list(category_counts.values())
                
                colors_cat = plt.cm.Set3(range(len(categories)))
                plt.pie(counts, labels=categories, colors=colors_cat, autopct='%1.1f%%',
                       startangle=90, textprops={'fontsize': 11})
                plt.title('Stock Mentions by Category', fontsize=14, fontweight='bold')
                plt.axis('equal')
                plt.tight_layout()
                plt.savefig(f'{output_dir}/stock_categories.png', dpi=300, bbox_inches='tight')
                print(f"✅ 주식 카테고리 차트 저장: {output_dir}/stock_categories.png")
                plt.close()
                
    except ImportError:
        print("\n⚠️  matplotlib가 설치되지 않아 시각화를 건너뜁니다.")
        print("   시각화를 원하시면: pip install matplotlib")

def main():
    """메인 실행"""
    print("\n" + "="*60)
    print("🚀 Reddit 데이터 트렌드 분석 시작")
    print("="*60)
    
    # 데이터 로드
    json_file = 'data/reddit_data.json'
    df = load_reddit_data(json_file)
    
    print(f"\n✅ 총 {len(df)}개의 Reddit 포스트 로드 완료")
    print(f"📅 수집 시간: {df['crawled_at'].min()} ~ {df['crawled_at'].max()}")
    
    # 분석 수행
    keyword_data = analyze_keywords(df)
    sentiment_data = analyze_sentiment(df)
    subreddit_data = analyze_subreddits(df)
    engagement_data = analyze_engagement(df)
    stock_ticker_data = analyze_stock_tickers(df)
    
    # 시각화 생성 (선택사항)
    print("\n" + "="*60)
    print("📊 시각화 생성 시도 중...")
    print("="*60)
    try:
        create_visualizations(keyword_data, sentiment_data, subreddit_data, stock_ticker_data)
    except Exception as e:
        print(f"⚠️  시각화 생성 실패: {e}")
    
    # 리포트 저장 (numpy 타입을 Python 타입으로 변환)
    def convert_to_native(obj):
        """numpy/pandas 타입을 Python native 타입으로 변환"""
        import numpy as np
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(item) for item in obj]
        return obj
    
    report = {
        'analysis_date': datetime.now().isoformat(),
        'total_posts': int(len(df)),
        'keyword_trends': convert_to_native(keyword_data),
        'sentiment_distribution': convert_to_native(sentiment_data),
        'top_subreddits': convert_to_native(subreddit_data),
        'engagement_metrics': convert_to_native(engagement_data),
        'stock_tickers': convert_to_native(stock_ticker_data)
    }
    
    import os
    os.makedirs('reports', exist_ok=True)
    with open('reports/reddit_trend_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("✅ 분석 완료!")
    print("="*60)
    print(f"📄 리포트 저장: reports/reddit_trend_report.json")
    print(f"📊 시각화 저장: visualizations/ 디렉토리")

if __name__ == '__main__':
    main()

