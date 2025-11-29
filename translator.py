from googletrans import Translator
from typing import Optional

class KoreanTranslator:
    def __init__(self):
        self.translator = Translator()
    
    def translate_to_korean(self, text: str) -> Optional[str]:
        """영어 텍스트를 한국어로 번역"""
        try:
            if len(text) > 5000:  # 너무 긴 텍스트는 분할
                chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
                translated_chunks = []
                for chunk in chunks:
                    result = self.translator.translate(chunk, dest='ko')
                    translated_chunks.append(result.text)
                    # API 제한 회피
                return ' '.join(translated_chunks)
            else:
                result = self.translator.translate(text, dest='ko')
                return result.text
        except Exception as e:
            print(f"번역 오류: {e}")
            return text  # 번역 실패시 원문 반환