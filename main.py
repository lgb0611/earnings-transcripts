import os
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from googlesearch import search
from datetime import datetime
import pytz
import argparse

# --- 설정값 ---
# GitHub Actions에서 입력받은 티커
parser = argparse.ArgumentParser()
parser.add_argument("--ticker", type=str, required=True)
args = parser.parse_args()
TARGET_TICKER = args.ticker

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def search_and_scrape(ticker):
    """구글에서 Transcript 검색 후 텍스트 추출"""
    query = f"{ticker} earnings call transcript 2024 site:seekingalpha.com OR site:motleyfool.com"
    print(f"Searching Google for: {query}")
    
    scraped_text = ""
    source_url = ""

    try:
        # 구글 검색 결과 상위 5개 중 접속 가능한 곳 탐색
        for url in search(query, num_results=5):
            print(f"Trying URL: {url}")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # p 태그 위주로 텍스트 추출 (대부분의 기사 본문 구조)
                    paragraphs = soup.find_all('p')
                    text_content = " ".join([p.get_text() for p in paragraphs])
                    
                    # 본문이 충분히 길면(3000자 이상) 유효한 Transcript로 판단
                    if len(text_content) > 3000:
                        scraped_text = text_content
                        source_url = url
                        break
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                continue
                
    except Exception as e:
        print(f"Search failed: {e}")

    return scraped_text, source_url

def summarize_text(ticker, text, url):
    """LLM을 사용하여 번역 및 요약"""
    if not text:
        return None

    prompt = f"""
    아래 텍스트는 {ticker}의 주식 어닝콜(실적발표) 관련 웹페이지 내용입니다.
    내용을 분석하여 한국어 투자자를 위해 3000자 이내로 요약 보고서를 작성해주세요.
    
    [필수 포함 항목]
    1. 요약 (핵심 3줄)
    2. 실적 하이라이트 (수치 위주)
    3. 경영진 주요 발언 및 Q&A
    4. 원문 출처: {url}
    
    [Text]:
    {text[:25000]}
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None

def save_markdown(ticker, summary):
    kst = pytz.timezone('Asia/Seoul')
    today = datetime.now(kst).strftime("%Y-%m-%d")
    
    os.makedirs("_posts", exist_ok=True)
    filename = f"_posts/{today}-{ticker}-manual-search.md"
    
    content = f"""---
layout: post
title: "{ticker} 어닝콜 AI 요약 (구글검색)"
date: {today} 09:00:00 +0900
categories: earnings
---

{summary}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    print(f"--- Start Processing {TARGET_TICKER} ---")
    text, url = search_and_scrape(TARGET_TICKER)
    
    if text:
        print("Transcript found. Summarizing...")
        summary = summarize_text(TARGET_TICKER, text, url)
        if summary:
            save_markdown(TARGET_TICKER, summary)
            print("Done.")
    else:
        print("Failed to find valid transcript.")
        # 실패 시 빈 파일이라도 만들거나 에러 로그 남김