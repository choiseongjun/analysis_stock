"""
Celery 애플리케이션 설정
"""

import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# Celery 앱 생성
app = Celery(
    'stock_tech_trends',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    include=['tasks']
)

# Celery 설정
app.conf.update(
    # 작업 설정
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    
    # 작업 시간 제한
    task_soft_time_limit=3600,  # 1시간
    task_time_limit=7200,  # 2시간
    
    # 재시도 설정
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # 결과 설정
    result_expires=3600,  # 1시간
    result_backend_transport_options={'master_name': 'mymaster'},
    
    # 워커 설정
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # 로깅
    worker_hijack_root_logger=False,
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)

# 주기적 작업 스케줄
app.conf.beat_schedule = {
    # Reddit 크롤링 - 매 시간마다
    'crawl-reddit-hourly': {
        'task': 'tasks.crawl_reddit',
        'schedule': crontab(minute=0),  # 매 시간 정각
    },
    
    # Hacker News 크롤링 - 매 30분마다
    'crawl-hackernews-30min': {
        'task': 'tasks.crawl_hackernews',
        'schedule': timedelta(minutes=30),
    },
    
    # GitHub 크롤링 - 매 6시간마다
    'crawl-github-6hours': {
        'task': 'tasks.crawl_github',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    
    # 트렌드 분석 - 매일 자정
    'analyze-trends-daily': {
        'task': 'tasks.analyze_trends',
        'schedule': crontab(minute=0, hour=0),
    },
    
    # 리포트 생성 - 매주 월요일 오전 9시
    'generate-report-weekly': {
        'task': 'tasks.generate_weekly_report',
        'schedule': crontab(minute=0, hour=9, day_of_week=1),
    },
    
    # 오래된 데이터 정리 - 매일 새벽 3시
    'cleanup-old-data': {
        'task': 'tasks.cleanup_old_data',
        'schedule': crontab(minute=0, hour=3),
    },
}

if __name__ == '__main__':
    app.start()
