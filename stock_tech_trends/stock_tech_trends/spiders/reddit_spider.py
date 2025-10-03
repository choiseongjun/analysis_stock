import scrapy
import json
import base64
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
from ..items import RedditPostItem
import sys
import os

# utils 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
from utils.stock_ticker_extractor import extract_stock_tickers


class RedditSpiderSpider(scrapy.Spider):
    name = "reddit_spider"
    allowed_domains = ["reddit.com", "oauth.reddit.com"]
    
    # Reddit API를 사용하므로 start_urls는 사용하지 않음
    start_urls = []
    
    # 기술 관련 서브레딧 목록
    tech_subreddits = [
        'MachineLearning', 'artificial', 'datascience', 'programming',
        'Python', 'javascript', 'webdev', 'startups', 'investing',
        'stocks', 'SecurityAnalysis', 'ValueInvesting', 'cryptocurrency',
        'ethereum', 'bitcoin', 'blockchain', 'technology', 'gadgets',
        'hardware', 'software', 'cloudcomputing', 'devops', 'kubernetes',
        'docker', 'aws', 'azure', 'gcp', 'ai', 'deeplearning',
        'computervision', 'nlp', 'robotics', 'IoT', '5G', 'quantumcomputing'
    ]
    
    def __init__(self, *args, **kwargs):
        super(RedditSpiderSpider, self).__init__(*args, **kwargs)
        self.access_token = None
        self.headers = {}
        
    def start_requests(self):
        """Reddit API 인증 후 크롤링 시작"""
        # Reddit API 인증
        auth_url = "https://www.reddit.com/api/v1/access_token"
        
        # 환경 변수에서 API 키 가져오기
        client_id = self.settings.get('REDDIT_CLIENT_ID')
        client_secret = self.settings.get('REDDIT_CLIENT_SECRET')
        user_agent = self.settings.get('REDDIT_USER_AGENT', 'StockTechTrends/1.0')
        
        if not client_id or not client_secret:
            self.logger.error("Reddit API credentials not found in settings")
            return
        
        # API 인증 요청
        auth_data = {
            'grant_type': 'client_credentials'
        }
        
        auth_string = f"{client_id}:{client_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        auth_headers = {
            'Authorization': f'Basic {auth_b64}',
            'User-Agent': user_agent
        }
        
        # 인증 토큰 요청
        try:
            response = requests.post(auth_url, data=auth_data, headers=auth_headers)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # API 요청용 헤더 설정
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': user_agent
            }
            
            self.logger.info("Reddit API authentication successful")
            
            # 각 서브레딧에 대해 크롤링 요청 생성
            for subreddit in self.tech_subreddits:
                yield scrapy.Request(
                    url=f"https://oauth.reddit.com/r/{subreddit}/hot.json?limit=100",
                    headers=self.headers,
                    callback=self.parse_subreddit,
                    meta={'subreddit': subreddit},
                    dont_filter=True
                )
                
        except Exception as e:
            self.logger.error(f"Reddit API authentication failed: {e}")
    
    def parse_subreddit(self, response):
        """서브레딧의 포스트들을 파싱"""
        try:
            data = json.loads(response.text)
            subreddit = response.meta['subreddit']
            
            if 'data' not in data or 'children' not in data['data']:
                self.logger.warning(f"No data found for subreddit: {subreddit}")
                return
            
            posts = data['data']['children']
            
            for post_data in posts:
                post = post_data['data']
                
                # 기술/주식 관련 키워드 필터링
                if self._is_relevant_post(post):
                    item = RedditPostItem()
                    
                    # 기본 정보
                    item['post_id'] = post.get('id')
                    item['title'] = post.get('title', '')
                    item['content'] = post.get('selftext', '')
                    item['author'] = post.get('author')
                    item['subreddit'] = subreddit
                    
                    # 통계 정보
                    item['score'] = post.get('score', 0)
                    item['upvote_ratio'] = post.get('upvote_ratio', 0)
                    item['num_comments'] = post.get('num_comments', 0)
                    
                    # 시간 정보
                    created_utc = post.get('created_utc')
                    if created_utc:
                        item['created_utc'] = datetime.fromtimestamp(created_utc).isoformat()
                    
                    # URL 정보
                    item['url'] = post.get('url', '')
                    item['permalink'] = f"https://reddit.com{post.get('permalink', '')}"
                    item['is_self'] = post.get('is_self', False)
                    item['domain'] = post.get('domain', '')
                    
                    # 기술 키워드 추출
                    item['tech_keywords'] = self._extract_tech_keywords(
                        item['title'] + ' ' + item['content']
                    )
                    
                    # 주식 티커 심볼 추출
                    item['stock_tickers'] = self._extract_stock_tickers(
                        item['title'] + ' ' + item['content']
                    )
                    
                    yield item
                    
        except Exception as e:
            self.logger.error(f"Error parsing subreddit {response.meta['subreddit']}: {e}")
    
    def _is_relevant_post(self, post):
        """포스트가 기술/주식 관련인지 확인"""
        title = post.get('title', '').lower()
        content = post.get('selftext', '').lower()
        text = title + ' ' + content
        
        # 기술 키워드 체크
        tech_keywords = self.settings.get('TECH_KEYWORDS', [])
        stock_keywords = self.settings.get('STOCK_KEYWORDS', [])
        blocked_keywords = self.settings.get('BLOCKED_KEYWORDS', [])
        
        # 금지된 키워드 체크
        for blocked in blocked_keywords:
            if blocked.lower() in text:
                return False
        
        # 기술 또는 주식 키워드가 포함되어 있는지 확인
        relevant_keywords = tech_keywords + stock_keywords
        for keyword in relevant_keywords:
            if keyword.lower() in text:
                return True
        
        # 점수나 댓글 수로 인기도 체크
        score = post.get('score', 0)
        num_comments = post.get('num_comments', 0)
        
        # 높은 점수나 많은 댓글이 있는 포스트는 포함
        if score > 50 or num_comments > 10:
            return True
        
        return False
    
    def _extract_tech_keywords(self, text):
        """텍스트에서 기술 키워드 추출"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        tech_keywords = self.settings.get('TECH_KEYWORDS', [])
        stock_keywords = self.settings.get('STOCK_KEYWORDS', [])
        
        all_keywords = tech_keywords + stock_keywords
        
        for keyword in all_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_stock_tickers(self, text):
        """텍스트에서 주식 티커 심볼 추출"""
        if not text:
            return []
        
        try:
            tickers = extract_stock_tickers(text)
            return tickers
        except Exception as e:
            self.logger.warning(f"Error extracting stock tickers: {e}")
            return []
