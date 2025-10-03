# Scrapy settings for stock_tech_trends project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

BOT_NAME = "stock_tech_trends"

SPIDER_MODULES = ["stock_tech_trends.spiders"]
NEWSPIDER_MODULE = "stock_tech_trends.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "StockTechTrends/1.0 (+https://github.com/yourusername/stock-tech-trends)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS', 16))
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = float(os.getenv('DELAY_BETWEEN_REQUESTS', 1))
DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', 30))

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    "stock_tech_trends.middlewares.StockTechTrendsSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "stock_tech_trends.middlewares.StockTechTrendsDownloaderMiddleware": 543,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 110,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
    "scrapy.extensions.logstats.LogStats": 0,
    "scrapy.extensions.corestats.CoreStats": 0,
    "scrapy.extensions.closespider.CloseSpider": 0,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "stock_tech_trends.pipelines.ValidationPipeline": 100,
    "stock_tech_trends.pipelines.SentimentAnalysisPipeline": 200,
    # "stock_tech_trends.pipelines.MongoDBPipeline": 300,  # 임시로 비활성화
    # "stock_tech_trends.pipelines.PostgreSQLPipeline": 400,  # 임시로 비활성화
    "stock_tech_trends.pipelines.DuplicatesPipeline": 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1시간
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [503, 504, 505, 500, 403, 404, 408, 429]
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# 로깅 설정
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
# LOG_FILE = os.getenv('LOG_FILE', 'logs/crawler.log')  # 임시로 비활성화

# 데이터베이스 설정
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = 'stock_tech_trends'

POSTGRES_URL = os.getenv('POSTGRES_URL', 'postgresql://user:password@localhost:5432/stock_trends')

# API 키 설정
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'StockTechTrends/1.0')

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
STACKOVERFLOW_KEY = os.getenv('STACKOVERFLOW_KEY')

# Redis 설정
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# 감성 분석 설정
SENTIMENT_MODEL = os.getenv('SENTIMENT_MODEL', 'vader')

# 크롤링 대상 설정
TECH_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 'deep learning',
    'NLP', 'computer vision', 'blockchain', 'cryptocurrency',
    'cloud computing', 'edge computing', 'quantum computing',
    'IoT', '5G', 'autonomous vehicles', 'robotics',
    'AR', 'VR', 'metaverse', 'NFT',
    'cybersecurity', 'data science', 'big data',
    'microservices', 'kubernetes', 'docker',
    'python', 'javascript', 'react', 'node.js',
    'tensorflow', 'pytorch', 'openai', 'chatgpt'
]

# 주식 관련 키워드
STOCK_KEYWORDS = [
    'stock', 'share', 'equity', 'investment', 'portfolio',
    'earnings', 'revenue', 'profit', 'growth', 'valuation',
    'IPO', 'merger', 'acquisition', 'dividend', 'buyback'
]

# 금지된 키워드 (스팸 필터링)
BLOCKED_KEYWORDS = [
    'spam', 'scam', 'fake', 'clickbait', 'advertisement'
]

# 중복 제거 설정
DUPEFILTER_CLASS = 'scrapy.dupefilters.RFPDupeFilter'
DUPEFILTER_DEBUG = True

# 재시도 설정
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# 다운로드 미들웨어 설정
DOWNLOADER_MIDDLEWARES.update({
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
})

# 스파이더 미들웨어 설정
SPIDER_MIDDLEWARES.update({
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 543,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 80,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 80,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
})
