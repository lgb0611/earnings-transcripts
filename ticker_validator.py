"""티커 유효성 검증 및 회사명 자동 조회"""
import requests
from typing import Optional, Tuple

class TickerValidator:
    def __init__(self):
        self.api_url = "https://query1.finance.yahoo.com/v1/finance/search"
    
    def validate_ticker(self, ticker: str) -> Tuple[bool, Optional[str]]:
        """티커 유효성 검증 및 회사명 반환"""
        try:
            params = {
                'q': ticker.upper(),
                'quotesCount': 1,
                'newsCount': 0
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.api_url, params=params, headers=headers, timeout=10)
            data = response.json()
            
            if data.get('quotes') and len(data['quotes']) > 0:
                quote = data['quotes'][0]
                company_name = quote.get('longname', quote.get('shortname', ticker))
                return True, company_name
            
            return False, None
            
        except Exception as e:
            print(f"티커 검증 오류: {e}")
            return False, None
    
    def get_search_query(self, ticker: str) -> str:
        """검색 쿼리 생성"""
        is_valid, company_name = self.validate_ticker(ticker)
        if is_valid and company_name:
            return f"{ticker} {company_name} earnings call transcript latest"
        return f"{ticker} earnings call transcript latest"