# 📈 Reddit 주식 티커 추출 기능

Reddit에서 자주 언급되는 주식 티커 심볼(예: AAPL, TSLA, NVDA 등)을 자동으로 추출하고 분석하는 기능입니다.

## 🎯 주요 기능

### 1. 주식 티커 자동 추출 (2가지 모드)

#### 🔓 AGGRESSIVE 모드 (기본값) - **스타트업 포함!**
- **모든 주식 티커 추출** - 알려지지 않은 스타트업도 감지
- `$AAPL`, `$TSLA` 등 달러 기호가 붙은 티커 자동 감지
- 주식 관련 문맥에 나타나는 **모든** 대문자 티커 추출
- IPO, 소형주, 새로운 스타트업도 포함

**예시:**
```
"Check out $RBLX and this new startup $ABCD for AI gaming!"
→ ['ABCD', 'RBLX'] 추출 (ABCD는 알려지지 않았지만 추출됨)
```

#### 🔒 STRICT 모드 - 주요 주식만
- 150개 이상의 **알려진 주요 기술 기업**만 추출
- false positive 최소화
- 안정적인 결과

**예시:**
```
"Check out $RBLX and this new startup $ABCD for AI gaming!"
→ ['RBLX'] 추출 (ABCD는 알려지지 않아서 제외됨)
```

### 2. 카테고리별 분류
추출된 주식을 다음 카테고리로 자동 분류:
- **Big Tech**: AAPL, MSFT, GOOGL, AMZN, META
- **Semiconductors**: NVDA, AMD, INTC, TSM, QCOM
- **AI/Data**: PLTR, AI, BBAI
- **Electric Vehicles**: TSLA, RIVN, LCID, NIO
- **Cloud/Software**: CRM, ORCL, NOW, SNOW
- **Fintech**: SQ, PYPL, COIN, HOOD
- **Cybersecurity**: CRWD, ZS, PANW
- **ETF**: QQQ, SPY, ARKK

### 3. 상세 분석
각 티커별로 다음 정보 제공:
- 멘션 횟수
- 평균 포스트 점수
- 평균 댓글 수
- 감성 분석 (긍정/중립/부정)
- 언급된 서브레딧 목록

### 4. 시각화
- 상위 20개 티커 차트 (감성별 색상 구분)
- 카테고리별 멘션 분포 파이 차트

## 🚀 사용 방법

### 방법 1: 주식 티커만 추출하기

```bash
# 🔓 모든 티커 추출 (스타트업 포함) - 기본값
python extract_stocks_from_reddit.py

# 🔒 주요 주식만 추출
python extract_stocks_from_reddit.py --strict
```

출력 예시:
```
💰 Reddit 주식 티커 추출 및 분석
======================================================================

🔓 AGGRESSIVE 모드: 모든 주식 티커 추출 (알려지지 않은 스타트업 포함)
   - 주식 관련 문맥에 나타나는 모든 대문자 티커 추출
   - 스타트업, IPO, 소형주도 감지

✅ 1,234개의 Reddit 포스트 로드 완료

📊 분석 결과:
  총 티커 멘션 수: 3,456
  고유 티커 수: 189  ← 스타트업 포함으로 훨씬 많음!

🏆 가장 많이 언급된 주식 TOP 30:
======================================================================

 1. $NVDA (Semiconductors)
    📈 멘션 횟수: 342회
    ⭐ 평균 점수: 156.3
    💬 평균 댓글: 45.2
    📍 서브레딧: stocks, investing, wallstreetbets
    🔥 인기 포스트: NVIDIA hits new all-time high on AI chip demand...
```

### 방법 2: 전체 분석에 포함

```bash
# Reddit 데이터 전체 분석 (키워드, 감성, 주식 티커 포함)
python analyze_reddit_data.py
```

이 명령을 실행하면:
1. 키워드 트렌드 분석
2. 감성 분석
3. 서브레딧별 통계
4. 참여도 분석
5. **주식 티커 분석** ← 새로 추가됨!
6. 시각화 생성

### 방법 3: 새로운 데이터 수집부터

```bash
# 1. Reddit 데이터 크롤링 (주식 티커 자동 추출됨)
python run_crawler.py

# 2. 분석 실행
python analyze_reddit_data.py
```

## 📊 출력 파일

### 1. `reports/stock_tickers_report.json`
주식 티커 상세 분석 결과:
```json
{
  "total_mentions": 3456,
  "unique_tickers": 89,
  "top_tickers": [
    {
      "ticker": "NVDA",
      "count": 342,
      "category": "Semiconductors",
      "avg_score": 156.3,
      "avg_comments": 45.2,
      "subreddits": ["stocks", "investing", "wallstreetbets"]
    }
  ],
  "category_breakdown": {
    "Semiconductors": {
      "count": 567,
      "tickers": ["NVDA", "AMD", "INTC", "TSM"]
    }
  }
}
```

### 2. `reports/reddit_trend_report.json`
전체 트렌드 리포트 (주식 티커 섹션 포함)

### 3. 시각화 이미지
- `visualizations/stock_tickers.png` - 상위 20개 티커 차트
- `visualizations/stock_categories.png` - 카테고리별 분포 차트

## 🔧 지원되는 주식 티커

현재 **150개 이상**의 주요 기술/트렌드 관련 주식 티커를 지원합니다:

### 빅테크
AAPL, MSFT, GOOGL, GOOG, AMZN, META, NVDA, TSLA

