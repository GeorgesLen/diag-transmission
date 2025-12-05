import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from my_package.diagnostic_model import build_domains_for_sector, SECTORS
from my_package.scoring import score_global
from my_package.questionnaire import (
    extract_weak_points,
    extract_strong_points,
    load_answers_from_file,
    generate_sample_answers,
)


# Libellés lisibles pour les types de questions
TYPE_LABELS = {
    "stars": "Note (1 à 5)",
    "boolean": "Oui / Non",
}

def format_answer(ans, q_type: str) -> str:
    """Formate une réponse pour l'affichage dans le tableau."""
    if q_type == "stars":
        if ans is None:
            return "-"
        return f"{ans}/5"
    if q_type == "boolean":
        if ans is True:
            return "Oui"
        if ans is False:
            return "Non"
        return "-"
    # fallback pour d'autres types éventuels
    return str(ans)


# ---------------------------------------------------------
#  Configuration globale de la page
# ---------------------------------------------------------

st.set_page_config(
    page_title="Diagnostic Transmission",
    layout="wide",
    page_icon="📊",
)

# Un peu de CSS pour donner un look plus “app”
st.markdown(
    """
    <style>
    .big-metric {
        font-size: 38px;
        font-weight: 700;
    }
    .metric-label {
        font-size: 14px;
        text-transform: uppercase;
        color: #888;
    }
    .tag {
        display: inline-block;
        padding: 0.15rem 0.7rem;
        border-radius: 999px;
        background-color: #eef2ff;
        color: #4338ca;
        font-size: 12px;
        margin-right: 0.3rem;
        margin-bottom: 0.2rem;
    }
    .card {
        padding: 0.9rem 1.1rem;
        border-radius: 0.75rem;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.6rem;
    }
    .card-title {
        font-weight: 600;
        margin-bottom: 0.15rem;
        font-size: 14px;
    }
    .pill-ok {
        border-radius: 999px;
        padding: 0.1rem 0.7rem;
        font-size: 11px;
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 600;
    }
    .pill-mid {
        border-radius: 999px;
        padding: 0.1rem 0.7rem;
        font-size: 11px;
        background-color: #fef9c3;
        color: #92400e;
        font-weight: 600;
    }
    .pill-bad {
        border-radius: 999px;
        padding: 0.1rem 0.7rem;
        font-size: 11px;
        background-color: #fee2e2;
        color: #b91c1c;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
#  Fonctions utilitaires
# ---------------------------------------------------------

def list_answer_files(data_dir: Path) -> List[Path]:
    """Liste tous les fichiers .json dans le dossier data/."""
    if not data_dir.exists():
        return []
    return sorted(data_dir.glob("*.json"))


def classify_score(score: float) -> Tuple[str, str]:
    """
    Retourne (libellé, classe_css) pour un score de domaine ou global.

    >= 75 : "Fort"
    60–74 : "Bon"
    40–59 : "Moyen"
    20–39 : "À améliorer"
    <  20 : "Critique"
    """
    if score >= 75.0:
        return "Fort", "pill-ok"
    if score >= 60.0:
        return "Bon", "pill-ok"
    if score >= 40.0:
        return "Moyen", "pill-mid"
    if score >= 20.0:
        return "À améliorer", "pill-bad"
    return "Critique", "pill-bad"


def build_scores_dataframe(domains: Dict[str, Any], domain_scores: Dict[str, float]) -> pd.DataFrame:
    """Construit un DataFrame récapitulatif des scores par domaine."""
    rows = []
    for did, domain in domains.items():
        s = domain_scores.get(did, 0.0)
        level, _css = classify_score(s)
        rows.append(
            {
                "Domaine": domain.label,
                "Score (%)": round(s, 1),
                "Niveau": level,
            }
        )
    df = pd.DataFrame(rows)
    df = df.sort_values("Score (%)", ascending=False)
    return df


def build_radar_chart(df_scores: pd.DataFrame) -> go.Figure:
    """Crée le radar chart Plotly à partir du DataFrame des scores."""
    categories = df_scores["Domaine"].tolist()
    values = df_scores["Score (%)"].tolist()
    # radar fermé -> on répète la première valeur
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name="Score par domaine",
        )
    )
    fig.update_layout(
        showlegend=False,
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
        ),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    return fig


def build_bar_chart(df_scores: pd.DataFrame) -> go.Figure:
    """Crée un bar chart Plotly des scores."""
    fig = go.Figure(
        data=[
            go.Bar(
                x=df_scores["Domaine"],
                y=df_scores["Score (%)"],
            )
        ]
    )
    fig.update_layout(
        xaxis={"tickangle": -20},
        yaxis={"range": [0, 100]},
        margin=dict(l=20, r=20, t=20, b=30),
        height=320,
    )
    return fig


def generate_pdf_report(
    output_path: Path,
    sector_label: str,
    global_score: float,
    df_scores: pd.DataFrame,
) -> None:
    """
    Génère un petit rapport PDF à l'aide de fpdf2.
    Si la bibliothèque n'est pas disponible, on lève ImportError.
    """
    from fpdf import FPDF  # type: ignore

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Diagnostic de Transmission", ln=1)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Secteur : {sector_label}", ln=1)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Score global", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"{global_score:.1f} %", ln=1)
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Scores par domaine", ln=1)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    for _, row in df_scores.iterrows():
        pdf.cell(
            0,
            6,
            f"- {row['Domaine']} : {row['Score (%)']:.1f} % ({row['Niveau']})",
            ln=1,
        )

    pdf.output(str(output_path))


# ---------------------------------------------------------
#  BARRE LATERALE : paramètres et fichiers
# ---------------------------------------------------------

st.sidebar.header("⚙️ Paramètres")

# 1) Secteur
sector_ids = list(SECTORS.keys())
sector_id = st.sidebar.selectbox("Choisir un secteur :", sector_ids, index=0)

# 2) Fichier de réponses
data_dir = Path("data")
answer_files = list_answer_files(data_dir)
default_path = data_dir / "reponses_template.json"

if default_path not in answer_files:
    answer_files.insert(0, default_path)

file_labels = [f.name for f in answer_files]
selected_file_idx = st.sidebar.selectbox(
    "Fichier de réponses :",
    list(range(len(answer_files))),
    format_func=lambda i: file_labels[i],
)
answers_path = answer_files[selected_file_idx]

st.sidebar.markdown(f"Fichier utilisé : `{answers_path}`")

# 3) Bouton : générer des réponses d'exemple
if st.sidebar.button("🧪 Générer des réponses d'exemple"):
    domains_for_sample = build_domains_for_sector(sector_id)
    sample_answers = generate_sample_answers(domains_for_sample)

    answers_path.parent.mkdir(exist_ok=True)
    with answers_path.open("w", encoding="utf-8") as f:
        json.dump(sample_answers, f, ensure_ascii=False, indent=2)

    st.sidebar.success(f"Fichier d'exemple mis à jour : {answers_path}")
    st.rerun()


# ---------------------------------------------------------
#  Chargement des données
# ---------------------------------------------------------

domains = build_domains_for_sector(sector_id)

try:
    all_answers = load_answers_from_file(str(answers_path))
except FileNotFoundError:
    st.error(f"Fichier de réponses introuvable : {answers_path}")
    st.stop()
except json.JSONDecodeError as e:
    st.error(f"Erreur de lecture JSON dans {answers_path} : {e}")
    st.stop()

# Calcul des scores
domain_scores = score_global(domains, all_answers)
global_score = domain_scores.get("__global__", 0.0)

weak_points = extract_weak_points(domains, all_answers)
strong_points = extract_strong_points(domains, all_answers)

df_scores = build_scores_dataframe(domains, domain_scores)

sector_label = SECTORS.get(sector_id).label if sector_id in SECTORS else sector_id

# ---------------------------------------------------------
#  CONTENU PRINCIPAL
# ---------------------------------------------------------

st.title("📊 Tableau de bord – Diagnostic de Transmission")
st.caption("Prototype – version 2 (radar + cartes + barres)")

# --- Ligne 1 : score global + radar ---
col_score, col_radar = st.columns([1, 2])

with col_score:
    level, css_class = classify_score(global_score)
    st.markdown('<div class="metric-label">Score global</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="big-metric">{global_score:.1f} %</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<span class="{css_class}">{level}</span>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("**Secteur :**", sector_label)

with col_radar:
    st.subheader("❄️ Scores par domaine (radar)")
    radar_fig = build_radar_chart(df_scores)
    st.plotly_chart(radar_fig, use_container_width=True)

st.markdown("---")

# Tabs pour structurer le reste
tab_overview, tab_details, tab_data = st.tabs(
    ["Vue d'ensemble", "Détail par domaine", "Données & export"]
)

# ---------------------------------------------------------
#  TAB 1 : Vue d'ensemble
# ---------------------------------------------------------
with tab_overview:
    # --- Résumé rapide ---
    st.subheader("📌 Résumé rapide")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Nombre de domaines évalués :** "
                    f"{len(domains)}")
        st.markdown(f"**Fichier de réponses utilisé :** `{answers_path}`")

    with c2:
        st.markdown("**Domaines les plus faibles :**")
        if weak_points:
            for did, score in weak_points.items():
                label = domains[did].label
                st.markdown(f"- {label} : **{score:.1f} %**")
        else:
            st.write("Aucun domaine faible.")

    st.markdown("")

    # --- Scores par domaine (barres) ---
    st.subheader("📊 Scores par domaine (barres)")
    bar_fig = build_bar_chart(df_scores)
    st.plotly_chart(bar_fig, use_container_width=True)

    # --- Points faibles / forts sous forme de cartes ---
    c_weak, c_strong = st.columns(2)

    with c_weak:
        st.subheader("🔻 Points faibles")
        if weak_points:
            for did, score in weak_points.items():
                dom = domains[did]
                level, css_class = classify_score(score)
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-title">{dom.label}</div>
                        <div>Score : <b>{score:.1f} %</b>
                        &nbsp;&nbsp;<span class="{css_class}">{level}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aucun domaine faible identifié.")

    with c_strong:
        st.subheader("🔺 Points forts")
        if strong_points:
            for did, score in strong_points.items():
                dom = domains[did]
                level, css_class = classify_score(score)
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-title">{dom.label}</div>
                        <div>Score : <b>{score:.1f} %</b>
                        &nbsp;&nbsp;<span class="{css_class}">{level}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aucun domaine fort identifié.")

    st.markdown("---")

    # --- Domaines inclus dans le secteur ---
    st.subheader("🌟 Domaines inclus dans le secteur")
    tags_html = "".join(
        f'<span class="tag">{dom.label}</span>'
        for dom in domains.values()
    )
    st.markdown(tags_html, unsafe_allow_html=True)

    st.markdown("---")

    # --- Tableau récapitulatif ---
    st.subheader("📑 Tableau récapitulatif des scores par domaine")
    st.dataframe(
        df_scores.set_index("Domaine"),
        use_container_width=True,
        height=315,
    )


# ---------------------------------------------------------
#  TAB 2 : Détail par domaine
# ---------------------------------------------------------
with tab_details:
    st.subheader("🔍 Analyse détaillée par domaine")

    domain_ids = list(domains.keys())
    domain_labels = [domains[d].label for d in domain_ids]

    selected_idx = st.selectbox(
        "Choisir un domaine :",
        list(range(len(domain_ids))),
        format_func=lambda i: domain_labels[i],
    )
    selected_id = domain_ids[selected_idx]
    selected_domain = domains[selected_id]

    score_dom = domain_scores.get(selected_id, 0.0)
    level, css_class = classify_score(score_dom)

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{selected_domain.label}</div>
            <div style="margin-top:0.2rem;">
                Score : <b>{score_dom:.1f} %</b>
                &nbsp;&nbsp;<span class="{css_class}">{level}</span>
            </div>
            <div style="margin-top:0.4rem;color:#6b7280;font-size:13px;">
                {selected_domain.description}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Affichage des questions & réponses
st.markdown("#### Questions et réponses")

answers_for_dom: Dict[str, Any] = all_answers.get(selected_id, {})
if not answers_for_dom:
    st.info("Aucune réponse saisie pour ce domaine.")
else:
    rows_q = []
    for idx, q in enumerate(selected_domain.questions, start=1):
        ans = answers_for_dom.get(q.id)
        rows_q.append(
            {
                "N°": idx,
                "Question": q.text,
                "Type": TYPE_LABELS.get(q.type, q.type),
                "Réponse": format_answer(ans, q.type),
            }
        )

    df_q = pd.DataFrame(rows_q)

    # Un seul tableau, large, sans index pandas
    st.dataframe(
        df_q,
        hide_index=True,
        use_container_width=True,
    )



    # 🔧 Sécurité supplémentaire : forcer le type string dans toute la colonne
    # df_q["Réponse"] = df_q["Réponse"].astype(str)

    # Affichage amélioré en tableau Streamlit
    # st.dataframe(df_q, width="stretch", hide_index=True)



# ---------------------------------------------------------
#  TAB 3 : Données & export
# ---------------------------------------------------------
with tab_data:
    st.subheader("📂 Données & export")

    col_raw, col_export = st.columns([2, 1])

    with col_raw:
        st.markdown("**JSON brut des réponses**")
        st.json(all_answers)

        st.markdown("**Tableau des scores par domaine**")
        st.dataframe(df_scores, use_container_width=True)

    with col_export:
        st.markdown("### 📄 Export du rapport")

        # Génération à la demande -> PDF en mémoire
        if st.button("Télécharger le rapport PDF"):
            try:
                output_path = Path("output/rapport_diagnostic.pdf")
                output_path.parent.mkdir(exist_ok=True)
                generate_pdf_report(
                    output_path=output_path,
                    sector_label=sector_label,
                    global_score=global_score,
                    df_scores=df_scores,
                )
                with output_path.open("rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="⬇️ Télécharger le rapport",
                    data=pdf_bytes,
                    file_name="rapport_diagnostic.pdf",
                    mime="application/pdf",
                )
                st.success("Rapport PDF généré.")
            except ImportError:
                st.error(
                    "La bibliothèque `fpdf2` n'est pas installée.\n\n"
                    "Installe-la avec : `pip install fpdf2`."
                )
