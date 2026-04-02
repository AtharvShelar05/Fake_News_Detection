/**
 * FakeShield — Frontend Application Logic
 * =========================================
 * Handles user interaction, calls /check-news API,
 * and renders the structured verdict with confidence tier,
 * model agreement, and SHAP word-level explanations.
 */

"use strict";

// ── DOM references ────────────────────────────────────────────────────────────
const input       = document.getElementById("news-input");
const analyzeBtn  = document.getElementById("analyze-btn");
const wordCounter = document.getElementById("word-counter");
const loadingCard = document.getElementById("loading-card");
const resultCard  = document.getElementById("result-card");
const errorCard   = document.getElementById("error-card");
const errorMsg    = document.getElementById("error-msg");
const resetBtn    = document.getElementById("reset-btn");
const statusDot   = document.getElementById("status-dot");

// Result elements
const verdictBanner   = document.getElementById("verdict-banner");
const verdictIcon     = document.getElementById("verdict-icon");
const verdictLabel    = document.getElementById("verdict-label");
const verdictSub      = document.getElementById("verdict-sub");
const confidenceTier  = document.getElementById("confidence-tier");
const reasonText      = document.getElementById("reason-text");
const agreementBadge  = document.getElementById("agreement-badge");
const agreementModels = document.getElementById("agreement-models");
const explanationText = document.getElementById("explanation-text");
const shapMethod      = document.getElementById("shap-method");
const barReal         = document.getElementById("bar-real");
const barFake         = document.getElementById("bar-fake");
const pctReal         = document.getElementById("pct-real");
const pctFake         = document.getElementById("pct-fake");
const keywordCloud    = document.getElementById("keyword-cloud");
const factcheckBody   = document.getElementById("factcheck-body");
const modelBadge      = document.getElementById("model-badge");

// ── Loading stage helpers ─────────────────────────────────────────────────────
const stages = ["stage-1", "stage-2", "stage-3", "stage-4"];
let stageTimer = null;

function startLoadingStages() {
  stages.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.remove("active", "done");
  });
  let idx = 0;
  const advanceStage = () => {
    if (idx > 0) {
      const prev = document.getElementById(stages[idx - 1]);
      if (prev) { prev.classList.remove("active"); prev.classList.add("done"); }
    }
    if (idx < stages.length) {
      const cur = document.getElementById(stages[idx]);
      if (cur) cur.classList.add("active");
      idx++;
      stageTimer = setTimeout(advanceStage, 700);
    }
  };
  advanceStage();
}

function clearLoadingStages() {
  clearTimeout(stageTimer);
  stages.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.remove("active", "done");
  });
}

// ── Character counter ─────────────────────────────────────────────────────────
input.addEventListener("input", () => {
  const len = input.value.length;
  wordCounter.textContent = `${len.toLocaleString()} / 10,000 chars`;
  wordCounter.style.color = len > 9000 ? "var(--warn-color)" : "var(--text-3)";
});

// ── Example content ───────────────────────────────────────────────────────────
const EXAMPLES = {
  fake: `SHOCKING: Scientists Hired by Big Pharma Have SECRETLY Discovered That 5G Towers Inject Mind-Control Nanobots Through COVID Vaccines — Government Officials Caught Covering Up The Truth As Whistleblowers Expose The Biggest Scandal In History! Share This Before It Gets Deleted!`,
  real: `A new peer-reviewed study published in the New England Journal of Medicine found that moderate aerobic exercise performed at least three times per week significantly reduces the risk of cardiovascular disease in adults over 50. The research, conducted over five years with 12,000 participants, provides the strongest evidence yet linking regular physical activity to improved heart health outcomes.`,
};

document.querySelectorAll(".example-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const key = btn.getAttribute("data-example");
    input.value = EXAMPLES[key] || "";
    input.dispatchEvent(new Event("input"));
    input.focus();
    input.scrollIntoView({ behavior: "smooth", block: "center" });
  });
});

// ── Show / hide helpers ───────────────────────────────────────────────────────
function showCard(card) { card.removeAttribute("hidden"); }
function hideCard(card) { card.setAttribute("hidden", ""); }
function showError(msg) { errorMsg.textContent = msg; showCard(errorCard); }
function hideAll() { hideCard(loadingCard); hideCard(resultCard); hideCard(errorCard); }

