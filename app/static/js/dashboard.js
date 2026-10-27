const $ = (id) => document.getElementById(id);

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const type = response.headers.get("content-type") || "";
  const data = type.includes("application/json") ? await response.json() : null;
  if (!response.ok) throw new Error(data?.error || `Request failed (${response.status})`);
  return data;
}

function setMessage(message, kind = "") {
  const el = $("message");
  el.textContent = message;
  el.style.color = kind === "error" ? "#b42318" : kind === "success" ? "#137447" : "#667085";
}

function scoreClass(score) {
  if (score < 70) return "score-pill low";
  if (score < 90) return "score-pill medium";
  return "score-pill";
}

async function loadDatasets() {
  const tbody = $("dataset-list");
  tbody.replaceChildren();
  try {
    const data = await apiRequest("/api/datasets?per_page=50");
    const datasets = data.items || [];
    $("total-datasets").textContent = data.total ?? datasets.length;
    $("total-rows").textContent = datasets.reduce((sum, d) => sum + Number(d.rows || 0), 0).toLocaleString();
    const average = datasets.length
      ? datasets.reduce((sum, d) => sum + Number(d.quality_score || 0), 0) / datasets.length
      : null;
    $("average-score").textContent = average === null ? "—" : `${average.toFixed(2)}%`;
    $("history-note").textContent = `Showing ${datasets.length} of ${data.total ?? datasets.length} datasets.`;

    if (!datasets.length) {
      const row = tbody.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 6;
      cell.className = "empty";
      cell.textContent = "No datasets yet. Upload a CSV to get started.";
      return;
    }

    for (const dataset of datasets) {
      const row = tbody.insertRow();
      row.insertCell().textContent = dataset.filename ?? "Unnamed dataset";
      row.insertCell().textContent = Number(dataset.rows || 0).toLocaleString();
      row.insertCell().textContent = Number(dataset.columns || 0).toLocaleString();
      const scoreCell = row.insertCell();
      const score = Number(dataset.quality_score || 0);
      const pill = document.createElement("span");
      pill.className = scoreClass(score);
      pill.textContent = `${score.toFixed(2)}%`;
      scoreCell.appendChild(pill);
      row.insertCell().textContent = dataset.uploaded_at
        ? new Date(dataset.uploaded_at).toLocaleString()
        : "—";
      const actionCell = row.insertCell();
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = "View report";
      button.addEventListener("click", () => loadReport(dataset.id));
      actionCell.appendChild(button);
    }
  } catch (error) {
    const row = tbody.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 6;
    cell.className = "empty";
    cell.textContent = `Could not load datasets: ${error.message}`;
    setMessage(`Could not load dataset history: ${error.message}`, "error");
  }
}

async function loadReport(id) {
  try {
    const result = await apiRequest(`/api/datasets/${encodeURIComponent(id)}/report`);
    const report = result.report || {};
    const dataset = result.dataset || {};
    $("report-title").textContent = `Report: ${dataset.filename || `Dataset ${id}`}`;
    const stats = [
      ["Overall score", `${Number(report.scores?.overall ?? dataset.quality_score ?? 0).toFixed(2)}%`],
      ["Rows", Number(report.rows ?? dataset.rows ?? 0).toLocaleString()],
      ["Columns", Number(report.columns ?? dataset.columns ?? 0).toLocaleString()],
      ["Missing cells", Number(report.missing_cells ?? 0).toLocaleString()]
    ];
    const summary = $("report-summary");
    summary.replaceChildren();
    for (const [label, value] of stats) {
      const box = document.createElement("div");
      box.className = "report-stat";
      const caption = document.createElement("span");
      caption.textContent = label;
      const strong = document.createElement("strong");
      strong.textContent = value;
      box.append(caption, strong);
      summary.appendChild(box);
    }

    const columnsBody = $("column-details");
    columnsBody.replaceChildren();
    const details = report.column_details || {};
    const entries = Object.entries(details);
    if (!entries.length) {
      const row = columnsBody.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 5;
      cell.className = "empty";
      cell.textContent = "No column-level details are available.";
    } else {
      for (const [name, info] of entries) {
        const row = columnsBody.insertRow();
        [name, info.dtype ?? "—", info.missing ?? 0, info.unique ?? "—", info.outliers ?? 0]
          .forEach(value => row.insertCell().textContent = String(value));
      }
    }

    const issues = $("issues-list");
    issues.replaceChildren();
    const issueItems = report.issues || [];
    if (!issueItems.length) {
      const li = document.createElement("li");
      li.textContent = "No issues reported by the current analyzer.";
      issues.appendChild(li);
    } else {
      for (const issue of issueItems) {
        const li = document.createElement("li");
        li.textContent = issue;
        issues.appendChild(li);
      }
    }
    $("report-content").textContent = JSON.stringify(result, null, 2);
    $("report-panel").hidden = false;
    $("report-panel").scrollIntoView({ behavior: "smooth", block: "start" });
    setMessage(`Loaded report for ${dataset.filename || `dataset ${id}`}.`, "success");
  } catch (error) {
    setMessage(`Could not load report: ${error.message}`, "error");
  }
}

$("upload-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("csv-file").files[0];
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".csv")) {
    setMessage("Please choose a .csv file.", "error");
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    setMessage("The file exceeds the 5 MB upload limit.", "error");
    return;
  }

  const button = $("upload-button");
  button.disabled = true;
  setMessage("Uploading and analyzing your CSV…");
  try {
    const formData = new FormData();
    formData.append("file", file);
    const result = await apiRequest("/api/datasets", { method: "POST", body: formData });
    setMessage(`Analysis complete. Quality score: ${Number(result.quality_score).toFixed(2)}%.`, "success");
    $("upload-form").reset();
    $("file-label").textContent = "Choose a .csv file";
    await loadDatasets();
    await loadReport(result.id);
  } catch (error) {
    setMessage(`Upload failed: ${error.message}`, "error");
  } finally {
    button.disabled = false;
  }
});

$("csv-file").addEventListener("change", (event) => {
  $("file-label").textContent = event.target.files[0]?.name || "Choose a .csv file";
});
$("refresh-button").addEventListener("click", loadDatasets);
$("close-report").addEventListener("click", () => { $("report-panel").hidden = true; });

async function initializeDashboard() {
  try {
    await apiRequest("/api/health");
    $("api-status").textContent = "API connected";
    document.querySelector(".status-dot").classList.add("online");
  } catch {
    $("api-status").textContent = "API unavailable";
  }
  await loadDatasets();
}
initializeDashboard();
