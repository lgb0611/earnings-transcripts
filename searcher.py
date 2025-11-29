from googlesearch import search
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import re
from typing import List, Optional, Dict
import time
from config import GOOGLE_SEARCH_QUERY_TEMPLATE

class EarningsCallSearcher:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        ]
    
    def search_earnings_transcript(self, ticker: str, search_query: str) -> List[Dict]:
        """티커로 최근 어닝 컨콜 스크립트 검색"""
        results = []
        
        try:
            print(f"🔍 검색 쿼리: {search_query}")
            for url in search(search_query, num_results=10, lang='en'):
                if self._is_valid_transcript_url(url):
                    content = self._extract_transcript(url)
                    if content and len(content) > 500:
                        results.append({
                            'url': url,
                            'title': self._get_title(url),
                            'content': content,
                            'ticker': ticker
                        })
                        if len(results) >= 3:
                            break
                time.sleep(1)
        except Exception as e:
            print(f"검색 중 오류 발생: {e}")
        
        return results
    
    def _is_valid_transcript_url(self, url: str) -> bool:
        """어닝 컨콜 스크립트 URL인지 검증"""
        valid_domains = [
            'seekingalpha.com', 'fool.com', 'yahoo.com', 
            'investing.com', 'motleyfool.com', 'nasdaq.com',
            'marketbeat.com', 'gurufocus.com'
        ]
        return any(domain in url.lower() for domain in valid_domains)
    
    def _extract_transcript(self, url: str) -> Optional[str]:
        """웹페이지에서 트랜스크립트 추출"""
        try:
            headers = {'User-Agent': self.user_agents[0]}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 다양한 선택자로 트랜스크립트 추출
            selectors = [
                '.transcript', '.call-transcript', '[class*="transcript"]',
                '.call-text', '[class*="call"]', '.post-body',
                'article', '.content', 'main', '.entry-content'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    text = ' '.join([el.get_text() for el in elements])
                    cleaned_text = self._clean_text(text)
                    if len(cleaned_text) > 1000:
                        return cleaned_text
            
            # 전체 텍스트에서 추출
            text = soup.get_text()
            return self._clean_text(text)
            
        except Exception as e:
            print(f"페이지 추출 오류 ({url}): {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정제"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\'\"\n]', '', text)
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        return '. '.join(sentences[:100])
    
    def _get_title(self, url: str) -> str:
        """제목 추출"""
        domain = urlparse(url).netloc
        return f"{domain} - Earnings Call Transcript"