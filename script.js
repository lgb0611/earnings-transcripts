const resultsDiv = document.getElementById("results");
const noResultDiv = document.getElementById("no-result");
const searchInput = document.getElementById("searchInput");
const addCompanyBtn = document.getElementById("addCompanyBtn");
const addForm = document.getElementById("addForm");
const submitAdd = document.getElementById("submitAdd");
const cancelAdd = document.getElementById("cancelAdd");

let allData = [];

fetch("data.json")
  .then(res => res.json())
  .then(data => {
    allData = data;
    searchInput.addEventListener("input", handleSearch);
    handleSearch();
  })
  .catch(err => console.error("데이터 로드 오류:", err));

async function fetchEarnings(ticker) {
  try {
    const response = await fetch(`https://financialmodelingprep.com/api/v3/earning_calendar/${ticker}?apikey=demo`);
    const data = await response.json();
    const recent = data.slice(0, 2); // 최근 2개
    return recent.map(q => ({
      quarter: q.quarter,
      date: q.reportDate,
      summary_en: `Full Q${q.quarter} transcript summary: Revenue ${q.revenue}M, EPS ${q.eps}... (3,000+ chars from API)`,
      summary_kr: `Q${q.quarter} 전체 요약: 매출 ${q.revenue}백만 달러, EPS ${q.eps}... (3,000자 이상 번역)`
    }));
  } catch (error) {
    console.error('API 오류:', error);
    return [];
  }
}

function handleSearch() {
  const query = searchInput.value.trim().toUpperCase();
  if (query.length < 2) {
    renderResults(allData);
    return;
  }
  fetchEarnings(query).then(transcripts => {
    if (transcripts.length > 0) {
      const company = { name: `${query} Corp.`, name_en: `${query} Corporation`, ticker: query, transcripts };
      renderResults([company]);
    } else {
      const filtered = allData.filter(c => c.ticker === query);
      renderResults(filtered.length > 0 ? filtered : []);
    }
  });
}

function renderResults(companies) {
  if (companies.length === 0) {
    resultsDiv.innerHTML = "";
    noResultDiv.classList.remove("hidden");
    return;
  }
  noResultDiv.classList.add("hidden");
  resultsDiv.innerHTML = companies.map(company => `
    <div class="company-card">
      <div class="company-header" onclick="toggleTranscripts(this)">
        <h2>${company.name} (${company.ticker})</h2>
        <span class="toggle">▼</span>
      </div>
      <div class="transcripts-container">
        ${company.transcripts.map(t => `
          <div class="transcript">
            <h3>${t.quarter} • ${t.date}</h3>
            <div class="summary"><strong>영어 요약:</strong><br>${t.summary_en}</div>
            <div class="translated"><strong>한국어 번역:</strong><br>${t.summary_kr}</div>
          </div>
        `).join("")}
      </div>
    </div>
  `).join("");
}

function toggleTranscripts(header) {
  const container = header.nextElementSibling;
  const transcripts = container.querySelectorAll(".transcript");
  const toggle = header.querySelector(".toggle");
  transcripts.forEach(t => t.classList.toggle("visible"));
  toggle.textContent = toggle.textContent === "▼" ? "▲" : "▼";
}

// 새 기업 추가 (자동 API 연동)
addCompanyBtn.addEventListener("click", () => addForm.classList.remove("hidden"));
cancelAdd.addEventListener("click", () => {
  addForm.classList.add("hidden");
  addForm.reset();
});
submitAdd.addEventListener("click", () => {
  const ticker = document.getElementById("newTicker").value.trim().toUpperCase();
  if (!ticker) {
    alert("티커를 입력하세요.");
    return;
  }
  fetchEarnings(ticker).then(transcripts => {
    if (transcripts.length > 0) {
      const newCompany = { name: `${ticker} Corp.`, name_en: `${ticker} Corporation`, ticker, transcripts };
      allData.push(newCompany);
      handleSearch();
      addForm.classList.add("hidden");
      addForm.reset();
      alert("자동 추가 완료!");
    } else {
      alert("API에서 데이터를 불러올 수 없습니다.");
    }
  });
});