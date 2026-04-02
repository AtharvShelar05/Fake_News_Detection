"""
visualization/dashboard.py
==========================
TruthLens: Premium Fake News Detection Dashboard
Integrates EnsemblePredictor, SHAP/TF-IDF explainability, and SIR propagation data.
"""

import json
import os
import sys
import re
import glob
import pickle
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
from matplotlib.cm import viridis
import plotly.graph_objects as go

# ── Path setup ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TruthLens | AI Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.9) !important;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    section[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

    h1, h2, h3, h4 { color: #f8fafc !important; font-weight: 700 !important; letter-spacing: -0.02em; }

    .stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.7) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        line-height: 1.7 !important;
        transition: border-color 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15) !important;
    }
    .stTextArea label { color: #94a3b8 !important; font-weight: 500 !important; }

    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
        color: #fff !important; border: none !important;
        border-radius: 10px !important; padding: 0.75rem 2rem !important;
        font-weight: 700 !important; font-size: 1.05rem !important;
        letter-spacing: 0.3px; transition: all 0.25s ease !important;
        width: 100%; cursor: pointer;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.45) !important;
    }

    .glass-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px; padding: 1.5rem 2rem;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
        margin-bottom: 1.5rem;
    }

    .verdict-fake  { background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.35); border-radius: 12px; padding: 1rem 1.5rem; }
    .verdict-real  { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.35); border-radius: 12px; padding: 1rem 1.5rem; }
    .verdict-uncert { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.35); border-radius: 12px; padding: 1rem 1.5rem; }

    .verdict-title {
        font-size: 2rem; font-weight: 800; margin: 0;
        letter-spacing: -0.03em;
    }
    .verdict-title.fake    { color: #f87171; }
    .verdict-title.real    { color: #34d399; }
    .verdict-title.uncert  { color: #fbbf24; }

    .prob-label { font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
                  letter-spacing: 1px; color: #64748b; margin-bottom: 0.25rem; }
    .prob-value { font-size: 1.1rem; font-weight: 700; }

    .highlight-fake { background: rgba(239,68,68,0.25); color: #fca5a5;
                      border-radius: 4px; padding: 1px 5px; font-weight: 600; }
    .highlight-real { background: rgba(16,185,129,0.25); color: #6ee7b7;
                      border-radius: 4px; padding: 1px 5px; font-weight: 600; }

    .risk-banner-high { background: rgba(239,68,68,0.12); border-left: 4px solid #ef4444;
                        color: #fca5a5; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0;
                        margin-top: 0.75rem; font-size: 0.9rem; }
    .risk-banner-low  { background: rgba(16,185,129,0.12); border-left: 4px solid #10b981;
                        color: #6ee7b7; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0;
                        margin-top: 0.75rem; font-size: 0.9rem; }
    .uncert-banner    { background: rgba(245,158,11,0.12); border-left: 4px solid #f59e0b;
                        color: #fcd34d; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0;
                        margin-top: 0.75rem; font-size: 0.9rem; font-weight: 600; }

    .mode-badge {
        display: inline-block; background: rgba(99,102,241,0.2);
        color: #a5b4fc; border: 1px solid rgba(99,102,241,0.4);
        border-radius: 999px; padding: 2px 12px; font-size: 0.8rem; font-weight: 600;
    }

    .stRadio label { color: #94a3b8 !important; }
    .stMetric { background: rgba(255,255,255,0.03); border-radius: 10px; padding: 0.5rem !important; }
    .stMetric label { color: #64748b !important; }
    .stDataFrame { background: rgba(15,23,42,0.6) !important; }
    .stSpinner > div { color: #38bdf8 !important; }
</style>
""", unsafe_allow_html=True)


# ── Cached resource loading ───────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading AI models (first run may take ~30s)…")
def load_predictor():
    from realtime.ensemble import EnsemblePredictor
    return EnsemblePredictor()

@st.cache_resource(show_spinner=False)
def load_explainer(model_path, vec_path):
    from realtime.explainer import load_explainer_from_paths
    return load_explainer_from_paths(model_path, vec_path)

@st.cache_resource(show_spinner=False)
def load_shap_explainer(vec_path, model_path):
    try:
        from realtime.shap_explainer import SHAPExplainer
        with open(vec_path, "rb") as f:
            vec = pickle.load(f)
        with open(model_path, "rb") as f:
            obj = pickle.load(f)
        clf = obj.get("model") if isinstance(obj, dict) else obj
        return SHAPExplainer(vec, clf)
    except Exception as e:
        logger.warning(f"SHAP explainer unavailable: {e}")
        return None

@st.cache_data
def load_graph_stats():
    path = os.path.join(BASE_DIR, "data", "processed", "graph_statistics.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

@st.cache_data
def load_diffusion_data():
    trajectories = {}
    pattern = os.path.join(BASE_DIR, "data", "processed", "diffusion_trajectory_prob*.json")
    for filepath in sorted(glob.glob(pattern)):
        prob = os.path.basename(filepath).replace("diffusion_trajectory_prob","").replace(".json","")
        with open(filepath) as f:
            trajectories[prob] = json.load(f)
    return trajectories


# ── Helpers ───────────────────────────────────────────────────────────────────

def clean_input(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r"http\S+", "", text)
    return text if len(text) >= 10 else ""

def highlight_words(text: str, words: list) -> str:
    out = text
    for item in words:
        word = item.get("word", "")
        direction = item.get("direction", "neutral")
        cls = "highlight-fake" if direction == "fake" else "highlight-real"
        out = re.sub(rf'\b({re.escape(word)})\b',
                     rf'<span class="{cls}">\1</span>',
                     out, flags=re.IGNORECASE)
    return f"""<div style="font-size:1rem;line-height:1.85;color:#cbd5e1;
                padding:1.2rem 1.5rem;background:rgba(15,23,42,0.6);
                border-radius:10px;border:1px solid rgba(255,255,255,0.06);">{out}</div>"""

def confidence_donut(real_p, fake_p):
    fig = go.Figure(go.Pie(
        labels=["Real", "Fake"],
        values=[real_p, fake_p],
        hole=0.62,
        marker_colors=["#10b981", "#ef4444"],
        textinfo="percent",
        textfont_size=13,
        hovertemplate="%{label}: %{value:.1%}<extra></extra>"
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(font=dict(color="#94a3b8", size=13)),
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        annotations=[dict(
            text=f"<b>{max(real_p, fake_p)*100:.1f}%</b>",
            x=0.5, y=0.5, font_size=22, showarrow=False,
            font_color="#f1f5f9"
        )]
    )
    return fig

def bar_chart_words(words):
    if not words:
        return None
    labels = [w["word"] for w in words[:10]]
    scores = [w["score"] for w in words[:10]]
    dirs   = [w.get("direction", "neutral") for w in words[:10]]
    colors = ["#ef4444" if d=="fake" else "#10b981" for d in dirs]
    fig = go.Figure(go.Bar(
        x=scores, y=labels, orientation='h',
        marker_color=colors,
        hovertemplate="%{y}: %{x:.4f}<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10), height=280,
        xaxis=dict(color="#64748b", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(color="#94a3b8", autorange="reversed"),
        font=dict(color="#94a3b8", size=12),
    )
    return fig


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔍 TruthLens")
    st.markdown("<p style='color:#64748b;font-size:0.85rem;'>AI-Powered Disinformation Engine</p>", unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("Navigation", [
        "🕵️ Fake News Detector",
        "📊 Propagation Analysis",
        "🌐 Network Visualization",
    ])

    st.markdown("---")
    st.markdown("**Model Configuration**")
    confidence_threshold_high = st.slider("REAL threshold (≥)", 0.50, 0.90, 0.70, 0.05)
    confidence_threshold_low  = st.slider("FAKE threshold (≤)", 0.10, 0.50, 0.30, 0.05)
    top_n_words = st.slider("Explanation words", 5, 15, 10)
    st.markdown("---")
    st.markdown("<p style='color:#475569;font-size:0.8rem;'>DistilBERT + TF-IDF Ensemble<br>SHAP Word Explainability<br>SIR Propagation Model</p>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE 1 — FAKE NEWS DETECTOR
# ═══════════════════════════════════════════════════════════════════

if "Detector" in page:
    st.markdown("# <span style='background:linear-gradient(90deg,#38bdf8,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>TruthLens</span> Fake News Detector 🕵️", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b;margin-bottom:1.5rem;'>Analyze news articles using our DistilBERT + TF-IDF ensemble with word-level explainability.</p>", unsafe_allow_html=True)

    # Load models
    try:
        predictor = load_predictor()
        model_path = os.path.join(BASE_DIR, "ml_models", "fake_news_model.pkl")
        vec_path   = os.path.join(BASE_DIR, "ml_models", "vectorizer.pkl")
        tfidf_explainer = load_explainer(model_path, vec_path)
        shap_explainer  = load_shap_explainer(vec_path, model_path)
    except Exception as e:
        st.error(f"❌ Failed to load models: {e}")
        st.stop()

    mode = st.radio("Prediction Mode", ["🤝 Ensemble (Recommended)", "🧠 BERT Only", "📋 TF-IDF Only"], horizontal=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    news_text = st.text_area("Paste the news article content below:", height=180, placeholder="e.g. 'Scientists confirm that drinking coffee cures cancer according to a leaked NASA report…'", label_visibility="visible")
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        analyze = st.button("🚀 Analyze Article")
    with col_info:
        st.markdown(f"<p style='color:#475569;font-size:0.85rem;padding-top:0.6rem;'>REAL threshold ≥ {confidence_threshold_high:.0%} | FAKE threshold ≤ {confidence_threshold_low:.0%}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze:
        cleaned = clean_input(news_text)
        if not cleaned:
            st.warning("Please enter at least 10 characters of news text.")
        else:
            with st.spinner("Running inference and computing explanations…"):
                result = predictor.predict(cleaned)

            real_p   = result["real_proba"]
            fake_p   = result["fake_proba"]
            raw_label = result["label"]   # "Real" | "Fake"
            model_src = result["model_source"]
            agreement = result["model_agreement"]
            ind_preds = result.get("individual_predictions", {})

            # Apply configurable thresholds
            if real_p >= confidence_threshold_high:
                verdict, vclass = "AUTHENTIC ✅", "real"
            elif real_p <= confidence_threshold_low:
                verdict, vclass = "FABRICATED 🚨", "fake"
            else:
                verdict, vclass = "UNCERTAIN ⚠️", "uncert"

            # Explainability words
            with st.spinner("Computing word importance…"):
                if shap_explainer and shap_explainer.is_ready():
                    words = shap_explainer.explain(cleaned, top_n=top_n_words)
                    explain_method = "SHAP"
                elif tfidf_explainer and tfidf_explainer.is_ready():
                    words = tfidf_explainer.explain(cleaned, top_n=top_n_words)
                    explain_method = "TF-IDF coefficients"
                else:
                    words, explain_method = [], "unavailable"

            graph_stats = load_graph_stats()

            # ── Results layout ──────────────────────────────────────────────
            st.markdown("---")
            st.subheader("📋 Analysis Report")

            r1, r2 = st.columns([1, 2])

            with r1:
                st.markdown(f"""
                <div class="verdict-{vclass}">
                    <div style="color:#64748b;font-size:0.8rem;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">VERDICT</div>
                    <div class="verdict-title {vclass}">{verdict}</div>
                    <div style="color:#64748b;font-size:0.85rem;margin-top:8px;">
                        via <span class="mode-badge">{model_src}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

                # Propagation risk
                if vclass == "fake" and graph_stats:
                    density = graph_stats.get("density", 0)
                    if density > 0.2:
                        st.markdown(f"<div class='risk-banner-high'>🌋 <strong>High Spread Risk</strong><br>Network density {density:.3f} — viral spread likely in this environment.</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='risk-banner-low'>🛡️ <strong>Low Spread Risk</strong><br>Network density {density:.3f} — diffusion expected to remain limited.</div>", unsafe_allow_html=True)

                if vclass == "uncert":
                    st.markdown("<div class='uncert-banner'>⚠️ Confidence marginal — manual verification recommended.</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Real Prob.", f"{real_p*100:.1f}%")
                with c2:
                    st.metric("Fake Prob.", f"{fake_p*100:.1f}%")

                if ind_preds:
                    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
                    for model_name, label in ind_preds.items():
                        color = "#34d399" if label == "Real" else "#f87171"
                        st.markdown(f"<p style='margin:2px 0;font-size:0.85rem;color:#64748b;'><b style='color:{color};'>{label}</b> — {model_name}</p>", unsafe_allow_html=True)

            with r2:
                tab1, tab2, tab3 = st.tabs(["📊 Confidence Chart", "🔍 Highlighted Text", "📈 Word Importance"])

                with tab1:
                    fig_donut = confidence_donut(real_p, fake_p)
                    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
                    st.markdown(f"<p style='text-align:center;color:#475569;font-size:0.8rem;'>Model agreement: <b>{agreement}</b></p>", unsafe_allow_html=True)

                with tab2:
                    if words:
                        st.markdown(highlight_words(cleaned, words), unsafe_allow_html=True)
                        st.markdown(f"<p style='color:#475569;font-size:0.8rem;margin-top:0.5rem;'>🟥 Fake indicators &nbsp; 🟩 Real indicators &nbsp;|&nbsp; Method: {explain_method}</p>", unsafe_allow_html=True)
                    else:
                        st.info("Word importance is not available for this prediction.")

                with tab3:
                    if words:
                        fig_bar = bar_chart_words(words)
                        if fig_bar:
                            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
                        df_words = pd.DataFrame(words)[["word", "score", "direction"]]
                        df_words.columns = ["Word", "Importance", "Direction"]
                        st.dataframe(df_words, use_container_width=True, hide_index=True)
                    else:
                        st.info("No word importance data available.")


# ═══════════════════════════════════════════════════════════════════
#  PAGE 2 — PROPAGATION ANALYSIS  (existing viz kept intact)
# ═══════════════════════════════════════════════════════════════════

elif "Propagation" in page:
    st.title("📊 SIR Propagation Analysis")
    st.markdown("<p style='color:#64748b;'>Explore how misinformation spreads through the network using the SIR model.</p>", unsafe_allow_html=True)

    graph_stats = load_graph_stats()
    diffusion   = load_diffusion_data()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nodes",    graph_stats.get("num_nodes", "N/A"))
    c2.metric("Edges",    graph_stats.get("num_edges", "N/A"))
    c3.metric("Density",  f"{graph_stats.get('density', 0):.3f}")
    c4.metric("Avg Degree", f"{graph_stats.get('avg_degree', 0):.2f}")

    st.markdown("---")
    if diffusion:
        probs = sorted(diffusion.keys(), key=float)
        sel   = st.selectbox("Infection Probability Scenario", probs)
        traj  = diffusion[sel]["trajectory"]
        t     = list(range(len(traj)))
        S, I, R = zip(*traj)

        fig, ax = plt.subplots(figsize=(11, 4), facecolor="#0f172a")
        ax.set_facecolor("#0f172a")
        ax.plot(t, S, "o-", color="#38bdf8", lw=2, ms=4, label="Susceptible")
        ax.plot(t, I, "s-", color="#f97316", lw=2, ms=4, label="Infected")
        ax.plot(t, R, "^-", color="#10b981", lw=2, ms=4, label="Recovered")
        ax.fill_between(t, 0, I, alpha=0.15, color="#f97316")
        ax.set_xlabel("Time Steps", color="#64748b")
        ax.set_ylabel("Population", color="#64748b")
        ax.set_title(f"SIR Trajectory — Infection Probability {sel}", color="#f1f5f9", fontweight="bold")
        ax.legend(facecolor="#1e293b", labelcolor="#cbd5e1")
        ax.tick_params(colors="#475569")
        for spine in ax.spines.values():
            spine.set_edgecolor("#334155")
        ax.grid(alpha=0.12, color="#334155")
        st.pyplot(fig)
        plt.close()

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Peak Infected",     max(I))
        d2.metric("Final Recovered",   R[-1])
        d3.metric("Final Susceptible", S[-1])
        total = S[0]
        d4.metric("Spread Rate",       f"{R[-1]/total*100:.1f}%" if total else "N/A")


# ═══════════════════════════════════════════════════════════════════
#  PAGE 3 — NETWORK VISUALIZATION (existing viz kept intact)
# ═══════════════════════════════════════════════════════════════════

elif "Network" in page:
    st.title("🌐 Social Network Visualization")
    st.markdown("<p style='color:#64748b;'>Explore the structure of the simulated social network.</p>", unsafe_allow_html=True)

    graph_stats = load_graph_stats()

    try:
        with open(os.path.join(BASE_DIR, "data", "processed", "centrality_metrics.json")) as f:
            centrality = json.load(f)
        with open(os.path.join(BASE_DIR, "data", "processed", "influential_spreaders.json")) as f:
            spreaders = json.load(f)

        G = nx.DiGraph()
        n = graph_stats.get("num_nodes", 15)
        users = list(centrality["degree_centrality"].keys())
        G.add_nodes_from(users)
        deg = centrality["degree_centrality"]
        for i, u1 in enumerate(users):
            for j, u2 in enumerate(users):
                if i != j and np.random.random() < 0.4:
                    G.add_edge(u1, u2)

        inf_dict = {s["user_id"]: s["influence_score"] for s in spreaders["top_spreaders"]}
        pos = nx.spring_layout(G, k=2, seed=42)

        fig, ax = plt.subplots(figsize=(12, 9), facecolor="#0f172a")
        ax.set_facecolor("#0f172a")
        nsizes = [inf_dict.get(nd, 0.05) * 3000 for nd in G.nodes()]
        ncolor = [deg.get(nd, 0) for nd in G.nodes()]
        nx.draw_networkx_edges(G, pos, edge_color="#334155", alpha=0.4, arrows=True, arrowsize=10, ax=ax, connectionstyle="arc3,rad=0.1")
        nodes = nx.draw_networkx_nodes(G, pos, node_size=nsizes, node_color=ncolor, cmap=viridis, alpha=0.85, ax=ax)
        nx.draw_networkx_labels(G, pos, labels={nd: nd.replace("user","") for nd in G.nodes()}, font_size=8, font_color="#f1f5f9", font_weight="bold", ax=ax)
        ax.set_title("Social Network — Influence Propagation Map", color="#f1f5f9", fontsize=14, fontweight="bold")
        ax.axis("off")
        st.pyplot(fig)
        plt.close()

    except Exception as e:
        st.warning(f"Could not load network data: {e}")


# ── Footer ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<p style='text-align:center;color:#334155;font-size:0.8rem;'>TruthLens · DistilBERT + TF-IDF Ensemble · SHAP Explainability · SIR Propagation Model</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    pass
