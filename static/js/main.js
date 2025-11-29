let currentTaskId = null;
let statusInterval = null;

document.getElementById('analyzeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const ticker = document.getElementById('ticker').value.trim().toUpperCase();
    if (!ticker) return;
    
    // UI 초기화
    hideAll();
    showLoading();
    
    // 분석 요청
    fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `ticker=${ticker}`
    })
    .then(response => response.json())
    .then(data => {
        currentTaskId = data.task_id;
        startStatusPolling();
    })
    .catch(error => {
        showError('연결 오류가 발생했습니다.');
    });
});

function startStatusPolling() {
    statusInterval = setInterval(() => {
        if (!currentTaskId) return;
        
        fetch(`/status/${currentTaskId}`)
        .then(response => response.json())
        .then(data => {
            updateProgress(data.progress, data.status);
            
            if (data.status === 'error') {
                showError(data.error || '분석 중 오류가 발생했습니다.');
                clearInterval(statusInterval);
            } else if (data.result) {
                clearInterval(statusInterval);
                window.location.href = `/result/${currentTaskId}`;
            }
        })
        .catch(error => {
            console.error('Status check failed:', error);
        });
    }, 2000);
}

function updateProgress(progress, status) {
    document.getElementById('progressFill').style.width = progress + '%';
    document.getElementById('statusText').textContent = status;
}

function setTicker(ticker) {
    document.getElementById('ticker').value = ticker;
    document.getElementById('analyzeForm').dispatchEvent(new Event('submit'));
}

function hideAll() {
    document.getElementById('loading').classList.add('hidden');
    document.querySelector('.error').classList.add('hidden');
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function showError(message) {
    const errorDiv = document.querySelector('.error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    document.getElementById('loading').classList.add('hidden');
}

// Enter 키로 제출
document.getElementById('ticker').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        document.getElementById('analyzeForm').dispatchEvent(new Event('submit'));
    }
});
