const uploadForm = document.getElementById("uploadForm");
const uploadStatus = document.getElementById("uploadStatus");
const askBtn = document.getElementById("askBtn");
const answer = document.getElementById("answer");
const sources = document.getElementById("sources");

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = document.getElementById("file").files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  uploadStatus.textContent = "Indexing PDF...";

  const res = await fetch("/upload", { method: "POST", body: formData });
  const data = await res.json();
  uploadStatus.textContent = data.message || data.error;
});

askBtn.addEventListener("click", async () => {
  const question = document.getElementById("question").value.trim();
  if (!question) return;

  answer.textContent = "Searching...";
  sources.innerHTML = "";

  const res = await fetch("/ask", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question})
  });
  const data = await res.json();

  if (data.error) {
    answer.textContent = data.error;
    return;
  }

  answer.textContent = data.answer;
  sources.innerHTML = "<h3>Sources</h3>" +
    data.sources.map(s => `<div>Page ${s.page} — similarity ${s.score}</div>`).join("");
});