### 반도체
AMD, INTC, TSM, QCOM, MU, AVGO, ASML, ARM, AMAT, LRCX, KLAC

### AI/데이터
PLTR, AI, BBAI, SOUN, PATH

### 전기차
RIVN, LCID, NIO, XPEV, LI

### 클라우드/소프트웨어
CRM, ORCL, IBM, SAP, ADBE, NOW, SNOW, NET, DDOG, MDB

### 핀테크
SQ, PYPL, COIN, HOOD, SOFI

### 사이버보안
CRWD, ZS, PANW, FTNT, S

### ETF
QQQ, SPY, VOO, VTI, ARKK, ARKQ, ARKW, ARKG

*전체 목록은 `utils/stock_ticker_extractor.py`에서 확인 가능*

## 🎨 커스터마이징

### 티커 목록 추가/수정

`utils/stock_ticker_extractor.py` 파일에서 `KNOWN_TICKERS` 세트를 수정:

```python
class StockTickerExtractor:
    KNOWN_TICKERS = {
        # 여기에 새로운 티커 추가
        'YOUR_TICKER_HERE',
        # ...
    }
```

### 카테고리 추가

`get_ticker_category()` 메서드에서 카테고리 정의 수정:

```python
def get_ticker_category(self, ticker: str) -> str:
    categories = {
        'Your Category': ['TICKER1', 'TICKER2'],
        # ...
    }
```

## 📈 실전 활용 예시

### 1. 기본 사용 - 모든 티커 추출 (스타트업 포함)
```python
from utils.stock_ticker_extractor import extract_stock_tickers

text = "I'm bullish on $NVDA and this new startup $ABCD for AI. $TSLA to the moon! 🚀"

# AGGRESSIVE 모드 (기본값) - 모든 티커
tickers = extract_stock_tickers(text)
print(tickers)  # ['ABCD', 'AMD', 'NVDA', 'TSLA'] - 스타트업 ABCD 포함!

# STRICT 모드 - 알려진 주식만
tickers_strict = extract_stock_tickers(text, mode='strict')
print(tickers_strict)  # ['AMD', 'NVDA', 'TSLA'] - ABCD 제외됨
```

### 2. 문맥과 함께 추출
```python
from utils.stock_ticker_extractor import extract_tickers_with_context

# 모든 티커 추출 (기본값)
results = extract_tickers_with_context(text)
for result in results:
    print(f"{result['ticker']}: {result['mention_count']}회 언급")
    print(f"문맥: {result['contexts']}")

# 주요 주식만 추출
results_strict = extract_tickers_with_context(text, mode='strict')
```

### 3. 클래스 직접 사용
```python
from utils.stock_ticker_extractor import StockTickerExtractor

# AGGRESSIVE 모드로 초기화
extractor = StockTickerExtractor(mode='aggressive')
tickers = extractor.extract_tickers(text)

# STRICT 모드로 초기화
extractor_strict = StockTickerExtractor(mode='strict')
tickers_strict = extractor_strict.extract_tickers(text)
```

## ⚙️ 알고리즘 설명

### 2가지 추출 모드

#### 🔓 AGGRESSIVE 모드 (기본값)
**"스타트업과 새로운 IPO를 놓치지 않는다!"**

1. **달러 기호 패턴** (`$AAPL`) - **무조건 추출**
   - 정규식: `\$([A-Z]{1,5})\b`
   - 가장 확실한 주식 티커 표시
   - 알려지지 않아도 추출!

2. **대문자 단어 패턴** (`AAPL`) - **문맥만 확인**
   - 정규식: `\b([A-Z]{2,5})\b`
   - 주식 관련 문맥에 있으면 추출
   - 알려지지 않아도 OK

3. **문맥 분석**
   - 티커 주변 100자 분석
   - 주식 관련 키워드 확인:
     - stock, share, buy, sell, price, trade, invest
     - bull, bear, call, put, option, equity, market
     - portfolio, long, short, gain, loss, earnings, IPO, ticker

4. **False Positive 방지**
   - 일반 단어 제외 (THE, AND, FOR, ARE 등)
   - 약어 제외 (AI, VR, AR, CEO 등)

#### 🔒 STRICT 모드
**"검증된 주요 주식만 가져온다"**

1. **달러 기호 패턴** (`$AAPL`)
   - 알려진 티커 목록과 대조
   - 목록에 없으면 제외

2. **대문자 단어 패턴** (`AAPL`)
   - 알려진 티커 목록과 대조
   - 문맥 + 목록 둘 다 확인

### 장단점 비교

| 특징 | AGGRESSIVE 🔓 | STRICT 🔒 |
|------|--------------|-----------|
| 스타트업 감지 | ✅ 가능 | ❌ 불가능 |
| IPO/신규 상장 | ✅ 감지 | ❌ 사전 등록 필요 |
| False Positive | ⚠️ 약간 있음 | ✅ 최소화 |
| 추출 수량 | 📈 많음 | 📉 적음 |
| 권장 용도 | 트렌드 발굴 | 안정적 분석 |

## 🤝 기여하기

새로운 티커 추가나 알고리즘 개선 제안은 언제든 환영합니다!

## 📝 라이센스

이 프로젝트의 일부입니다. 자유롭게 사용하세요!

---

**문제가 있나요?** Issue를 남겨주세요!
**더 많은 기능이 필요한가요?** PR을 보내주세요!

