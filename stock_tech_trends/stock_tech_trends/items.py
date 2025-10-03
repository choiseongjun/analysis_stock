# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime


class RedditPostItem(scrapy.Item):
    """Reddit 포스트 데이터 모델"""
    post_id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    subreddit = scrapy.Field()
    score = scrapy.Field()
    upvote_ratio = scrapy.Field()
    num_comments = scrapy.Field()
    created_utc = scrapy.Field()
    url = scrapy.Field()
    permalink = scrapy.Field()
    is_self = scrapy.Field()
    domain = scrapy.Field()
    crawled_at = scrapy.Field()
    sentiment_score = scrapy.Field()
    tech_keywords = scrapy.Field()
    stock_tickers = scrapy.Field()


class HackerNewsItem(scrapy.Item):
    """Hacker News 아이템 데이터 모델"""
    item_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    score = scrapy.Field()
    by = scrapy.Field()
    time = scrapy.Field()
    descendants = scrapy.Field()  # 댓글 수
    type = scrapy.Field()  # story, comment, poll 등
    text = scrapy.Field()  # 텍스트 내용 (있는 경우)
    crawled_at = scrapy.Field()
    sentiment_score = scrapy.Field()
    tech_keywords = scrapy.Field()


class JobPostingItem(scrapy.Item):
    """채용 공고 데이터 모델"""
    job_id = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    requirements = scrapy.Field()
    salary_range = scrapy.Field()
    job_type = scrapy.Field()  # full-time, part-time, contract
    remote = scrapy.Field()
    posted_date = scrapy.Field()
    source = scrapy.Field()  # indeed, linkedin 등
    url = scrapy.Field()
    crawled_at = scrapy.Field()
    tech_skills = scrapy.Field()
    seniority_level = scrapy.Field()


class GitHubRepoItem(scrapy.Item):
    """GitHub 저장소 데이터 모델"""
    repo_id = scrapy.Field()
    name = scrapy.Field()
    full_name = scrapy.Field()
    description = scrapy.Field()
    owner = scrapy.Field()
    language = scrapy.Field()
    languages = scrapy.Field()  # 모든 언어와 비율
    stars = scrapy.Field()
    forks = scrapy.Field()
    watchers = scrapy.Field()
    open_issues = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    pushed_at = scrapy.Field()
    topics = scrapy.Field()
    license = scrapy.Field()
    size = scrapy.Field()
    crawled_at = scrapy.Field()


class StackOverflowItem(scrapy.Item):
    """Stack Overflow 질문/답변 데이터 모델"""
    question_id = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
    tags = scrapy.Field()
    score = scrapy.Field()
    view_count = scrapy.Field()
    answer_count = scrapy.Field()
    accepted_answer_id = scrapy.Field()
    owner = scrapy.Field()
    created_date = scrapy.Field()
    last_activity_date = scrapy.Field()
    is_answered = scrapy.Field()
    crawled_at = scrapy.Field()
    tech_category = scrapy.Field()


class CompanyNewsItem(scrapy.Item):
    """기업 뉴스/IR 데이터 모델"""
    news_id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    company = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    published_date = scrapy.Field()
    news_type = scrapy.Field()  # earnings, product_launch, partnership 등
    crawled_at = scrapy.Field()
    sentiment_score = scrapy.Field()
    impact_score = scrapy.Field()  # 주가 영향도 예측 점수
