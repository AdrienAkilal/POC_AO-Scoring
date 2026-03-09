"""Application Streamlit principale pour le scoring d'AO"""
import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime
import logging

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ingestion import PDFProcessor
from src.parser import NLPExtractor
from src.rag import REGManager
from src.scoring import PapersAPI, ScoringEngine
from src.livrables import DocumentGenerator
from src.models import AppelOffre, AOStatus, DecisionType, AOHistorique
from src.config import AO_PDF_DIR, HISTORIQUE_DIR

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la page
st.set_page_config(
    page_title="POC AO Scoring",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1976d2;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1976d2;
    }
    .decision-go {
        color: #2e7d32;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .decision-reserve {
        color: #f57c00;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .decision-nogo {
        color: #d32f2f;
        font-weight: bold;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialisation de la session state
def init_session_state():
    """Initialise les variables de session"""
    if 'ao_list' not in st.session_state:
        st.session_state.ao_list = []
    if 'current_ao' not in st.session_state:
        st.session_state.current_ao = None
    if 'reg_manager' not in st.session_state:
        st.session_state.reg_manager = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False


def initialize_components():
    """Initialise les composants du système"""
    if not st.session_state.initialized:
        with st.spinner("Initialisation du système..."):
            try:
                # Initialiser le REG Manager
                st.session_state.reg_manager = REGManager()

                # Vérifier si la base REG est indexée
                stats = st.session_state.reg_manager.get_collection_stats()
                if stats.get('count', 0) == 0:
                    st.warning("⚠️ La base REG n'est pas indexée. Veuillez indexer les documents REG.")
                else:
                    st.success(f"✅ Base REG initialisée: {stats['count']} documents")

                st.session_state.initialized = True

            except Exception as e:
                st.error(f"Erreur lors de l'initialisation: {e}")
                logger.error(f"Initialization error: {e}", exc_info=True)


def load_historique() -> list:
    """Charge l'historique des AO"""
    historique_file = HISTORIQUE_DIR / "historique_ao.json"
    if historique_file.exists():
        with open(historique_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [AOHistorique(**ao) for ao in data]
    return []


def analyze_ao(pdf_file):
    """Analyse complète d'un AO"""
    try:
        # Sauvegarder le PDF
        ao_id = f"AO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pdf_path = AO_PDF_DIR / f"{ao_id}.pdf"

        with open(pdf_path, 'wb') as f:
            f.write(pdf_file.getbuffer())

        # Créer l'objet AO
        ao = AppelOffre(
            ao_id=ao_id,
            source_file=pdf_file.name,
            status=AOStatus.UPLOADED
        )

        progress_bar = st.progress(0)
        status_text = st.empty()

        # 1. Extraction PDF
        status_text.text("📄 Extraction du PDF...")
        progress_bar.progress(10)
        pdf_processor = PDFProcessor()
        pdf_data = pdf_processor.extract_text(pdf_path)

        # 2. Parsing NLP
        status_text.text("🤖 Extraction NLP avec GPT-4o...")
        progress_bar.progress(30)
        ao.status = AOStatus.PARSING
        nlp_extractor = NLPExtractor()
        ao.context = nlp_extractor.extract_context(pdf_data['text'], ao_id)

        # 3. Recherche RAG
        status_text.text("🔍 Recherche dans le REG...")
        progress_bar.progress(50)
        requirements = nlp_extractor.extract_key_requirements(ao.context)
        ao.evidences_reg = st.session_state.reg_manager.search_for_requirements(requirements)

        # 4. Récupération profil entreprise
        status_text.text("🏢 Récupération profil entreprise...")
        progress_bar.progress(60)
        papers_api = PapersAPI()
        ao.profil_entreprise = papers_api.get_profil_entreprise()

        # 5. Chargement historique
        status_text.text("📚 Analyse historique...")
        progress_bar.progress(70)
        ao.ao_similaires = load_historique()

        # 6. Scoring
        status_text.text("🎯 Calcul du score...")
        progress_bar.progress(80)
        scoring_engine = ScoringEngine()
        ao.scoring = scoring_engine.score_ao(
            ao.context,
            ao.evidences_reg,
            ao.profil_entreprise,
            ao.ao_similaires
        )
        ao.status = AOStatus.SCORED

        progress_bar.progress(100)
        status_text.text("✅ Analyse terminée!")

        # Ajouter à la liste
        st.session_state.ao_list.append(ao)
        st.session_state.current_ao = ao

        return ao

    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse: {e}")
        logger.error(f"Analysis error: {e}", exc_info=True)
        return None


def display_ao_list():
    """Affiche la liste des AO"""
    st.markdown('<div class="main-header">📊 Liste des Appels d\'Offres</div>', unsafe_allow_html=True)

    if not st.session_state.ao_list:
        st.info("Aucun AO analysé. Uploadez un PDF dans la barre latérale.")
        return

    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_decision = st.selectbox(
            "Filtrer par décision",
            ["Tous", "Go", "Go sous réserve", "No-Go"]
        )
    with col2:
        filter_score_min = st.slider("Score minimum", 0, 100, 0)

    # Tableau des AO
    for ao in st.session_state.ao_list:
        if ao.scoring:
            # Appliquer les filtres
            if filter_decision != "Tous" and ao.scoring.decision.value != filter_decision:
                continue
            if ao.scoring.score_global < filter_score_min:
                continue

            # Afficher l'AO
            with st.expander(f"📄 {ao.context.titre if ao.context else ao.source_file}"):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Score", f"{ao.scoring.score_global:.1f}/100")
                with col2:
                    decision_class = "decision-go" if ao.scoring.decision == DecisionType.GO else \
                                   "decision-reserve" if ao.scoring.decision == DecisionType.GO_RESERVE else \
                                   "decision-nogo"
                    st.markdown(f'<div class="{decision_class}">{ao.scoring.decision.value}</div>',
                              unsafe_allow_html=True)
                with col3:
                    if ao.context and ao.context.date_limite:
                        st.metric("Date limite", ao.context.date_limite.strftime('%d/%m/%Y'))
                with col4:
                    if st.button("Voir détails", key=f"view_{ao.ao_id}"):
                        st.session_state.current_ao = ao
                        st.rerun()


def display_ao_detail():
    """Affiche le détail d'un AO"""
    ao = st.session_state.current_ao

    if not ao:
        st.warning("Aucun AO sélectionné")
        return

    if st.button("⬅️ Retour à la liste"):
        st.session_state.current_ao = None
        st.rerun()

    st.markdown(f'<div class="main-header">📋 {ao.context.titre if ao.context else ao.source_file}</div>',
                unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Score", "📝 Contexte", "🔍 Preuves REG", "📦 Livrables"])

    with tab1:
        display_scoring_tab(ao)

    with tab2:
        display_context_tab(ao)

    with tab3:
        display_evidences_tab(ao)

    with tab4:
        display_livrables_tab(ao)


def display_scoring_tab(ao):
    """Affiche l'onglet scoring"""
    if not ao.scoring:
        st.warning("Scoring non disponible")
        return

    # Score global
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Score Global", f"{ao.scoring.score_global:.1f}/100")

    with col2:
        decision_emoji = "✅" if ao.scoring.decision == DecisionType.GO else \
                        "⚠️" if ao.scoring.decision == DecisionType.GO_RESERVE else "❌"
        st.metric("Décision", f"{decision_emoji} {ao.scoring.decision.value}")

    with col3:
        if ao.context and ao.context.budget_indicatif:
            st.metric("Budget", f"{ao.context.budget_indicatif:,.0f} €")

    # Red flags
    if ao.scoring.red_flags_bloquants:
        st.error("🚨 Red Flags Bloquants")
        for flag in ao.scoring.red_flags_bloquants:
            st.write(f"**{flag.type}**: {flag.description}")

    # Scores détaillés
    st.subheader("Scores par Critère")

    for detail in ao.scoring.scores_details:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.progress(detail.score / 100)
            st.caption(f"**{detail.critere}** ({detail.poids*100:.0f}%)")
            st.write(detail.justification)

        with col2:
            st.metric("Score", f"{detail.score:.0f}/100")

        if detail.evidences:
            with st.expander("Voir les preuves"):
                for evidence in detail.evidences:
                    st.write(f"- {evidence}")

        st.divider()

    # Points à clarifier
    if ao.scoring.points_a_clarifier:
        st.warning("⚠️ Points à Clarifier")
        for point in ao.scoring.points_a_clarifier:
            st.write(f"- {point}")

    # Recommandations
    if ao.scoring.recommandations:
        st.info("💡 Recommandations")
        for reco in ao.scoring.recommandations:
            st.write(f"- {reco}")


def display_context_tab(ao):
    """Affiche l'onglet contexte"""
    if not ao.context:
        st.warning("Contexte non disponible")
        return

    # Informations générales
    st.subheader("Informations Générales")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Organisme:** {ao.context.organisme}")
        if ao.context.date_limite:
            st.write(f"**Date limite:** {ao.context.date_limite.strftime('%d/%m/%Y %H:%M')}")

    with col2:
        if ao.context.budget_indicatif:
            st.write(f"**Budget:** {ao.context.budget_indicatif:,.0f} €")

    st.write("**Résumé:**")
    st.write(ao.context.resume)

    # Exigences
    st.subheader(f"Exigences ({len(ao.context.exigences)})")

    if ao.context.exigences:
        # Grouper par catégorie
        categories = {}
        for exig in ao.context.exigences:
            if exig.categorie not in categories:
                categories[exig.categorie] = []
            categories[exig.categorie].append(exig)

        for cat, exigs in categories.items():
            with st.expander(f"{cat.capitalize()} ({len(exigs)} exigences)"):
                for exig in exigs:
                    priority_emoji = "🔴" if exig.priorite == "obligatoire" else \
                                   "🟡" if exig.priorite == "souhaitable" else "🟢"
                    st.write(f"{priority_emoji} {exig.description}")

    # Questions
    if ao.context.questions:
        st.subheader(f"Questions ({len(ao.context.questions)})")
        for q in ao.context.questions:
            with st.expander(f"Q{q.id}: {q.section}"):
                st.write(q.question)
                if q.points:
                    st.caption(f"Points: {q.points}")

    # Red flags contexte
    if ao.context.red_flags:
        st.subheader("Red Flags Identifiés")
        for flag in ao.context.red_flags:
            flag_emoji = "🚨" if flag.bloquant else "⚠️"
            st.write(f"{flag_emoji} **{flag.type}**: {flag.description}")


def display_evidences_tab(ao):
    """Affiche l'onglet preuves REG"""
    st.subheader(f"Preuves REG Trouvées ({len(ao.evidences_reg)})")

    if not ao.evidences_reg:
        st.info("Aucune preuve REG trouvée")
        return

    for i, evidence in enumerate(ao.evidences_reg, start=1):
        with st.expander(f"Preuve {i}: {evidence.document_name} (similarité: {evidence.similarity_score:.2f})"):
            st.write(evidence.chunk_text)
            st.caption(f"Source: {evidence.document_id}")


def display_livrables_tab(ao):
    """Affiche l'onglet livrables"""
    st.subheader("Génération de Livrables")

    if not ao.scoring:
        st.warning("Scoring non disponible")
        return

    doc_gen = DocumentGenerator()

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Rapport No-Go")
        if ao.scoring.decision == DecisionType.NO_GO:
            format_nogo = st.radio("Format", ["PDF", "Word"], key="format_nogo")

            if st.button("📄 Générer Rapport No-Go"):
                with st.spinner("Génération en cours..."):
                    output_path = doc_gen.generate_no_go_report(
                        ao.context,
                        ao.scoring,
                        output_format="pdf" if format_nogo == "PDF" else "docx"
                    )
                    st.success(f"✅ Rapport généré: {output_path.name}")

                    # Téléchargement
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Télécharger",
                            data=f,
                            file_name=output_path.name,
                            mime="application/pdf" if format_nogo == "PDF" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
        else:
            st.info("Disponible uniquement pour les décisions No-Go")

    with col2:
        st.write("### Dossier Go")
        if ao.scoring.decision in [DecisionType.GO, DecisionType.GO_RESERVE]:
            format_go = st.radio("Format", ["Word", "PDF"], key="format_go")

            if st.button("📦 Générer Dossier Go"):
                with st.spinner("Génération en cours..."):
                    output_path = doc_gen.generate_go_package(
                        ao.context,
                        ao.scoring,
                        ao.evidences_reg,
                        output_format="docx" if format_go == "Word" else "pdf"
                    )
                    st.success(f"✅ Dossier généré: {output_path.name}")

                    # Téléchargement
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Télécharger",
                            data=f,
                            file_name=output_path.name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if format_go == "Word" else "application/pdf"
                        )
        else:
            st.info("Disponible uniquement pour les décisions Go et Go sous réserve")


def sidebar():
    """Barre latérale"""
    with st.sidebar:
        st.title("POC AO Scoring")
        st.markdown("---")

        st.header("📤 Uploader un AO")
        uploaded_file = st.file_uploader(
            "Sélectionner un PDF",
            type=['pdf'],
            help="Uploadez un dossier d'appel d'offres (CCTP, RC, etc.)"
        )

        if uploaded_file:
            if st.button("🚀 Analyser"):
                ao = analyze_ao(uploaded_file)
                if ao:
                    st.success("✅ Analyse terminée!")
                    st.rerun()

        st.markdown("---")

        # Stats REG
        if st.session_state.reg_manager:
            st.header("📚 Base REG")
            stats = st.session_state.reg_manager.get_collection_stats()
            st.metric("Documents indexés", stats.get('count', 0))

            if st.button("🔄 Réindexer REG"):
                with st.spinner("Réindexation en cours..."):
                    st.session_state.reg_manager.index_documents(force_reindex=True)
                    st.success("✅ Réindexation terminée")
                    st.rerun()

        st.markdown("---")

        # Stats AO
        st.header("📊 Statistiques")
        st.metric("AO analysés", len(st.session_state.ao_list))

        if st.session_state.ao_list:
            decisions = {}
            for ao in st.session_state.ao_list:
                if ao.scoring:
                    dec = ao.scoring.decision.value
                    decisions[dec] = decisions.get(dec, 0) + 1

            for dec, count in decisions.items():
                st.write(f"**{dec}**: {count}")


def main():
    """Fonction principale"""
    init_session_state()
    initialize_components()

    sidebar()

    # Affichage principal
    if st.session_state.current_ao:
        display_ao_detail()
    else:
        display_ao_list()


if __name__ == "__main__":
    main()
