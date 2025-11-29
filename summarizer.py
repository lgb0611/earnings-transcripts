from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import Optional

class SummaryGenerator:
    def __init__(self, max_length: int = 3000):
        # 한국어 요약 모델 로드 (mT5)
        model_name = "google/mt5-small"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.summarizer = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        self.max_length = max_length
    
    def summarize_korean(self, text: str, max_length: int = 1024) -> str:
        """한국어 텍스트 요약"""
        try:
            # 긴 텍스트는 청크로 분할
            if len(text) > 4000:
                chunks = [text[i:i+4000] for i in range(0, len(text), 3500)]
                summaries = []
                for chunk in chunks:
                    summary = self.summarizer(
                        chunk,
                        max_length=200,
                        min_length=50,
                        do_sample=False
                    )[0]['summary_text']
                    summaries.append(summary)
                full_summary = ' '.join(summaries)
            else:
                full_summary = self.summarizer(
                    text,
                    max_length=max_length,
                    min_length=100,
                    do_sample=False
                )[0]['summary_text']
            
            # 최종 길이 제한
            if len(full_summary) > self.max_length:
                full_summary = full_summary[:self.max_length]
            
            return full_summary.strip()
            
        except Exception as e:
            print(f"요약 오류: {e}")
            # 오류시 간단한 트렁케이션
            return text[:self.max_length]