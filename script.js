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
    handleSearch(); // 초기 로드
  });

// 검색 기능
function handleSearch() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = allData.filter(company =>
    company.name.toLowerCase().includes(query) ||
    company.name_en.toLowerCase().includes(query) ||
    company.ticker.toLowerCase().includes(query)
  );
  renderResults(filtered);
}

// 결과 렌더링 (상세 내용 표시)
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
            <div class="summary"><strong>영어 상세 요약:</strong><br>${t.summary_en}</div>
            <div class="translated"><strong>한국어 번역 상세 요약:</strong><br>${t.summary_kr}</div>
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
  const isOpen = transcripts[0]?.classList.contains("visible");

  transcripts.forEach(t => t.classList.toggle("visible"));
  toggle.textContent = isOpen ? "▼" : "▲";
}

// 새 기업 추가 기능
addCompanyBtn.addEventListener("click", () => {
  addForm.classList.toggle("hidden");
});

cancelAdd.addEventListener("click", () => {
  addForm.classList.add("hidden");
  addForm.reset(); // 폼 초기화
});

submitAdd.addEventListener("click", () => {
  const newCompany = {
    name: document.getElementById("newName").value,
    name_en: document.getElementById("newNameEn").value,
    ticker: document.getElementById("newTicker").value,
    transcripts: []
  };

  // 분기 1 추가 (필수)
  const q1 = document.getElementById("newQuarter1").value;
  if (q1) {
    newCompany.transcripts.push({
      quarter: q1,
      date: document.getElementById("newDate1").value,
      summary_en: document.getElementById("newSummaryEn1").value,
      summary_kr: document.getElementById("newSummaryKr1").value
    });
  }

  // 분기 2 추가 (선택)
  const q2 = document.getElementById("newQuarter2").value;
  if (q2) {
    newCompany.transcripts.push({
      quarter: q2,
      date: document.getElementById("newDate2").value,
      summary_en: document.getElementById("newSummaryEn2").value,
      summary_kr: document.getElementById("newSummaryKr2").value
    });
  }

  if (newCompany.transcripts.length > 0) {
    allData.push(newCompany);
    renderResults(allData); // 즉시 재렌더링
    addForm.classList.add("hidden");
    addForm.reset();
    alert("기업이 추가되었습니다! 검색창에 입력해 확인하세요.");
  } else {
    alert("최소 하나의 분기 내용을 입력하세요.");
  }
});