from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading
import time
from datetime import datetime
from searcher import EarningsCallSearcher
from translator import KoreanTranslator
from summarizer import SummaryGenerator
from ticker_validator import TickerValidator
from config import MAX_SUMMARY_LENGTH

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'results'

# 결과 저장 딕셔너리
results = {}
tasks = {}

class BackgroundTask:
    def __init__(self, ticker):
        self.ticker = ticker
        self.status = "processing"
        self.progress = 0
        self.result = None
        self.error = None
    
    def run(self):
        try:
            self.progress = 10
            self.status = "티커 검증 중..."
            
            # 1. 티커 검증
            validator = TickerValidator()
            is_valid, company_name = validator.validate_ticker(self.ticker)
            
            if not is_valid:
                self.error = f"유효하지 않은 티커: {self.ticker}"
                self.status = "error"
                return
            
            self.progress = 25
            self.status = f"{company_name} 검색 중..."
            search_query = validator.get_search_query(self.ticker)
            
            # 2. 검색
            searcher = EarningsCallSearcher()
            transcripts = searcher.search_earnings_transcript(self.ticker, search_query)
            
            if not transcripts:
                self.error = f"{self.ticker}의 어닝 컨콜을 찾을 수 없습니다."
                self.status = "error"
                return
            
            self.progress = 50
            self.status = "최적 트랜스크립트 선택 중..."
            
            # 3. 가장 긴 트랜스크립트 선택
            best_transcript = max(transcripts, key=lambda x: len(x['content']))
            
            self.progress = 60
            self.status = "한국어 번역 중..."
            
            # 4. 번역
            translator = KoreanTranslator()
            korean_text = translator.translate_to_korean(best_transcript['content'])
            
            self.progress = 80
            self.status = "AI 요약 생성 중..."
            
            # 5. 요약
            summarizer = SummaryGenerator()
            summary = summarizer.summarize_korean(korean_text, MAX_SUMMARY_LENGTH)
            
            # 결과 저장
            self.result = {
                'ticker': self.ticker,
                'company_name': company_name,
                'url': best_transcript['url'],
                'summary': summary,
                'length': len(summary),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'transcripts_count': len(transcripts)
            }
            
            self.progress = 100
            self.status = "완료!"
            
        except Exception as e:
            self.error = f"오류 발생: {str(e)}"
            self.status = "error"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    ticker = request.form['ticker'].strip().upper()
    task_id = f"{ticker}_{int(time.time())}"
    
    # 태스크 생성
    task = BackgroundTask(ticker)
    tasks[task_id] = task
    
    # 백그라운드 실행
    thread = threading.Thread(target=task.run)
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id, 'ticker': ticker})

@app.route('/status/<task_id>')
def status(task_id):
    if task_id in tasks:
        task = tasks[task_id]
        return jsonify({
            'status': task.status,
            'progress': task.progress,
            'error': task.error,
            'result': task.result
        })
    return jsonify({'status': 'not_found'}), 404

@app.route('/result/<task_id>')
def result(task_id):
    if task_id in tasks and tasks[task_id].result:
        return render_template('result.html', result=tasks[task_id].result)
    return "결과를 찾을 수 없습니다.", 404

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    app.run(debug=False, host='0.0.0.0', port=5000)
