const resultsDiv = document.getElementById("results");
const noResultDiv = document.getElementById("no-result");
const searchInput = document.getElementById("searchInput");

let allData = [];

fetch("data.json")
  .then(res => res.json())
  .then(data => {
    allData = data;
    searchInput.addEventListener("input", handleSearch);
    handleSearch(); // 초기 로드 시 전체 표시
  });

function handleSearch() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = allData.filter(company =>
    company.name.toLowerCase().includes(query) ||
    company.name_en.toLowerCase().includes(query) ||
    company.ticker.toLowerCase().includes(query)
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
            <div class="translated"><strong>한국어 번역 요약:</strong><br>${t.summary_kr}</div>
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