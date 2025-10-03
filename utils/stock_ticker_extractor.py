"""
주식 티커 심볼 추출 유틸리티
Reddit 포스트에서 주식 티커 심볼을 감지하고 추출합니다.
"""

import re
from typing import List, Set, Dict

class StockTickerExtractor:
    """주식 티커 심볼을 추출하는 클래스"""
    
    # 추출 모드
    MODE_STRICT = 'strict'      # 알려진 티커만 추출
    MODE_AGGRESSIVE = 'aggressive'  # 문맥 기반으로 모든 티커 추출
    
    # 주요 기술/트렌드 관련 주식 티커 목록 (카테고리 분류용 + strict 모드용)
    KNOWN_TICKERS = {
        # 빅테크
        'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA',
        # 반도체
        'AMD', 'INTC', 'TSM', 'QCOM', 'MU', 'AVGO', 'ASML', 'ARM',
        # 클라우드/소프트웨어
        'CRM', 'ORCL', 'IBM', 'SAP', 'ADBE', 'NOW', 'SNOW', 'NET', 'DDOG',
        # AI/데이터
        'PLTR', 'AI', 'BBAI', 'SOUN', 'PATH',
        # 전기차/자율주행
        'RIVN', 'LCID', 'NIO', 'XPEV', 'LI',
        # 핀테크/결제
        'SQ', 'PYPL', 'COIN', 'HOOD', 'SOFI',
        # 게임/엔터테인먼트
        'RBLX', 'U', 'EA', 'TTWO', 'ATVI',
        # 사이버보안
        'CRWD', 'ZS', 'PANW', 'FTNT', 'S',
        # 클라우드 인프라
        'SHOP', 'TEAM', 'ESTC', 'MDB', 'DOCN',
        # 기타 기술 기업
        'UBER', 'LYFT', 'DASH', 'ABNB', 'SPOT', 'PINS', 'SNAP', 'TWLO',
        'ZM', 'OKTA', 'ROKU', 'SQ', 'MELI', 'SE',
        # ETF
        'QQQ', 'SPY', 'VOO', 'VTI', 'ARKK', 'ARKQ', 'ARKW', 'ARKG',
        # 중국 기술주
        'BABA', 'BIDU', 'JD', 'PDD', 'TCEHY',
        # 반도체 장비
        'AMAT', 'LRCX', 'KLAC',
        # 기타
        'DELL', 'HPQ', 'WDC', 'STX', 'NFLX', 'DIS',
    }
    
    # 제외할 일반 단어 (false positive 방지)
    EXCLUDED_WORDS = {
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 
        'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM',
        'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY',
        'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO',
        'USE', 'IT', 'IS', 'AS', 'AT', 'BE', 'WE', 'HE', 'SO', 'ON',
        'BY', 'TO', 'OF', 'IN', 'AN', 'OR', 'IF', 'DO', 'MY', 'UP',
        'GO', 'NO', 'US', 'AM', 'PM', 'AI', 'AR', 'VR', 'ML', 'IT',
        'ID', 'CEO', 'CTO', 'CFO', 'USA', 'UK', 'EU', 'API', 'CPU', 'GPU',
    }
    
    def __init__(self, mode='aggressive'):
        """
        Args:
            mode: 'strict' (알려진 티커만) 또는 'aggressive' (문맥 기반 모든 티커)
        """
        self.mode = mode
        self.ticker_pattern = re.compile(r'\$([A-Z]{1,5})\b')  # $AAPL 형식
        self.word_pattern = re.compile(r'\b([A-Z]{2,5})\b')    # AAPL 형식 (대문자만)
    
    def extract_tickers(self, text: str) -> List[str]:
        """
        텍스트에서 주식 티커 심볼을 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            추출된 티커 심볼 리스트
        """
        if not text:
            return []
        
        tickers = set()
        
        if self.mode == self.MODE_AGGRESSIVE:
            # AGGRESSIVE 모드: 문맥만 확인하면 모든 티커 추출
            
            # $ 기호가 있는 티커는 무조건 추출 (가장 확실한 신호)
            dollar_tickers = self.ticker_pattern.findall(text)
            for ticker in dollar_tickers:
                if ticker not in self.EXCLUDED_WORDS:
                    tickers.add(ticker)
            
            # 대문자로만 이루어진 단어 중 주식 문맥에 있는 것 추출
            words = self.word_pattern.findall(text)
            for word in words:
                if word not in self.EXCLUDED_WORDS:
                    # 문맥 확인: 주식 관련 단어 근처에 있는지 확인
                    if self._is_stock_context(text, word):
                        tickers.add(word)
        
        else:  # STRICT 모드
            # STRICT 모드: 알려진 티커만 추출 (기존 방식)
            
            # $ 기호가 있는 티커 추출
            dollar_tickers = self.ticker_pattern.findall(text)
            for ticker in dollar_tickers:
                if ticker in self.KNOWN_TICKERS and ticker not in self.EXCLUDED_WORDS:
                    tickers.add(ticker)
            
            # 대문자로만 이루어진 단어 중 알려진 티커 추출
            words = self.word_pattern.findall(text)
            for word in words:
                if word in self.KNOWN_TICKERS and word not in self.EXCLUDED_WORDS:
                    # 문맥 확인
                    if self._is_stock_context(text, word):
                        tickers.add(word)
        
        return sorted(list(tickers))
    
    def _is_stock_context(self, text: str, ticker: str) -> bool:
        """
        티커가 주식 관련 문맥에서 언급되는지 확인
        
        Args:
            text: 전체 텍스트
            ticker: 확인할 티커
            
        Returns:
            주식 문맥 여부
        """
        # 티커 위치 찾기
        ticker_pos = text.find(ticker)
        if ticker_pos == -1:
            return False
        
        # 앞뒤 100자 추출
        start = max(0, ticker_pos - 100)
        end = min(len(text), ticker_pos + len(ticker) + 100)
        context = text[start:end].lower()
        
        # 주식 관련 키워드
        stock_keywords = [
            'stock', 'share', 'buy', 'sell', 'price', 'trade', 'invest',
            'bull', 'bear', 'call', 'put', 'option', 'equity', 'market',
            'portfolio', 'holding', 'position', 'long', 'short', 'dip',
            'moon', 'rocket', 'yolo', 'gain', 'loss', 'profit', 'revenue',
            'earnings', 'valuation', 'ipo', 'dividend', 'ticker'
        ]
        
        # 주식 관련 키워드가 있으면 True
        for keyword in stock_keywords:
            if keyword in context:
                return True
        
        # $ 기호가 티커 앞에 있으면 True
        if ticker_pos > 0 and text[ticker_pos - 1] == '$':
            return True
        
        return False
    
    def extract_with_context(self, text: str) -> List[Dict[str, any]]:
        """
        티커와 함께 문맥 정보도 추출
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            티커와 문맥 정보가 담긴 딕셔너리 리스트
        """
        tickers = self.extract_tickers(text)
        results = []
        
        for ticker in tickers:
            # 티커가 언급된 문장 추출
            sentences = re.split(r'[.!?]+', text)
            mentions = []
            
            for sentence in sentences:
                if ticker in sentence or f'${ticker}' in sentence:
                    mentions.append(sentence.strip())
            
            results.append({
                'ticker': ticker,
                'mention_count': len(mentions),
                'contexts': mentions[:3]  # 최대 3개 문장만
            })
        
        return results
    
    def get_ticker_category(self, ticker: str) -> str:
        """
        티커의 카테고리 반환
        
        Args:
            ticker: 티커 심볼
            
        Returns:
            카테고리 문자열
        """
        categories = {
            'Big Tech': ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META'],
            'Semiconductors': ['NVDA', 'AMD', 'INTC', 'TSM', 'QCOM', 'MU', 'AVGO', 'ASML', 'ARM', 'AMAT', 'LRCX', 'KLAC'],
            'AI/Data': ['PLTR', 'AI', 'BBAI', 'SOUN', 'PATH'],
            'Electric Vehicles': ['TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI'],
            'Cloud/Software': ['CRM', 'ORCL', 'IBM', 'SAP', 'ADBE', 'NOW', 'SNOW', 'NET', 'DDOG', 'MDB', 'ESTC'],
            'Fintech': ['SQ', 'PYPL', 'COIN', 'HOOD', 'SOFI'],
            'Cybersecurity': ['CRWD', 'ZS', 'PANW', 'FTNT', 'S'],
            'ETF': ['QQQ', 'SPY', 'VOO', 'VTI', 'ARKK', 'ARKQ', 'ARKW', 'ARKG'],
            'Gaming/Entertainment': ['RBLX', 'U', 'EA', 'TTWO', 'ATVI'],
            'E-commerce/Marketplace': ['SHOP', 'MELI', 'SE'],
        }
        
        for category, tickers in categories.items():
            if ticker in tickers:
                return category
        
        return 'Unknown/Startup'


# 싱글톤 인스턴스 (기본값: aggressive 모드)
_extractor = StockTickerExtractor(mode='aggressive')
_extractor_strict = StockTickerExtractor(mode='strict')

def extract_stock_tickers(text: str, mode='aggressive') -> List[str]:
    """
    편의 함수: 텍스트에서 주식 티커 추출
    
    Args:
        text: 분석할 텍스트
        mode: 'aggressive' (모든 티커) 또는 'strict' (알려진 티커만)
    """
    if mode == 'strict':
        return _extractor_strict.extract_tickers(text)
    return _extractor.extract_tickers(text)

def extract_tickers_with_context(text: str, mode='aggressive') -> List[Dict[str, any]]:
    """
    편의 함수: 티커와 문맥 정보 추출
    
    Args:
        text: 분석할 텍스트
        mode: 'aggressive' (모든 티커) 또는 'strict' (알려진 티커만)
    """
    if mode == 'strict':
        return _extractor_strict.extract_with_context(text)
    return _extractor.extract_with_context(text)

