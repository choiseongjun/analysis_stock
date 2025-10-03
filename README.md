# 주식 기술 트렌드 분석 크롤링 프로젝트

## 프로젝트 개요
주식 시장에서 기술(Tech) 트렌드를 기반으로 투자 인사이트를 제공하는 데이터 수집 및 분석 시스템

## 주요 기능
- **실시간 기술 트렌드 모니터링**: Reddit, Hacker News 등 커뮤니티 데이터 수집
- **기업 채용 트렌드 분석**: 채용 공고 사이트 크롤링을 통한 기술 투자 예측
- **기업 IR/PR 모니터링**: 신규 제품 출시, 파트너십 등 중요 발표 추적
- **개발자 커뮤니티 분석**: GitHub, Stack Overflow 데이터를 통한 기술 스택 트렌드 분석
- **감성 분석**: 수집된 데이터의 긍정/부정 감성 분석
- **시각화 대시보드**: 실시간 트렌드 시각화

## 데이터 소스
1. **Reddit API** - 기술 관련 서브레딧 (r/MachineLearning, r/investing 등)
2. **Hacker News API** - 기술 뉴스 및 토론
3. **Indeed/LinkedIn** - 채용 공고 데이터
4. **GitHub API** - 오픈소스 기여도 및 기술 스택
5. **Stack Overflow API** - 기술 질문/답변 트렌드
6. **기업 IR 페이지** - 공식 발표 및 뉴스

## 기술 스택
- **크롤링**: Scrapy, Selenium, BeautifulSoup
- **데이터 처리**: Pandas, NumPy
- **데이터베이스**: MongoDB, PostgreSQL
- **감성 분석**: TextBlob, VADER
- **시각화**: Plotly, Dash, Streamlit
- **스케줄링**: Celery, Schedule

## 설치 및 실행

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 API 키 및 데이터베이스 설정

# Scrapy 프로젝트 초기화
scrapy startproject stock_tech_trends

# 크롤링 실행
cd stock_tech_trends
scrapy crawl reddit_spider
scrapy crawl hackernews_spider
```

## 프로젝트 구조
```
trends_pj/
├── stock_tech_trends/          # Scrapy 프로젝트
│   ├── spiders/                # 크롤링 스파이더
│   ├── items.py               # 데이터 모델
│   ├── pipelines.py           # 데이터 처리 파이프라인
│   └── settings.py            # 설정
├── data_analysis/             # 데이터 분석 모듈
├── visualization/             # 시각화 대시보드
├── sentiment_analysis/        # 감성 분석 모듈
└── utils/                     # 유틸리티 함수
```

## 라이선스
MIT License
