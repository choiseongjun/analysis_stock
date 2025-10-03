import scrapy
import json
import requests
from datetime import datetime
from ..items import HackerNewsItem


class HackernewsSpiderSpider(scrapy.Spider):
    name = "hackernews_spider"
    allowed_domains = ["hacker-news.firebaseio.com", "news.ycombinator.com"]
    
    # Hacker News API를 사용하므로 start_urls는 사용하지 않음
    start_urls = []
    
    def start_requests(self):
        """Hacker News API를 사용하여 최신 스토리들 가져오기"""
        # Hacker News API 엔드포인트
        api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        
        try:
            # 최신 스토리 ID 목록 가져오기
            response = requests.get(api_url)
            response.raise_for_status()
            
            story_ids = response.json()
            
            # 상위 100개 스토리만 처리
            for story_id in story_ids[:100]:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                
                yield scrapy.Request(
                    url=story_url,
                    callback=self.parse_story,
                    meta={'story_id': story_id},
                    dont_filter=True
                )
                
        except Exception as e:
            self.logger.error(f"Failed to fetch Hacker News stories: {e}")
    
    def parse_story(self, response):
        """개별 스토리 파싱"""
        try:
            data = json.loads(response.text)
            
            if not data or data.get('type') != 'story':
                return
            
            # 기술/주식 관련 키워드 필터링
            if self._is_relevant_story(data):
                item = HackerNewsItem()
                
                # 기본 정보
                item['item_id'] = str(data.get('id'))
                item['title'] = data.get('title', '')
                item['url'] = data.get('url', '')
                item['score'] = data.get('score', 0)
                item['by'] = data.get('by', '')
                
                # 시간 정보
                time_stamp = data.get('time')
                if time_stamp:
                    item['time'] = datetime.fromtimestamp(time_stamp).isoformat()
                
                # 댓글 정보
                item['descendants'] = data.get('descendants', 0)
                item['type'] = data.get('type', 'story')
                item['text'] = data.get('text', '')
                
                # 기술 키워드 추출
                text_content = item['title'] + ' ' + (item['text'] or '')
                item['tech_keywords'] = self._extract_tech_keywords(text_content)
                
                yield item
                
        except Exception as e:
            self.logger.error(f"Error parsing story {response.meta['story_id']}: {e}")
    
    def _is_relevant_story(self, story):
        """스토리가 기술/주식 관련인지 확인"""
        title = story.get('title', '').lower()
        text = story.get('text', '').lower()
        combined_text = title + ' ' + text
        
        # 기술 키워드 체크
        tech_keywords = self.settings.get('TECH_KEYWORDS', [])
        stock_keywords = self.settings.get('STOCK_KEYWORDS', [])
        blocked_keywords = self.settings.get('BLOCKED_KEYWORDS', [])
        
        # 금지된 키워드 체크
        for blocked in blocked_keywords:
            if blocked.lower() in combined_text:
                return False
        
        # 기술 또는 주식 키워드가 포함되어 있는지 확인
        relevant_keywords = tech_keywords + stock_keywords
        for keyword in relevant_keywords:
            if keyword.lower() in combined_text:
                return True
        
        # 높은 점수나 많은 댓글이 있는 스토리는 포함
        score = story.get('score', 0)
        descendants = story.get('descendants', 0)
        
        if score > 100 or descendants > 20:
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
