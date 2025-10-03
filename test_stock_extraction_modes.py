"""
주식 티커 추출 모드 비교 테스트

AGGRESSIVE vs STRICT 모드의 차이를 보여줍니다.
"""

import sys
import io

# Windows에서 UTF-8 출력 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.stock_ticker_extractor import extract_stock_tickers

# 테스트 케이스들
test_cases = [
    {
        "name": "케이스 1: 유명 주식 + 신규 스타트업",
        "text": "I'm buying $NVDA and this new AI startup $ABCD just IPOed today!",
    },
    {
        "name": "케이스 2: 달러 기호 없는 소형주",
        "text": "PLTR is great but check out XYZW, a new cybersecurity stock with huge potential.",
    },
    {
        "name": "케이스 3: 여러 신규 티커",
        "text": "Hot IPOs this week: $NEWCO, $STRT, and $TECH. Also looking at ABCD stock.",
    },
    {
        "name": "케이스 4: 알려진 주식만",
        "text": "Portfolio update: Added $AAPL, $MSFT, $GOOGL. Sold $TSLA for profit.",
    },
    {
        "name": "케이스 5: 주식 + 일반 약어 (false positive 테스트)",
        "text": "The CEO said AI and ML will boost $NVDA stock. Check USA market.",
    },
]

def main():
    print("="*80)
    print("🔬 주식 티커 추출 모드 비교 테스트")
    print("="*80)
    print("\n🔓 AGGRESSIVE 모드: 모든 티커 추출 (스타트업 포함)")
    print("🔒 STRICT 모드: 알려진 주요 주식만")
    print("="*80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n\n{'='*80}")
        print(f"📝 {case['name']}")
        print(f"{'='*80}")
        print(f"\n원문:")
        print(f"  \"{case['text']}\"")
        
        # AGGRESSIVE 모드로 추출
        tickers_aggressive = extract_stock_tickers(case['text'], mode='aggressive')
        
        # STRICT 모드로 추출
        tickers_strict = extract_stock_tickers(case['text'], mode='strict')
        
        # 결과 출력
        print(f"\n결과:")
        print(f"  🔓 AGGRESSIVE: {tickers_aggressive}")
        print(f"     → 추출된 티커 수: {len(tickers_aggressive)}개")
        
        print(f"  🔒 STRICT:     {tickers_strict}")
        print(f"     → 추출된 티커 수: {len(tickers_strict)}개")
        
        # 차이 분석
        only_aggressive = set(tickers_aggressive) - set(tickers_strict)
        if only_aggressive:
            print(f"\n  💡 AGGRESSIVE에서만 추출된 티커 (스타트업/신규 상장):")
            print(f"     {sorted(list(only_aggressive))}")
        else:
            print(f"\n  ✓ 두 모드 결과 동일 (알려진 주식만 있음)")
    
    # 요약
    print("\n\n" + "="*80)
    print("📊 결론")
    print("="*80)
    print("""
🔓 AGGRESSIVE 모드 사용 시기:
   ✓ 새로운 트렌드와 스타트업을 발굴하고 싶을 때
   ✓ IPO와 신규 상장 주식을 놓치고 싶지 않을 때
   ✓ Reddit의 "다음 큰 것"을 찾고 있을 때
   ✓ 포괄적인 분석이 필요할 때

🔒 STRICT 모드 사용 시기:
   ✓ 검증된 주요 기업만 분석하고 싶을 때
   ✓ False positive를 최소화하고 싶을 때
   ✓ 안정적이고 예측 가능한 결과가 필요할 때
   ✓ 보고서나 리서치에 사용할 때

💡 권장: 기본적으로 AGGRESSIVE 모드를 사용하되, 
         필요에 따라 STRICT 모드로 검증하는 것이 좋습니다.
""")
    print("="*80)

if __name__ == '__main__':
    main()

