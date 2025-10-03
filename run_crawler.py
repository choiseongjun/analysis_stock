#!/usr/bin/env python3
"""
주식 기술 트렌드 크롤링 실행 스크립트
"""

import os
import sys
import subprocess
from datetime import datetime
import argparse

def setup_environment():
    """환경 설정"""
    # config.env 파일을 .env로 복사
    if os.path.exists('config.env') and not os.path.exists('.env'):
        with open('config.env', 'r', encoding='utf-8') as src:
            with open('.env', 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print("✅ 환경 설정 파일 생성 완료")

def run_spider(spider_name, output_format='json'):
    """스파이더 실행"""
    print(f"🚀 {spider_name} 크롤링 시작...")
    
    # 출력 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/{spider_name}_{timestamp}.{output_format}"
    
    # 출력 디렉토리 생성
    os.makedirs('data', exist_ok=True)
    
    # Scrapy 명령어 실행
    cmd = [
        'scrapy', 'crawl', spider_name,
        '-o', output_file,
        '--loglevel=INFO'
    ]
    
    try:
        result = subprocess.run(cmd, cwd='stock_tech_trends', check=True)
        print(f"✅ {spider_name} 크롤링 완료: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {spider_name} 크롤링 실패: {e}")
        return False

def run_all_spiders():
    """모든 스파이더 실행"""
    spiders = ['reddit_spider', 'hackernews_spider', 'github_spider']
    
    print("🎯 모든 스파이더 실행 시작...")
    
    results = []
    for spider in spiders:
        success = run_spider(spider)
        results.append((spider, success))
    
    # 결과 요약
    print("\n📊 크롤링 결과 요약:")
    for spider, success in results:
        status = "✅ 성공" if success else "❌ 실패"
        print(f"  {spider}: {status}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\n총 {len(results)}개 중 {successful}개 성공")

def main():
    parser = argparse.ArgumentParser(description='주식 기술 트렌드 크롤링 실행기')
    parser.add_argument('spider', nargs='?', help='실행할 스파이더 이름 (기본값: all)')
    parser.add_argument('--format', '-f', default='json', choices=['json', 'csv', 'xml'], 
                       help='출력 형식 (기본값: json)')
    
    args = parser.parse_args()
    
    # 환경 설정
    setup_environment()
    
    if args.spider:
        # 특정 스파이더 실행
        run_spider(args.spider, args.format)
    else:
        # 모든 스파이더 실행
        run_all_spiders()

if __name__ == '__main__':
    main()
