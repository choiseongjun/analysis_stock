// MongoDB 초기화 스크립트
db = db.getSiblingDB('stock_tech_trends');

// 컬렉션 생성
db.createCollection('reddit_posts');
db.createCollection('hackernews_items');
db.createCollection('job_postings');
db.createCollection('github_repos');
db.createCollection('stackoverflow_items');
db.createCollection('company_news');

// 인덱스 생성
db.reddit_posts.createIndex({ 'post_id': 1 }, { unique: true });
db.reddit_posts.createIndex({ 'subreddit': 1, 'created_utc': -1 });
db.reddit_posts.createIndex({ 'crawled_at': -1 });
db.reddit_posts.createIndex({ 'sentiment_score.vader_compound': 1 });
db.reddit_posts.createIndex({ 'tech_keywords': 1 });

db.hackernews_items.createIndex({ 'item_id': 1 }, { unique: true });
db.hackernews_items.createIndex({ 'time': -1 });
db.hackernews_items.createIndex({ 'score': -1 });
db.hackernews_items.createIndex({ 'crawled_at': -1 });

db.github_repos.createIndex({ 'repo_id': 1 }, { unique: true });
db.github_repos.createIndex({ 'language': 1, 'stars': -1 });
db.github_repos.createIndex({ 'created_at': -1 });
db.github_repos.createIndex({ 'crawled_at': -1 });

db.job_postings.createIndex({ 'job_id': 1 }, { unique: true });
db.job_postings.createIndex({ 'company': 1, 'posted_date': -1 });
db.job_postings.createIndex({ 'tech_skills': 1 });
db.job_postings.createIndex({ 'crawled_at': -1 });

db.stackoverflow_items.createIndex({ 'question_id': 1 }, { unique: true });
db.stackoverflow_items.createIndex({ 'tags': 1, 'score': -1 });
db.stackoverflow_items.createIndex({ 'created_date': -1 });
db.stackoverflow_items.createIndex({ 'crawled_at': -1 });

db.company_news.createIndex({ 'news_id': 1 }, { unique: true });
db.company_news.createIndex({ 'company': 1, 'published_date': -1 });
db.company_news.createIndex({ 'news_type': 1 });
db.company_news.createIndex({ 'crawled_at': -1 });

print('MongoDB 초기화 완료');
print('생성된 컬렉션:', db.getCollectionNames());

