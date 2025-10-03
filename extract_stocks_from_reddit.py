"""
Reddit 데이터에서 주식 티커 추출 전용 스크립트

기존 reddit_data.json 파일을 읽어서 주식 티커를 추출하고 분석합니다.
"""

import json
import sys
from collections import Counter
from utils.stock_ticker_extractor import StockTickerExtractor

def main(mode='aggressive'):
    print("="*70)
    print("💰 Reddit 주식 티커 추출 및 분석")
    print("="*70)
    
    if mode == 'aggressive':
        print("\n🔓 AGGRESSIVE 모드: 모든 주식 티커 추출 (알려지지 않은 스타트업 포함)")
        print("   - 주식 관련 문맥에 나타나는 모든 대문자 티커 추출")
        print("   - 스타트업, IPO, 소형주도 감지")
    else:
        print("\n🔒 STRICT 모드: 알려진 주요 주식만 추출")
        print("   - 150개 이상의 주요 기술 기업만 추출")
    
    # 데이터 로드
    json_file = 'data/reddit_data.json'
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"\n✅ {len(data)}개의 Reddit 포스트 로드 완료")
    except FileNotFoundError:
        print(f"\n❌ 파일을 찾을 수 없습니다: {json_file}")
        print("먼저 Reddit 크롤링을 실행해주세요: python run_crawler.py")
        return
    except Exception as e:
        print(f"\n❌ 파일 로드 실패: {e}")
        return
    
    # 티커 추출기 초기화
    extractor = StockTickerExtractor(mode=mode)
    
    # 티커 추출
    all_tickers = []
    ticker_contexts = {}  # 티커별 멘션 정보
    
    print("\n🔍 주식 티커 추출 중...")
    for idx, post in enumerate(data):
        text = post.get('title', '') + ' ' + post.get('content', '')
        tickers = extractor.extract_tickers(text)
        
        for ticker in tickers:
            all_tickers.append(ticker)
            
            if ticker not in ticker_contexts:
                ticker_contexts[ticker] = {
                    'posts': [],
                    'subreddits': set(),
                    'total_score': 0,
                    'total_comments': 0
                }
            
            ticker_contexts[ticker]['posts'].append({
                'title': post.get('title', ''),
                'score': post.get('score', 0),
                'num_comments': post.get('num_comments', 0),
                'subreddit': post.get('subreddit', ''),
                'permalink': post.get('permalink', '')
            })
            ticker_contexts[ticker]['subreddits'].add(post.get('subreddit', ''))
            ticker_contexts[ticker]['total_score'] += post.get('score', 0)
            ticker_contexts[ticker]['total_comments'] += post.get('num_comments', 0)
        
        # 진행 상황 표시
        if (idx + 1) % 100 == 0:
            print(f"  처리 중... {idx + 1}/{len(data)} 포스트")
    
    if not all_tickers:
        print("\n⚠️  주식 티커가 발견되지 않았습니다.")
        return
    
    # 통계 출력
    ticker_counts = Counter(all_tickers)
    print(f"\n📊 분석 결과:")
    print(f"  총 티커 멘션 수: {len(all_tickers):,}")
    print(f"  고유 티커 수: {len(ticker_counts)}")
    
    # 상위 30개 티커
    print("\n🏆 가장 많이 언급된 주식 TOP 30:")
    print("="*70)
    
    for rank, (ticker, count) in enumerate(ticker_counts.most_common(30), 1):
        context = ticker_contexts[ticker]
        avg_score = context['total_score'] / len(context['posts'])
        avg_comments = context['total_comments'] / len(context['posts'])
        category = extractor.get_ticker_category(ticker)
        
        print(f"\n{rank:2d}. ${ticker} ({category})")
        print(f"    📈 멘션 횟수: {count}회")
        print(f"    ⭐ 평균 점수: {avg_score:.1f}")
        print(f"    💬 평균 댓글: {avg_comments:.1f}")
        print(f"    📍 서브레딧: {', '.join(list(context['subreddits'])[:5])}")
        
        # 대표 포스트 1개 표시
        top_post = max(context['posts'], key=lambda x: x['score'])
        print(f"    🔥 인기 포스트: {top_post['title'][:60]}...")
        print(f"       ↪ {top_post['permalink']}")
    
    # 카테고리별 분석
    print("\n\n📊 카테고리별 언급 현황:")
    print("="*70)
    
    category_stats = {}
    for ticker, count in ticker_counts.items():
        category = extractor.get_ticker_category(ticker)
        if category not in category_stats:
            category_stats[category] = {
                'count': 0,
                'tickers': []
            }
        category_stats[category]['count'] += count
        category_stats[category]['tickers'].append((ticker, count))
    
    for category in sorted(category_stats.keys(), 
                          key=lambda x: category_stats[x]['count'], 
                          reverse=True):
        stats = category_stats[category]
        print(f"\n{category}:")
        print(f"  총 멘션: {stats['count']}회")
        print(f"  티커 종류: {len(stats['tickers'])}개")
        
        # 해당 카테고리 상위 5개 티커
        top_in_category = sorted(stats['tickers'], key=lambda x: x[1], reverse=True)[:5]
        print(f"  Top 5: {', '.join([f'${t[0]}({t[1]})' for t in top_in_category])}")
    
    # 결과를 JSON 파일로 저장
    output = {
        'total_mentions': len(all_tickers),
        'unique_tickers': len(ticker_counts),
        'top_tickers': [
            {
                'ticker': ticker,
                'count': count,
                'category': extractor.get_ticker_category(ticker),
                'avg_score': ticker_contexts[ticker]['total_score'] / len(ticker_contexts[ticker]['posts']),
                'avg_comments': ticker_contexts[ticker]['total_comments'] / len(ticker_contexts[ticker]['posts']),
                'subreddits': list(ticker_contexts[ticker]['subreddits'])
            }
            for ticker, count in ticker_counts.most_common(50)
        ],
        'category_breakdown': {
            category: {
                'count': stats['count'],
                'tickers': [t[0] for t in sorted(stats['tickers'], key=lambda x: x[1], reverse=True)]
            }
            for category, stats in category_stats.items()
        }
    }
    
    import os
    os.makedirs('reports', exist_ok=True)
    
    with open('reports/stock_tickers_report.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n\n✅ 분석 완료!")
    print("="*70)
    print("📄 상세 리포트: reports/stock_tickers_report.json")
    print("💡 전체 트렌드 분석을 보려면: python analyze_reddit_data.py")
    print("\n💡 TIP: 모드 변경")
    print("   - 모든 티커 (기본): python extract_stocks_from_reddit.py")
    print("   - 주요 주식만: python extract_stocks_from_reddit.py --strict")
    print()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Reddit에서 주식 티커 추출')
    parser.add_argument('--strict', action='store_true', 
                       help='알려진 주요 주식만 추출 (기본값: 모든 티커 추출)')
    args = parser.parse_args()
    
    mode = 'strict' if args.strict else 'aggressive'
    main(mode=mode)

