import scrapy
import json
import requests
from datetime import datetime
from ..items import GitHubRepoItem


class GithubSpiderSpider(scrapy.Spider):
    name = "github_spider"
    allowed_domains = ["api.github.com", "github.com"]
    
    # GitHub API를 사용하므로 start_urls는 사용하지 않음
    start_urls = []
    
    # 기술 관련 검색 쿼리 목록
    tech_queries = [
        'machine learning', 'artificial intelligence', 'deep learning',
        'blockchain', 'cryptocurrency', 'web3', 'defi',
        'cloud computing', 'kubernetes', 'docker', 'microservices',
        'data science', 'big data', 'analytics', 'visualization',
        'cybersecurity', 'penetration testing', 'vulnerability',
        'mobile development', 'react native', 'flutter',
        'quantum computing', 'computer vision', 'nlp',
        'robotics', 'iot', '5g', 'edge computing',
        'ar', 'vr', 'metaverse', 'nft'
    ]
    
    def start_requests(self):
        """GitHub API를 사용하여 기술 관련 저장소들 검색"""
        # GitHub API 토큰 가져오기
        token = self.settings.get('GITHUB_TOKEN')
        
        if not token:
            self.logger.error("GitHub API token not found in settings")
            return
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'StockTechTrends/1.0'
        }
        
        # 각 기술 쿼리에 대해 검색 요청 생성
        for query in self.tech_queries:
            # 최근 7일 내에 업데이트된 저장소만 검색
            search_url = (
                f"https://api.github.com/search/repositories"
                f"?q={query}+pushed:>{(datetime.now().timestamp() - 7*24*3600):.0f}"
                f"&sort=stars&order=desc&per_page=50"
            )
            
            yield scrapy.Request(
                url=search_url,
                headers=headers,
                callback=self.parse_search_results,
                meta={'query': query},
                dont_filter=True
            )
    
    def parse_search_results(self, response):
        """검색 결과 파싱"""
        try:
            data = json.loads(response.text)
            query = response.meta['query']
            
            if 'items' not in data:
                self.logger.warning(f"No items found for query: {query}")
                return
            
            repos = data['items']
            
            for repo_data in repos:
                # 기술 관련 저장소 필터링
                if self._is_relevant_repo(repo_data):
                    item = GitHubRepoItem()
                    
                    # 기본 정보
                    item['repo_id'] = str(repo_data.get('id'))
                    item['name'] = repo_data.get('name', '')
                    item['full_name'] = repo_data.get('full_name', '')
                    item['description'] = repo_data.get('description', '')
                    
                    # 소유자 정보
                    owner = repo_data.get('owner', {})
                    item['owner'] = owner.get('login', '')
                    
                    # 언어 정보
                    item['language'] = repo_data.get('language', '')
                    item['languages'] = {}  # 별도 API 호출로 채워질 예정
                    
                    # 통계 정보
                    item['stars'] = repo_data.get('stargazers_count', 0)
                    item['forks'] = repo_data.get('forks_count', 0)
                    item['watchers'] = repo_data.get('watchers_count', 0)
                    item['open_issues'] = repo_data.get('open_issues_count', 0)
                    item['size'] = repo_data.get('size', 0)
                    
                    # 시간 정보
                    created_at = repo_data.get('created_at')
                    if created_at:
                        item['created_at'] = created_at
                    
                    updated_at = repo_data.get('updated_at')
                    if updated_at:
                        item['updated_at'] = updated_at
                    
                    pushed_at = repo_data.get('pushed_at')
                    if pushed_at:
                        item['pushed_at'] = pushed_at
                    
                    # 기타 정보
                    item['topics'] = repo_data.get('topics', [])
                    item['license'] = repo_data.get('license', {}).get('name', '') if repo_data.get('license') else ''
                    
                    # 언어 정보를 위한 추가 요청
                    languages_url = repo_data.get('languages_url')
                    if languages_url:
                        yield scrapy.Request(
                            url=languages_url,
                            headers=response.request.headers,
                            callback=self.parse_languages,
                            meta={'item': item},
                            dont_filter=True
                        )
                    else:
                        yield item
                        
        except Exception as e:
            self.logger.error(f"Error parsing search results for query {response.meta['query']}: {e}")
    
    def parse_languages(self, response):
        """저장소의 언어 정보 파싱"""
        try:
            item = response.meta['item']
            languages_data = json.loads(response.text)
            
            # 언어 정보 추가
            item['languages'] = languages_data
            
            yield item
            
        except Exception as e:
            self.logger.error(f"Error parsing languages: {e}")
            # 언어 정보 파싱 실패 시에도 기본 아이템 반환
            yield response.meta['item']
    
    def _is_relevant_repo(self, repo):
        """저장소가 기술 관련인지 확인"""
        name = repo.get('name', '').lower()
        description = repo.get('description', '').lower()
        topics = [topic.lower() for topic in repo.get('topics', [])]
        
        combined_text = name + ' ' + description + ' ' + ' '.join(topics)
        
        # 기술 키워드 체크
        tech_keywords = self.settings.get('TECH_KEYWORDS', [])
        
        for keyword in tech_keywords:
            if keyword.lower() in combined_text:
                return True
        
        # 인기도 체크 (별표 수)
        stars = repo.get('stargazers_count', 0)
        if stars > 100:  # 100개 이상의 별표를 받은 저장소
            return True
        
        return False
