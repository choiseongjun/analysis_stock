# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import hashlib
import re
from datetime import datetime
from typing import Dict, Any, List

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymongo
import psycopg2
from psycopg2.extras import RealDictCursor
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

logger = logging.getLogger(__name__)


class ValidationPipeline:
    """데이터 검증 파이프라인"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # 필수 필드 검증
        if not adapter.get('title') or not adapter.get('title').strip():
            raise DropItem(f"Missing title in {item}")
        
        # 텍스트 길이 검증
        title = adapter.get('title', '')
        if len(title) < 10 or len(title) > 500:
            raise DropItem(f"Invalid title length: {len(title)}")
        
        # URL 검증
        url = adapter.get('url', '')
        if url and not self._is_valid_url(url):
            raise DropItem(f"Invalid URL: {url}")
        
        # 크롤링 시간 추가
        adapter['crawled_at'] = datetime.utcnow().isoformat()
        
        return item
    
    def _is_valid_url(self, url: str) -> bool:
        """URL 유효성 검사"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None


class SentimentAnalysisPipeline:
    """감성 분석 파이프라인"""
    
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # 분석할 텍스트 수집
        text_parts = []
        
        if adapter.get('title'):
            text_parts.append(adapter['title'])
        if adapter.get('content'):
            text_parts.append(adapter['content'])
        if adapter.get('description'):
            text_parts.append(adapter['description'])
        if adapter.get('body'):
            text_parts.append(adapter['body'])
        
        if text_parts:
            combined_text = ' '.join(text_parts)
            sentiment_score = self._analyze_sentiment(combined_text)
            adapter['sentiment_score'] = sentiment_score
        
        return item
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """VADER를 사용한 감성 분석"""
        try:
            # VADER 감성 분석
            vader_scores = self.vader_analyzer.polarity_scores(text)
            
            # TextBlob 감성 분석 (보조)
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            return {
                'vader_compound': vader_scores['compound'],
                'vader_positive': vader_scores['pos'],
                'vader_neutral': vader_scores['neu'],
                'vader_negative': vader_scores['neg'],
                'textblob_polarity': textblob_polarity,
                'textblob_subjectivity': textblob_subjectivity,
                'overall_sentiment': self._get_overall_sentiment(vader_scores['compound'])
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                'vader_compound': 0.0,
                'vader_positive': 0.0,
                'vader_neutral': 1.0,
                'vader_negative': 0.0,
                'textblob_polarity': 0.0,
                'textblob_subjectivity': 0.5,
                'overall_sentiment': 'neutral'
            }
    
    def _get_overall_sentiment(self, compound_score: float) -> str:
        """전체 감성 분류"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'


class MongoDBPipeline:
    """MongoDB 저장 파이프라인"""
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DATABASE')
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        
        # 컬렉션별 인덱스 생성
        self._create_indexes()
    
    def close_spider(self, spider):
        self.client.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # 아이템 타입에 따른 컬렉션 선택
        collection_name = self._get_collection_name(item)
        collection = self.db[collection_name]
        
        # 중복 체크를 위한 고유 키 생성
        unique_key = self._generate_unique_key(item)
        
        # 업서트 (중복이면 업데이트, 없으면 삽입)
        collection.update_one(
            {'unique_key': unique_key},
            {'$set': dict(adapter)},
            upsert=True
        )
        
        logger.info(f"Saved {collection_name} item: {unique_key}")
        return item
    
    def _get_collection_name(self, item) -> str:
        """아이템 타입에 따른 컬렉션 이름 반환"""
        item_type = type(item).__name__
        collection_mapping = {
            'RedditPostItem': 'reddit_posts',
            'HackerNewsItem': 'hackernews_items',
            'JobPostingItem': 'job_postings',
            'GitHubRepoItem': 'github_repos',
            'StackOverflowItem': 'stackoverflow_items',
            'CompanyNewsItem': 'company_news'
        }
        return collection_mapping.get(item_type, 'general_items')
    
    def _generate_unique_key(self, item) -> str:
        """아이템의 고유 키 생성"""
        adapter = ItemAdapter(item)
        
        # 아이템 타입별 고유 키 생성
        if 'post_id' in adapter:
            return f"reddit_{adapter['post_id']}"
        elif 'item_id' in adapter:
            return f"hn_{adapter['item_id']}"
        elif 'job_id' in adapter:
            return f"job_{adapter['job_id']}"
        elif 'repo_id' in adapter:
            return f"repo_{adapter['repo_id']}"
        elif 'question_id' in adapter:
            return f"so_{adapter['question_id']}"
        elif 'news_id' in adapter:
            return f"news_{adapter['news_id']}"
        else:
            # URL 기반 해시 생성
            url = adapter.get('url', '')
            return hashlib.md5(url.encode()).hexdigest()
    
    def _create_indexes(self):
        """컬렉션별 인덱스 생성"""
        indexes = {
            'reddit_posts': [
                [('post_id', 1), ('unique', True)],
                [('subreddit', 1), ('created_utc', -1)],
                [('crawled_at', -1)],
                [('sentiment_score.vader_compound', 1)]
            ],
            'hackernews_items': [
                [('item_id', 1), ('unique', True)],
                [('time', -1)],
                [('score', -1)],
                [('crawled_at', -1)]
            ],
            'job_postings': [
                [('job_id', 1), ('unique', True)],
                [('company', 1), ('posted_date', -1)],
                [('tech_skills', 1)],
                [('crawled_at', -1)]
            ],
            'github_repos': [
                [('repo_id', 1), ('unique', True)],
                [('language', 1), ('stars', -1)],
                [('created_at', -1)],
                [('crawled_at', -1)]
            ],
            'stackoverflow_items': [
                [('question_id', 1), ('unique', True)],
                [('tags', 1), ('score', -1)],
                [('created_date', -1)],
                [('crawled_at', -1)]
            ],
            'company_news': [
                [('news_id', 1), ('unique', True)],
                [('company', 1), ('published_date', -1)],
                [('news_type', 1)],
                [('crawled_at', -1)]
            ]
        }
        
        for collection_name, index_list in indexes.items():
            collection = self.db[collection_name]
            for index_spec in index_list:
                try:
                    collection.create_index(index_spec[0], unique=index_spec[1] if len(index_spec) > 1 else False)
                except Exception as e:
                    logger.warning(f"Index creation failed for {collection_name}: {e}")


class PostgreSQLPipeline:
    """PostgreSQL 저장 파이프라인"""
    
    def __init__(self, postgres_url):
        self.postgres_url = postgres_url
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            postgres_url=crawler.settings.get('POSTGRES_URL')
        )
    
    def open_spider(self, spider):
        self.connection = psycopg2.connect(self.postgres_url)
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        self._create_tables()
    
    def close_spider(self, spider):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # 아이템 타입에 따른 테이블 선택
        table_name = self._get_table_name(item)
        
        # 데이터 삽입
        self._insert_item(adapter, table_name)
        
        return item
    
    def _get_table_name(self, item) -> str:
        """아이템 타입에 따른 테이블 이름 반환"""
        item_type = type(item).__name__
        table_mapping = {
            'RedditPostItem': 'reddit_posts',
            'HackerNewsItem': 'hackernews_items',
            'JobPostingItem': 'job_postings',
            'GitHubRepoItem': 'github_repos',
            'StackOverflowItem': 'stackoverflow_items',
            'CompanyNewsItem': 'company_news'
        }
        return table_mapping.get(item_type, 'general_items')
    
    def _insert_item(self, adapter, table_name):
        """아이템을 테이블에 삽입"""
        try:
            # 동적 SQL 생성
            columns = list(adapter.keys())
            values = [adapter[col] for col in columns]
            placeholders = ', '.join(['%s'] * len(columns))
            
            query = f"""
                INSERT INTO {table_name} ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT (unique_key) DO UPDATE SET
                {', '.join([f"{col} = EXCLUDED.{col}" for col in columns])}
            """
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"PostgreSQL insert error: {e}")
            self.connection.rollback()
    
    def _create_tables(self):
        """필요한 테이블 생성"""
        tables = {
            'reddit_posts': """
                CREATE TABLE IF NOT EXISTS reddit_posts (
                    unique_key VARCHAR(255) PRIMARY KEY,
                    post_id VARCHAR(50),
                    title TEXT,
                    content TEXT,
                    author VARCHAR(100),
                    subreddit VARCHAR(100),
                    score INTEGER,
                    upvote_ratio FLOAT,
                    num_comments INTEGER,
                    created_utc TIMESTAMP,
                    url TEXT,
                    permalink TEXT,
                    is_self BOOLEAN,
                    domain VARCHAR(255),
                    crawled_at TIMESTAMP,
                    sentiment_score JSONB,
                    tech_keywords TEXT[]
                )
            """,
            'hackernews_items': """
                CREATE TABLE IF NOT EXISTS hackernews_items (
                    unique_key VARCHAR(255) PRIMARY KEY,
                    item_id VARCHAR(50),
                    title TEXT,
                    url TEXT,
                    score INTEGER,
                    by VARCHAR(100),
                    time TIMESTAMP,
                    descendants INTEGER,
                    type VARCHAR(50),
                    text TEXT,
                    crawled_at TIMESTAMP,
                    sentiment_score JSONB,
                    tech_keywords TEXT[]
                )
            """,
            'job_postings': """
                CREATE TABLE IF NOT EXISTS job_postings (
                    unique_key VARCHAR(255) PRIMARY KEY,
                    job_id VARCHAR(50),
                    title TEXT,
                    company VARCHAR(255),
                    location VARCHAR(255),
                    description TEXT,
                    requirements TEXT,
                    salary_range VARCHAR(100),
                    job_type VARCHAR(50),
                    remote BOOLEAN,
                    posted_date TIMESTAMP,
                    source VARCHAR(100),
                    url TEXT,
                    crawled_at TIMESTAMP,
                    tech_skills TEXT[],
                    seniority_level VARCHAR(50)
                )
            """,
            'github_repos': """
                CREATE TABLE IF NOT EXISTS github_repos (
                    unique_key VARCHAR(255) PRIMARY KEY,
                    repo_id VARCHAR(50),
                    name VARCHAR(255),
                    full_name VARCHAR(255),
                    description TEXT,
                    owner VARCHAR(255),
                    language VARCHAR(100),
                    languages JSONB,
                    stars INTEGER,
                    forks INTEGER,
                    watchers INTEGER,
                    open_issues INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    pushed_at TIMESTAMP,
                    topics TEXT[],
                    license VARCHAR(255),
                    size INTEGER,
                    crawled_at TIMESTAMP
                )
            """,
            'stackoverflow_items': """
                CREATE TABLE IF NOT EXISTS stackoverflow_items (
                    unique_key VARCHAR(255) PRIMARY KEY,
                    question_id VARCHAR(50),
                    title TEXT,
                    body TEXT,
                    tags TEXT[],
                    score INTEGER,
                    view_count INTEGER,
                    answer_count INTEGER,
                    accepted_answer_id VARCHAR(50),
                    owner VARCHAR(255),
                    created_date TIMESTAMP,
                    last_activity_date TIMESTAMP,
                    is_answered BOOLEAN,
                    crawled_at TIMESTAMP,
                    tech_category VARCHAR(100)
                )
            """,
            'company_news': """
                CREATE TABLE IF NOT EXISTS company_news (
                    unique_key VARCHAR(255) PRIMARY KEY,
                    news_id VARCHAR(50),
                    title TEXT,
                    content TEXT,
                    company VARCHAR(255),
                    source VARCHAR(255),
                    url TEXT,
                    published_date TIMESTAMP,
                    news_type VARCHAR(100),
                    crawled_at TIMESTAMP,
                    sentiment_score JSONB,
                    impact_score FLOAT
                )
            """
        }
        
        for table_name, create_sql in tables.items():
            try:
                self.cursor.execute(create_sql)
                self.connection.commit()
            except Exception as e:
                logger.error(f"Table creation error for {table_name}: {e}")


class DuplicatesPipeline:
    """중복 제거 파이프라인"""
    
    def __init__(self):
        self.seen_urls = set()
        self.seen_titles = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # URL 기반 중복 체크
        url = adapter.get('url', '')
        if url and url in self.seen_urls:
            raise DropItem(f"Duplicate URL found: {url}")
        elif url:
            self.seen_urls.add(url)
        
        # 제목 기반 중복 체크 (URL이 없는 경우)
        title = adapter.get('title', '')
        if title and not url:
            title_hash = hashlib.md5(title.encode()).hexdigest()
            if title_hash in self.seen_titles:
                raise DropItem(f"Duplicate title found: {title}")
            else:
                self.seen_titles.add(title_hash)
        
        return item
