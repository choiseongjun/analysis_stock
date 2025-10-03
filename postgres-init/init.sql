-- PostgreSQL 초기화 스크립트

-- Reddit 포스트 테이블
CREATE TABLE IF NOT EXISTS reddit_posts (
    id SERIAL PRIMARY KEY,
    unique_key VARCHAR(255) UNIQUE NOT NULL,
    post_id VARCHAR(50),
    title TEXT NOT NULL,
    content TEXT,
    author VARCHAR(100),
    subreddit VARCHAR(100),
    score INTEGER DEFAULT 0,
    upvote_ratio FLOAT,
    num_comments INTEGER DEFAULT 0,
    created_utc TIMESTAMP,
    url TEXT,
    permalink TEXT,
    is_self BOOLEAN,
    domain VARCHAR(255),
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sentiment_score JSONB,
    tech_keywords TEXT[]
);

-- Hacker News 아이템 테이블
CREATE TABLE IF NOT EXISTS hackernews_items (
    id SERIAL PRIMARY KEY,
    unique_key VARCHAR(255) UNIQUE NOT NULL,
    item_id VARCHAR(50),
    title TEXT NOT NULL,
    url TEXT,
    score INTEGER DEFAULT 0,
    by VARCHAR(100),
    time TIMESTAMP,
    descendants INTEGER DEFAULT 0,
    type VARCHAR(50),
    text TEXT,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sentiment_score JSONB,
    tech_keywords TEXT[]
);

-- 채용 공고 테이블
CREATE TABLE IF NOT EXISTS job_postings (
    id SERIAL PRIMARY KEY,
    unique_key VARCHAR(255) UNIQUE NOT NULL,
    job_id VARCHAR(50),
    title TEXT NOT NULL,
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
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tech_skills TEXT[],
    seniority_level VARCHAR(50)
);

-- GitHub 저장소 테이블
CREATE TABLE IF NOT EXISTS github_repos (
    id SERIAL PRIMARY KEY,
    unique_key VARCHAR(255) UNIQUE NOT NULL,
    repo_id VARCHAR(50),
    name VARCHAR(255),
    full_name VARCHAR(255),
    description TEXT,
    owner VARCHAR(255),
    language VARCHAR(100),
    languages JSONB,
    stars INTEGER DEFAULT 0,
    forks INTEGER DEFAULT 0,
    watchers INTEGER DEFAULT 0,
    open_issues INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    pushed_at TIMESTAMP,
    topics TEXT[],
    license VARCHAR(255),
    size INTEGER,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stack Overflow 질문 테이블
CREATE TABLE IF NOT EXISTS stackoverflow_items (
    id SERIAL PRIMARY KEY,
    unique_key VARCHAR(255) UNIQUE NOT NULL,
    question_id VARCHAR(50),
    title TEXT NOT NULL,
    body TEXT,
    tags TEXT[],
    score INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    answer_count INTEGER DEFAULT 0,
    accepted_answer_id VARCHAR(50),
    owner VARCHAR(255),
    created_date TIMESTAMP,
    last_activity_date TIMESTAMP,
    is_answered BOOLEAN,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tech_category VARCHAR(100)
);

-- 기업 뉴스 테이블
CREATE TABLE IF NOT EXISTS company_news (
    id SERIAL PRIMARY KEY,
    unique_key VARCHAR(255) UNIQUE NOT NULL,
    news_id VARCHAR(50),
    title TEXT NOT NULL,
    content TEXT,
    company VARCHAR(255),
    source VARCHAR(255),
    url TEXT,
    published_date TIMESTAMP,
    news_type VARCHAR(100),
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sentiment_score JSONB,
    impact_score FLOAT
);

-- 인덱스 생성
CREATE INDEX idx_reddit_posts_subreddit ON reddit_posts(subreddit, created_utc DESC);
CREATE INDEX idx_reddit_posts_crawled_at ON reddit_posts(crawled_at DESC);
CREATE INDEX idx_reddit_posts_score ON reddit_posts(score DESC);
CREATE INDEX idx_reddit_posts_tech_keywords ON reddit_posts USING GIN(tech_keywords);

CREATE INDEX idx_hackernews_items_time ON hackernews_items(time DESC);
CREATE INDEX idx_hackernews_items_score ON hackernews_items(score DESC);
CREATE INDEX idx_hackernews_items_crawled_at ON hackernews_items(crawled_at DESC);

CREATE INDEX idx_job_postings_company ON job_postings(company, posted_date DESC);
CREATE INDEX idx_job_postings_tech_skills ON job_postings USING GIN(tech_skills);
CREATE INDEX idx_job_postings_crawled_at ON job_postings(crawled_at DESC);

CREATE INDEX idx_github_repos_language ON github_repos(language, stars DESC);
CREATE INDEX idx_github_repos_stars ON github_repos(stars DESC);
CREATE INDEX idx_github_repos_crawled_at ON github_repos(crawled_at DESC);

CREATE INDEX idx_stackoverflow_tags ON stackoverflow_items USING GIN(tags);
CREATE INDEX idx_stackoverflow_score ON stackoverflow_items(score DESC);
CREATE INDEX idx_stackoverflow_crawled_at ON stackoverflow_items(crawled_at DESC);

CREATE INDEX idx_company_news_company ON company_news(company, published_date DESC);
CREATE INDEX idx_company_news_type ON company_news(news_type);
CREATE INDEX idx_company_news_crawled_at ON company_news(crawled_at DESC);

-- 트리거 함수: crawled_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_crawled_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.crawled_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 각 테이블에 트리거 적용
CREATE TRIGGER update_reddit_posts_crawled_at
    BEFORE UPDATE ON reddit_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_crawled_at();

CREATE TRIGGER update_hackernews_items_crawled_at
    BEFORE UPDATE ON hackernews_items
    FOR EACH ROW
    EXECUTE FUNCTION update_crawled_at();

CREATE TRIGGER update_job_postings_crawled_at
    BEFORE UPDATE ON job_postings
    FOR EACH ROW
    EXECUTE FUNCTION update_crawled_at();

CREATE TRIGGER update_github_repos_crawled_at
    BEFORE UPDATE ON github_repos
    FOR EACH ROW
    EXECUTE FUNCTION update_crawled_at();

CREATE TRIGGER update_stackoverflow_items_crawled_at
    BEFORE UPDATE ON stackoverflow_items
    FOR EACH ROW
    EXECUTE FUNCTION update_crawled_at();

CREATE TRIGGER update_company_news_crawled_at
    BEFORE UPDATE ON company_news
    FOR EACH ROW
    EXECUTE FUNCTION update_crawled_at();

-- 통계 뷰 생성
CREATE OR REPLACE VIEW v_daily_stats AS
SELECT 
    DATE(crawled_at) as date,
    'reddit' as source,
    COUNT(*) as total_items,
    AVG(score) as avg_score,
    MAX(score) as max_score
FROM reddit_posts
GROUP BY DATE(crawled_at)
UNION ALL
SELECT 
    DATE(crawled_at) as date,
    'hackernews' as source,
    COUNT(*) as total_items,
    AVG(score) as avg_score,
    MAX(score) as max_score
FROM hackernews_items
GROUP BY DATE(crawled_at)
ORDER BY date DESC, source;

COMMENT ON VIEW v_daily_stats IS '일별 크롤링 통계';

-- 완료 메시지
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL 초기화 완료';
    RAISE NOTICE '생성된 테이블: reddit_posts, hackernews_items, job_postings, github_repos, stackoverflow_items, company_news';
END $$;
