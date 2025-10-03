"""
유틸리티 함수들
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import re
import requests
from urllib.parse import urlparse, urljoin
import time

def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """로깅 설정"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )

def load_config(config_file: str = 'config.env') -> Dict[str, str]:
    """설정 파일 로드"""
    config = {}
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

def save_json(data: Any, filepath: str):
    """JSON 파일 저장"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath: str) -> Any:
    """JSON 파일 로드"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def generate_unique_id(text: str) -> str:
    """텍스트에서 고유 ID 생성"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def clean_text(text: str) -> str:
    """텍스트 정리"""
    if not text:
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # URL 제거
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # 특수 문자 정리
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_keywords(text: str, keyword_list: List[str]) -> List[str]:
    """텍스트에서 키워드 추출"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in keyword_list:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords

def is_valid_url(url: str) -> bool:
    """URL 유효성 검사"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_domain(url: str) -> str:
    """URL에서 도메인 추출"""
    try:
        return urlparse(url).netloc
    except:
        return ""

def rate_limit_wait(requests_made: int, max_requests: int = 100, time_window: int = 3600):
    """API 요청 제한 대기"""
    if requests_made >= max_requests:
        print(f"API 요청 제한에 도달했습니다. {time_window}초 대기...")
        time.sleep(time_window)
        return True
    return False

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """실패 시 재시도 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"시도 {attempt + 1} 실패: {e}. {delay}초 후 재시도...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def format_timestamp(timestamp: Any) -> str:
    """타임스탬프 포맷팅"""
    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp).isoformat()
    elif isinstance(timestamp, str):
        try:
            return datetime.fromisoformat(timestamp.replace('Z', '+00:00')).isoformat()
        except:
            return timestamp
    else:
        return str(timestamp)

def calculate_time_ago(timestamp: Any) -> str:
    """시간 경과 계산"""
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except:
            return "알 수 없음"
    else:
        return "알 수 없음"
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}일 전"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}시간 전"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}분 전"
    else:
        return "방금 전"

def truncate_text(text: str, max_length: int = 100) -> str:
    """텍스트 자르기"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def safe_get(data: Dict, key: str, default: Any = None) -> Any:
    """안전한 딕셔너리 값 가져오기"""
    try:
        return data.get(key, default)
    except:
        return default

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """리스트를 청크로 나누기"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def merge_dicts(*dicts: Dict) -> Dict:
    """딕셔너리 병합"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def filter_dict(data: Dict, keys: List[str]) -> Dict:
    """딕셔너리 필터링"""
    return {k: v for k, v in data.items() if k in keys}

def validate_email(email: str) -> bool:
    """이메일 유효성 검사"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """전화번호 유효성 검사"""
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def sanitize_filename(filename: str) -> str:
    """파일명 정리"""
    # 특수 문자 제거
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 연속된 공백을 언더스코어로 변경
    filename = re.sub(r'\s+', '_', filename)
    # 길이 제한
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def get_file_size(filepath: str) -> int:
    """파일 크기 가져오기"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0

def format_file_size(size_bytes: int) -> str:
    """파일 크기 포맷팅"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def create_directory_structure(base_path: str, structure: Dict):
    """디렉토리 구조 생성"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_directory_structure(path, content)
        else:
            os.makedirs(path, exist_ok=True)

def get_environment_info() -> Dict:
    """환경 정보 가져오기"""
    import platform
    import sys
    
    return {
        'platform': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'hostname': platform.node(),
        'current_directory': os.getcwd(),
        'timestamp': datetime.now().isoformat()
    }

def check_dependencies() -> Dict:
    """의존성 체크"""
    required_packages = [
        'scrapy', 'pandas', 'numpy', 'requests', 'beautifulsoup4',
        'pymongo', 'psycopg2-binary', 'vaderSentiment', 'textblob',
        'plotly', 'streamlit', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    installed_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            installed_packages.append(package)
        except ImportError:
            missing_packages.append(package)
    
    return {
        'installed': installed_packages,
        'missing': missing_packages,
        'all_installed': len(missing_packages) == 0
    }

def main():
    """테스트 함수"""
    print("🔧 유틸리티 함수 테스트")
    print("=" * 50)
    
    # 로깅 설정 테스트
    setup_logging('INFO')
    logger = logging.getLogger(__name__)
    logger.info("로깅 테스트")
    
    # 텍스트 정리 테스트
    dirty_text = "<p>This is a <b>dirty</b> text with http://example.com URL</p>"
    clean = clean_text(dirty_text)
    print(f"텍스트 정리: {clean}")
    
    # 키워드 추출 테스트
    keywords = ['AI', 'machine learning', 'blockchain']
    found = extract_keywords("This is about AI and machine learning", keywords)
    print(f"키워드 추출: {found}")
    
    # URL 유효성 테스트
    test_urls = ["https://example.com", "invalid-url", "http://test.com/path"]
    for url in test_urls:
        print(f"URL 유효성 ({url}): {is_valid_url(url)}")
    
    # 타임스탬프 포맷팅 테스트
    now = datetime.now()
    formatted = format_timestamp(now.timestamp())
    print(f"타임스탬프 포맷팅: {formatted}")
    
    # 시간 경과 계산 테스트
    time_ago = calculate_time_ago(now.timestamp() - 3600)  # 1시간 전
    print(f"시간 경과: {time_ago}")
    
    # 환경 정보
    env_info = get_environment_info()
    print(f"환경 정보: {env_info['platform']}")
    
    # 의존성 체크
    deps = check_dependencies()
    print(f"의존성 상태: {len(deps['installed'])}/{len(deps['installed']) + len(deps['missing'])} 설치됨")
    if deps['missing']:
        print(f"누락된 패키지: {deps['missing']}")


if __name__ == '__main__':
    main()

