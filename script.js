const resultsDiv = document.getElementById("results");
const noResultDiv = document.getElementById("no-result");
const searchInput = document.getElementById("searchInput");
const addCompanyBtn = document.getElementById("addCompanyBtn");
const addForm = document.getElementById("addForm");
const submitAdd = document.getElementById("submitAdd");     // ← 여기 수정
const cancelAdd = document.getElementById("cancelAdd");     // ← 여기 수정

let allData = [];

// localStorage에 저장된 사용자 추가 기업 불러오기
const savedData = localStorage.getItem("userCompanies");
if (savedData) {
  allData = allData.concat(JSON.parse(savedData));
}

fetch("data.json")
  .then(res => res.json())
  .then(data => {
    allData = data.concat(allData.filter(c => !data.some(d => d.ticker === c.ticker))); // 중복 방지
    searchInput.addEventListener("input", handleSearch);
    handleSearch();
  });

function handleSearch() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = allData.filter(c => 
    c.name.toLowerCase().includes(query) || 
    c.name_en.toLowerCase().includes(query) || 
    c.ticker.toLowerCase().includes(query)
  );
  renderResults(filtered);
}

function renderResults(companies) {
  if (companies.length === 0) {
    resultsDiv.innerHTML = "";
    noResultDiv.classList.remove("hidden");
    return;
  }
  noResultDiv.classList.add("hidden");
  resultsDiv.innerHTML = companies.map(c => `
    <div class="company-card">
      <div class="company-header" onclick="toggleTranscripts(this)">
        <h2>${c.name} (${c.ticker})</h2>
        <span class="toggle">▼</span>
      </div>
      <div class="transcripts-container">
        ${c.transcripts.map(t => `
          <div class="transcript">
            <h3>${t.quarter} • ${t.date}</h3>
            <div class="summary"><strong>영어 컨콜:</strong><br>${t.summary_en}</div>
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

// 새 기업 추가 (완전 정상 작동 + localStorage 저장)
addCompanyBtn.onclick = () => addForm.classList.remove("hidden");

cancelAdd.onclick = () => {
  addForm.classList.add("hidden");
  addForm.reset();
};

submitAdd.onclick = () => {
  const req = ["newName","newNameEn","newTicker","newQuarter1","newDate1","newSummaryEn1","newSummaryKr1"];
  if (req.some(id => !document.getElementById(id).value.trim())) {
    alert("모든 필수 항목을 입력해 주세요!");
    return;
  }

  const newCompany = {
    name: document.getElementById("newName").value.trim(),
    name_en: document.getElementById("newNameEn").value.trim(),
    ticker: document.getElementById("newTicker").value.trim().toUpperCase(),
    transcripts: [{
      quarter: document.getElementById("newQuarter1").value.trim(),
      date: document.getElementById("newDate1").value,
      summary_en: document.getElementById("newSummaryEn1").value.trim(),
      summary_kr: document.getElementById("newSummaryKr1").value.trim()
    }]
  };

  allData.push(newCompany);
  localStorage.setItem("userCompanies", JSON.stringify(allData.filter(c => !["AAPL","TSLA","NVDA","MSFT","005930","META","GOOGL","AMZN","NFLX","ASML","TSM","AVGO","COST","WMT","JPM"].includes(c.ticker))));
  
  handleSearch();
  addForm.classList.add("hidden");
  addForm.reset();
  alert(`${newCompany.name}(${newCompany.ticker})이 성공적으로 추가되었습니다!`);
};