// ── System health check ───────────────────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch("/health");
    const data = await res.json();
    if (data.models_loaded) {
      statusDot.classList.add("online");
      const parts = [`Model: loaded`];
      if (data.bert_loaded) parts.push("BERT: ✅");
      if (data.fact_check_api) parts.push("Fact-Check API: ✅");
      if (data.shap_ready) parts.push("SHAP: ✅");
      statusDot.title = parts.join(" | ");
    } else {
      statusDot.classList.add("offline");
      statusDot.title = `System degraded: ${data.init_error || "Unknown error"}`;
    }
  } catch {
    statusDot.classList.add("offline");
    statusDot.title = "Cannot reach server";
  }
}
checkHealth();

// ── Render result ─────────────────────────────────────────────────────────────
function renderResult(data) {
  const verdict      = data.final_verdict;
  const confidence    = data.confidence;
  const mlPred        = data.ml_prediction;
  const mlConf        = data.ml_confidence;
  const reason        = data.confidence_reason || "";
  const keywords      = data.top_keywords || [];
  const fcResults     = data.fact_check_results || [];
  const fcAvail       = data.fact_check_available;
  const modelSrc      = data.model_source || "baseline";
  const agreement     = data.model_agreement || "single_model";
  const individualPreds = data.individual_predictions || {};
  const shapData      = data.shap_explanations || {};

  const isFake = verdict === "FAKE";

  // ── Verdict banner ──────────────────────────────────────────────────────────
  verdictBanner.className = "verdict-banner";
  if (confidence === "High") {
    verdictBanner.classList.add(isFake ? "verdict-verified-fake" : "verdict-verified-real");
  } else {
    verdictBanner.classList.add(isFake ? "verdict-fake" : "verdict-real");
  }
  verdictIcon.textContent = isFake ? "🚨" : "✅";
  verdictLabel.textContent = verdict;

  let subParts = [`ML: ${mlPred} (${mlConf.toFixed(1)}%)`];
  if (fcResults.length > 0) subParts.push(`${fcResults.length} fact-check claim(s)`);
  verdictSub.textContent = subParts.join(" · ");

  // ── Confidence tier badge ───────────────────────────────────────────────────
  confidenceTier.className = "confidence-tier";
  confidenceTier.textContent = confidence;
  if (confidence === "High" && isFake) confidenceTier.classList.add("conf-high-fake");
  else if (confidence === "High") confidenceTier.classList.add("conf-high");
  else if (confidence === "Medium") confidenceTier.classList.add("conf-medium");
  else confidenceTier.classList.add("conf-low");

  // ── Reason bar ──────────────────────────────────────────────────────────────
  reasonText.textContent = reason;

  // ── Model agreement ─────────────────────────────────────────────────────────
  agreementBadge.className = "agreement-badge";
  if (agreement === "agree") {
    agreementBadge.textContent = "✅ Models Agree";
    agreementBadge.classList.add("agree");
  } else if (agreement === "disagree") {
    agreementBadge.textContent = "⚠️ Models Disagree";
    agreementBadge.classList.add("disagree");
  } else {
    agreementBadge.textContent = "Single Model";
    agreementBadge.classList.add("single");
  }

  // Show individual model predictions
  let modelsHtml = "";
  for (const [name, pred] of Object.entries(individualPreds)) {
    const displayName = name === "tfidf" ? "TF-IDF" : name === "bert" ? "BERT" : name;
    const cls = pred === "Fake" ? "pred-fake" : "pred-real";
    modelsHtml += `<span class="model-pred-chip">
      <span class="model-name">${escapeHtml(displayName)}:</span>
      <span class="${cls}">${escapeHtml(pred)}</span>
    </span>`;
  }
  agreementModels.innerHTML = modelsHtml;

  // ── SHAP Explanation (highlighted text) ─────────────────────────────────────
  const highlighted = shapData.highlighted_text || [];
  const method = shapData.method || "unavailable";

  shapMethod.textContent = method === "shap" ? "SHAP" : method === "tfidf_coefficients" ? "TF-IDF" : "N/A";

  if (highlighted.length > 0) {
    explanationText.innerHTML = highlighted.map(w => {
      if (w.direction === "neutral" || w.score === 0) {
        return `<span class="word-neutral">${escapeHtml(w.word)} </span>`;
      }
      const title = `${w.direction === "fake" ? "→ Fake" : "→ Real"} (score: ${w.score})`;
      return `<span class="word-highlight" style="background:${w.color}" title="${title}">${escapeHtml(w.word)} </span>`;
    }).join("");
  } else {
    explanationText.innerHTML = '<span class="detail-empty">No word-level explanations available</span>';
  }

  // ── Probability bars ────────────────────────────────────────────────────────
  const fakeP = isFake ? mlConf : 100 - mlConf;
  const realP = isFake ? 100 - mlConf : mlConf;
  requestAnimationFrame(() => {
    barReal.style.width = `${realP}%`;
    barFake.style.width = `${fakeP}%`;
  });
  pctReal.textContent = `${realP.toFixed(1)}%`;
  pctFake.textContent = `${fakeP.toFixed(1)}%`;

  // ── Keywords ────────────────────────────────────────────────────────────────
  if (keywords.length > 0) {
    keywordCloud.innerHTML = keywords.map(kw => {
      const cls = kw.direction === "fake" ? "kw-fake" : "kw-real";
      const title = `${kw.direction === "fake" ? "→ Fake" : "→ Real"} (score: ${kw.score})`;
      return `<span class="kw-chip ${cls}" title="${title}">${escapeHtml(kw.word)}</span>`;
    }).join("");
  } else {
    keywordCloud.innerHTML = '<span class="detail-empty">No keywords extracted</span>';
  }

  // ── Fact-check results ──────────────────────────────────────────────────────
  let fcHtml = "";
  if (!fcAvail) {
    fcHtml = `<span class="factcheck-status fc-unavailable">⚠️ API Key Not Set</span>
      <p style="font-size:12px;color:var(--text-3);margin-top:6px;">Add <code>FACT_CHECK_API_KEY</code> to <code>.env</code></p>`;
  } else if (fcResults.length > 0) {
    const overallSays = fcResults.some(c =>
      /false|fake|misleading|incorrect|hoax|debunked|pants on fire/i.test(c.rating)
    ) ? "fc-verified-fake" : "fc-verified-real";
    fcHtml = `<span class="factcheck-status ${overallSays}">${fcResults.length} Claim(s) Found</span>`;
    fcHtml += fcResults.map(c => `
      <div class="claim-item">
        <div class="claim-text">"${escapeHtml(truncate(c.claim, 150))}"</div>
        <div class="claim-rating">Rating: <strong>${escapeHtml(c.rating)}</strong></div>
        <div class="claim-pub">— ${escapeHtml(c.publisher)}
          ${c.url ? `<a href="${escapeHtml(c.url)}" target="_blank" rel="noopener" style="color:var(--accent-2);text-decoration:none;margin-left:6px;">[source ↗]</a>` : ""}
        </div>
      </div>`).join("");
  } else {
    fcHtml = `<span class="factcheck-status fc-no-match">No Matching Claims</span>
      <p style="font-size:12px;color:var(--text-3);margin-top:6px;">No fact-checked claims matched. ML prediction only.</p>`;
  }
  factcheckBody.innerHTML = fcHtml;

  // ── Model badge ─────────────────────────────────────────────────────────────
  modelBadge.textContent = `${modelSrc} · ${confidence} confidence`;
}

