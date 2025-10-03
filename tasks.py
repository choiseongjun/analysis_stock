"""
Celery 작업 정의
"""

import os
import subprocess
import json
from datetime import datetime, timedelta
from celery_app import app
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

# 데이터베이스 연결 설정
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql://user:password@localhost:5432/stock_trends')


@app.task(bind=True, max_retries=3)
def crawl_reddit(self):
    """Reddit 크롤링 작업"""
    try:
        logger.info("Reddit 크롤링 시작...")
        
        # Scrapy 크롤러 실행
        result = subprocess.run(
            ['scrapy', 'crawl', 'reddit_spider', '-o', f'data/reddit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'],
            cwd='stock_tech_trends',
            capture_output=True,
            text=True,
            timeout=1800  # 30분 타임아웃
        )
        
        if result.returncode == 0:
            logger.info("Reddit 크롤링 완료")
            return {'status': 'success', 'message': 'Reddit crawling completed'}
        else:
            logger.error(f"Reddit 크롤링 실패: {result.stderr}")
            raise Exception(f"Crawling failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Reddit 크롤링 오류: {e}")
        raise self.retry(exc=e, countdown=300)  # 5분 후 재시도


@app.task(bind=True, max_retries=3)
def crawl_hackernews(self):
    """Hacker News 크롤링 작업"""
    try:
        logger.info("Hacker News 크롤링 시작...")
        
        result = subprocess.run(
            ['scrapy', 'crawl', 'hackernews_spider', '-o', f'data/hn_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'],
            cwd='stock_tech_trends',
            capture_output=True,
            text=True,
            timeout=1800
        )
        
        if result.returncode == 0:
            logger.info("Hacker News 크롤링 완료")
            return {'status': 'success', 'message': 'Hacker News crawling completed'}
        else:
            logger.error(f"Hacker News 크롤링 실패: {result.stderr}")
            raise Exception(f"Crawling failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Hacker News 크롤링 오류: {e}")
        raise self.retry(exc=e, countdown=300)


@app.task(bind=True, max_retries=3)
def crawl_github(self):
    """GitHub 크롤링 작업"""
    try:
        logger.info("GitHub 크롤링 시작...")
        
        result = subprocess.run(
            ['scrapy', 'crawl', 'github_spider', '-o', f'data/github_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'],
            cwd='stock_tech_trends',
            capture_output=True,
            text=True,
            timeout=1800
        )
        
        if result.returncode == 0:
            logger.info("GitHub 크롤링 완료")
            return {'status': 'success', 'message': 'GitHub crawling completed'}
        else:
            logger.error(f"GitHub 크롤링 실패: {result.stderr}")
            raise Exception(f"Crawling failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"GitHub 크롤링 오류: {e}")
        raise self.retry(exc=e, countdown=300)


@app.task
def analyze_trends():
    """트렌드 분석 작업"""
    try:
        logger.info("트렌드 분석 시작...")
        
        # 트렌드 분석 스크립트 실행
        result = subprocess.run(
            ['python', 'data_analysis/trend_analyzer.py'],
            capture_output=True,
            text=True,
            timeout=600  # 10분 타임아웃
        )
        
        if result.returncode == 0:
            logger.info("트렌드 분석 완료")
            return {'status': 'success', 'message': 'Trend analysis completed'}
        else:
            logger.error(f"트렌드 분석 실패: {result.stderr}")
            return {'status': 'error', 'message': result.stderr}
            
    except Exception as e:
        logger.error(f"트렌드 분석 오류: {e}")
        return {'status': 'error', 'message': str(e)}


@app.task
def generate_weekly_report():
    """주간 리포트 생성"""
    try:
        logger.info("주간 리포트 생성 시작...")
        
        # MongoDB에서 데이터 수집
        client = MongoClient(MONGODB_URI)
        db = client['stock_tech_trends']
        
        # 지난 주 데이터
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        collections = ['reddit_posts', 'hackernews_items', 'github_repos']
        report = {
            'report_date': datetime.utcnow().isoformat(),
            'period': '7_days',
            'summary': {}
        }
        
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({'crawled_at': {'$gte': week_ago.isoformat()}})
            report['summary'][collection_name] = count
        
        # 리포트 저장
        os.makedirs('reports', exist_ok=True)
        report_file = f"reports/weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        client.close()
        
        logger.info(f"주간 리포트 생성 완료: {report_file}")
        return {'status': 'success', 'report_file': report_file, 'summary': report['summary']}
        
    except Exception as e:
        logger.error(f"주간 리포트 생성 오류: {e}")
        return {'status': 'error', 'message': str(e)}


@app.task
def cleanup_old_data():
    """오래된 데이터 정리 (30일 이상)"""
    try:
        logger.info("오래된 데이터 정리 시작...")
        
        # 30일 이전 데이터
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # MongoDB 정리
        client = MongoClient(MONGODB_URI)
        db = client['stock_tech_trends']
        
        collections = ['reddit_posts', 'hackernews_items', 'github_repos']
        deleted_counts = {}
        
        for collection_name in collections:
            collection = db[collection_name]
            result = collection.delete_many({'crawled_at': {'$lt': cutoff_date.isoformat()}})
            deleted_counts[collection_name] = result.deleted_count
        
        client.close()
        
        # PostgreSQL 정리
        conn = psycopg2.connect(POSTGRES_URL)
        cursor = conn.cursor()
        
        tables = ['reddit_posts', 'hackernews_items', 'github_repos']
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table} WHERE crawled_at < %s", (cutoff_date,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"오래된 데이터 정리 완료: {deleted_counts}")
        return {'status': 'success', 'deleted_counts': deleted_counts}
        
    except Exception as e:
        logger.error(f"데이터 정리 오류: {e}")
        return {'status': 'error', 'message': str(e)}


@app.task
def send_trend_alert(trend_data):
    """트렌드 알림 전송"""
    try:
        logger.info(f"트렌드 알림 전송: {trend_data}")
        
        # 여기에 이메일, Slack, Discord 등 알림 로직 추가
        # 예: send_email(trend_data)
        # 예: send_slack_message(trend_data)
        
        return {'status': 'success', 'message': 'Alert sent'}
        
    except Exception as e:
        logger.error(f"알림 전송 오류: {e}")
        return {'status': 'error', 'message': str(e)}

