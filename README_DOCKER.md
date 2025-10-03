# Docker Compose 사용 가이드

## 개요
Docker Compose를 사용하여 주식 기술 트렌드 크롤링 시스템의 모든 인프라를 자동으로 구성하고 실행합니다.

## 포함된 서비스

### 데이터베이스
- **MongoDB** (포트 27017): 비정형 데이터 저장
- **PostgreSQL** (포트 5432): 정형 데이터 저장
- **Redis** (포트 6379): 캐싱 및 메시지 큐

### 관리 UI
- **Mongo Express** (포트 8081): MongoDB 관리 UI
  - URL: http://localhost:8081
  - 계정: admin / admin

- **pgAdmin** (포트 5050): PostgreSQL 관리 UI
  - URL: http://localhost:5050
  - 계정: admin@stock-trends.com / admin123

- **Redis Commander** (포트 8082): Redis 관리 UI
  - URL: http://localhost:8082

- **Flower** (포트 5555): Celery 작업 모니터링
  - URL: http://localhost:5555

- **Grafana** (포트 3000): 모니터링 대시보드
  - URL: http://localhost:3000
  - 계정: admin / admin123

### 백그라운드 작업
- **Celery Worker**: 크롤링 및 데이터 처리
- **Celery Beat**: 스케줄 관리
- **Flower**: Celery 모니터링

## 시작하기

### 1. 필수 요구사항
```bash
# Docker Desktop 설치 (Windows/Mac)
# https://www.docker.com/products/docker-desktop

# 또는 Docker Engine + Docker Compose 설치 (Linux)
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 2. 환경 설정
```bash
# .env 파일 생성 (config.env를 복사)
copy config.env .env

# 필요한 디렉토리 생성
mkdir data reports logs visualizations
```

### 3. Docker Compose 실행
```bash
# 모든 서비스 시작 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그 확인
docker-compose logs -f mongodb
docker-compose logs -f celery-worker

# 서비스 상태 확인
docker-compose ps
```

### 4. 서비스 중지 및 제거
```bash
# 모든 서비스 중지
docker-compose stop

# 모든 서비스 중지 및 컨테이너 제거
docker-compose down

# 볼륨까지 모두 제거 (데이터 삭제 주의!)
docker-compose down -v
```

## 데이터베이스 연결 정보

### MongoDB
```
URI: mongodb://admin:admin123@localhost:27017
데이터베이스: stock_tech_trends
관리 UI: http://localhost:8081
```

### PostgreSQL
```
호스트: localhost
포트: 5432
사용자: stock_user
비밀번호: stock_pass123
데이터베이스: stock_trends
관리 UI: http://localhost:5050
```

### Redis
```
호스트: localhost
포트: 6379
비밀번호: redis123
관리 UI: http://localhost:8082
```

## Celery 작업 스케줄

### 주기적 작업
- **Reddit 크롤링**: 매 시간 정각
- **Hacker News 크롤링**: 매 30분
- **GitHub 크롤링**: 매 6시간
- **트렌드 분석**: 매일 자정
- **주간 리포트**: 매주 월요일 오전 9시
- **데이터 정리**: 매일 새벽 3시

### 수동 작업 실행
```bash
# Celery Worker 컨테이너에 접속
docker exec -it stock_trends_celery_worker bash

# 작업 수동 실행
celery -A celery_app call tasks.crawl_reddit
celery -A celery_app call tasks.analyze_trends
```

## 크롤링 실행

### 방법 1: Docker 컨테이너 내에서 실행
```bash
# Worker 컨테이너 접속
docker exec -it stock_trends_celery_worker bash

# Scrapy 크롤링 실행
cd stock_tech_trends
scrapy crawl reddit_spider -o ../data/reddit_test.json
```

### 방법 2: 로컬에서 실행 (데이터베이스는 Docker 사용)
```bash
# .env 파일 업데이트 (Docker 서비스 주소로 변경)
MONGODB_URI=mongodb://admin:admin123@localhost:27017
POSTGRES_URL=postgresql://stock_user:stock_pass123@localhost:5432/stock_trends
REDIS_URL=redis://:redis123@localhost:6379/0

# Scrapy 크롤링 실행
cd stock_tech_trends
scrapy crawl reddit_spider -o ../data/reddit_test.json
```

## 모니터링

### 1. Flower (Celery 모니터링)
- URL: http://localhost:5555
- 실시간 작업 상태, 워커 상태, 작업 히스토리 확인

### 2. Grafana (시각화 대시보드)
- URL: http://localhost:3000
- 계정: admin / admin123
- MongoDB, PostgreSQL 데이터 소스 연결 후 대시보드 생성

### 3. 데이터베이스 관리 UI
- MongoDB: http://localhost:8081
- PostgreSQL: http://localhost:5050
- Redis: http://localhost:8082

## 트러블슈팅

### 포트 충돌
```bash
# 사용 중인 포트 확인
netstat -ano | findstr :27017
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# docker-compose.yml에서 포트 변경
ports:
  - "27018:27017"  # 외부:내부
```

### 컨테이너 재시작
```bash
# 특정 서비스만 재시작
docker-compose restart mongodb
docker-compose restart celery-worker

# 모든 서비스 재시작
docker-compose restart
```

### 로그 확인
```bash
# 실시간 로그
docker-compose logs -f

# 최근 100줄
docker-compose logs --tail=100

# 특정 서비스
docker-compose logs -f celery-worker
```

### 데이터 초기화
```bash
# 모든 데이터 삭제 (주의!)
docker-compose down -v

# 특정 볼륨만 삭제
docker volume rm trends_pj_mongodb_data
docker volume rm trends_pj_postgres_data
docker volume rm trends_pj_redis_data
```

### 컨테이너 내부 접속
```bash
# MongoDB 컨테이너
docker exec -it stock_trends_mongodb mongosh -u admin -p admin123

# PostgreSQL 컨테이너
docker exec -it stock_trends_postgres psql -U stock_user -d stock_trends

# Redis 컨테이너
docker exec -it stock_trends_redis redis-cli -a redis123

# Worker 컨테이너
docker exec -it stock_trends_celery_worker bash
```

## 성능 최적화

### 리소스 제한 설정
`docker-compose.yml`에 추가:
```yaml
services:
  mongodb:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 볼륨 백업
```bash
# MongoDB 백업
docker exec stock_trends_mongodb mongodump --out /backup --authenticationDatabase admin -u admin -p admin123

# PostgreSQL 백업
docker exec stock_trends_postgres pg_dump -U stock_user stock_trends > backup.sql
```

## 프로덕션 배포

### 1. 환경 변수 보안
```bash
# .env 파일을 안전한 곳에 보관
# 강력한 비밀번호 사용
# Secrets 관리 도구 사용 (AWS Secrets Manager, HashiCorp Vault 등)
```

### 2. 네트워크 보안
```bash
# 외부 접근 제한
# 방화벽 설정
# HTTPS 사용
```

### 3. 모니터링 및 알림
```bash
# Prometheus + Grafana
# Sentry (에러 모니터링)
# Slack/Discord 알림
```

## 추가 리소스

- Docker 공식 문서: https://docs.docker.com/
- Docker Compose 문서: https://docs.docker.com/compose/
- Scrapy 문서: https://docs.scrapy.org/
- Celery 문서: https://docs.celeryproject.org/