// ── Main prediction call ──────────────────────────────────────────────────────
async function runAnalysis() {
  const text = input.value.trim();
  if (!text) { hideAll(); showError("Please enter some text to analyze."); return; }
  if (text.length < 10) { hideAll(); showError("Text too short. Enter at least 10 characters."); return; }

  analyzeBtn.disabled = true;
  hideAll();
  showCard(loadingCard);
  startLoadingStages();

  try {
    const res = await fetch("/check-news", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    clearLoadingStages();
    hideCard(loadingCard);

    if (!res.ok || data.error) {
      showError(data.error || `Server error (${res.status}). Please try again.`);
      return;
    }
    renderResult(data);
    showCard(resultCard);
    resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (err) {
    clearLoadingStages();
    hideCard(loadingCard);
    showError("Network error — is the server running?");
    console.error("[FakeShield]", err);
  } finally {
    analyzeBtn.disabled = false;
  }
}

// ── Event listeners ───────────────────────────────────────────────────────────
analyzeBtn.addEventListener("click", runAnalysis);
input.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runAnalysis(); }
});
resetBtn.addEventListener("click", () => {
  hideAll();
  input.value = "";
  input.dispatchEvent(new Event("input"));
  input.focus();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function escapeHtml(str) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
  return String(str).replace(/[&<>"']/g, c => map[c]);
}
function truncate(str, max) {
  str = String(str);
  return str.length > max ? str.slice(0, max) + "…" : str;
}
