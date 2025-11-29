import sys
from searcher import EarningsCallSearcher
from translator import KoreanTranslator
from summarizer import SummaryGenerator
from config import MAX_SUMMARY_LENGTH
from datetime import datetime

def main():
    if len(sys.argv) != 2:
        print("사용법: python main.py <회사명>")
        print("예: python main.py Tesla")
        sys.exit(1)
    
    company_name = sys.argv[1].strip()
    print(f"🔍 '{company_name}' 최근 어닝 컨콜 분석 중...")
    
    # 1. 검색
    searcher = EarningsCallSearcher()
    print("📡 Google 검색 중...")
    transcripts = searcher.search_earnings_transcript(company_name)
    
    if not transcripts:
        print("❌ 해당 회사의 최근 어닝 컨콜을 찾을 수 없습니다.")
        return
    
    print(f"✅ {len(transcripts)}개의 트랜스크립트 발견")
    
    # 2. 가장 긴 트랜스크립트 선택
    best_transcript = max(transcripts, key=lambda x: len(x['content']))
    
    # 3. 번역
    print("🌐 한국어로 번역 중...")
    translator = KoreanTranslator()
    korean_text = translator.translate_to_korean(best_transcript['content'])
    
    # 4. 요약
    print("✂️ 요약 생성 중...")
    summarizer = SummaryGenerator()
    summary = summarizer.summarize_korean(korean_text, MAX_SUMMARY_LENGTH)
    
    # 결과 출력
    print("\n" + "="*60)
    print(f"🏢 회사: {company_name}")
    print(f"📄 출처: {best_transcript['url']}")
    print(f"📊 요약 길이: {len(summary)}자")
    print("="*60)
    print(summary)
    print("="*60)
    
    # 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{company_name}_{timestamp}_summary.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"회사: {company_name}\n")
        f.write(f"출처: {best_transcript['url']}\n")
        f.write(f"생성시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-" * 40 + "\n\n")
        f.write(summary)
    
    print(f"💾 결과가 '{filename}' 파일로 저장되었습니다.")

if __name__ == "__main__":
    main()