"""Script de test du pipeline complet"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import PDFProcessor
from src.parser import NLPExtractor
from src.rag import REGManager
from src.scoring import PapersAPI, ScoringEngine
from src.config import AO_PDF_DIR
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_pdf_extraction():
    """Test de l'extraction PDF"""
    print("\n=== TEST EXTRACTION PDF ===")

    processor = PDFProcessor(use_ocr=False)

    # Chercher un PDF de test
    pdf_files = list(AO_PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print("❌ Aucun PDF trouvé dans data/ao_pdf/")
        return None

    pdf_path = pdf_files[0]
    print(f"Test avec: {pdf_path.name}")

    try:
        result = processor.extract_text(pdf_path)
        print(f"✅ Extraction réussie:")
        print(f"   - Pages: {result['num_pages']}")
        print(f"   - Caractères: {len(result['text'])}")
        print(f"   - Images: {result['total_images']}")
        return result['text']
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def test_nlp_extraction(text):
    """Test de l'extraction NLP"""
    print("\n=== TEST EXTRACTION NLP ===")

    if not text:
        print("❌ Pas de texte à analyser")
        return None

    extractor = NLPExtractor()

    try:
        context = extractor.extract_context(text[:50000], "TEST_AO_001")  # Limiter pour le test
        print(f"✅ Extraction NLP réussie:")
        print(f"   - Titre: {context.titre}")
        print(f"   - Organisme: {context.organisme}")
        print(f"   - Exigences: {len(context.exigences)}")
        print(f"   - Questions: {len(context.questions)}")
        print(f"   - Red flags: {len(context.red_flags)}")
        return context
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error("NLP extraction error", exc_info=True)
        return None


def test_rag_search(context):
    """Test de la recherche RAG"""
    print("\n=== TEST RECHERCHE RAG ===")

    if not context or not context.exigences:
        print("❌ Pas de contexte ou d'exigences")
        return None

    try:
        reg_manager = REGManager()
        stats = reg_manager.get_collection_stats()

        print(f"Base REG: {stats.get('count', 0)} documents")

        if stats.get('count', 0) == 0:
            print("⚠️ Base REG vide. Exécutez scripts/init_reg.py d'abord")
            return None

        # Rechercher pour quelques exigences
        requirements = [e.description for e in context.exigences[:3]]
        evidences = reg_manager.search_for_requirements(requirements, top_k_per_req=2)

        print(f"✅ Recherche RAG réussie:")
        print(f"   - Exigences testées: {len(requirements)}")
        print(f"   - Preuves trouvées: {len(evidences)}")

        if evidences:
            print(f"   - Exemple: {evidences[0].document_name} (similarité: {evidences[0].similarity_score:.2f})")

        return evidences

    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error("RAG search error", exc_info=True)
        return None


def test_papers_api():
    """Test de l'API Papers"""
    print("\n=== TEST API PAPERS ===")

    try:
        api = PapersAPI()
        profil = api.get_profil_entreprise()

        print(f"✅ Profil entreprise récupéré:")
        print(f"   - Nom: {profil.nom}")
        print(f"   - Effectif: {profil.effectif}")
        print(f"   - Certifications: {len(profil.certifications)}")
        print(f"   - Références: {len(profil.references_clients)}")

        return profil

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def test_scoring(context, evidences, profil):
    """Test du scoring"""
    print("\n=== TEST SCORING ===")

    if not all([context, evidences is not None, profil]):
        print("❌ Données manquantes pour le scoring")
        return None

    try:
        engine = ScoringEngine()

        # Historique vide pour le test
        historique = []

        result = engine.score_ao(context, evidences or [], profil, historique)

        print(f"✅ Scoring calculé:")
        print(f"   - Score global: {result.score_global:.1f}/100")
        print(f"   - Décision: {result.decision.value}")
        print(f"   - Red flags bloquants: {len(result.red_flags_bloquants)}")
        print()
        print("   Détail par critère:")
        for detail in result.scores_details:
            print(f"     • {detail.critere}: {detail.score:.1f}/100")

        return result

    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error("Scoring error", exc_info=True)
        return None


def main():
    """Exécute tous les tests"""
    print("=" * 60)
    print("TEST DU PIPELINE COMPLET")
    print("=" * 60)

    # 1. Extraction PDF
    text = test_pdf_extraction()

    # 2. Extraction NLP
    context = test_nlp_extraction(text) if text else None

    # 3. Recherche RAG
    evidences = test_rag_search(context) if context else None

    # 4. API Papers
    profil = test_papers_api()

    # 5. Scoring
    scoring = test_scoring(context, evidences, profil) if context and profil else None

    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Extraction PDF:  {'✅' if text else '❌'}")
    print(f"Extraction NLP:  {'✅' if context else '❌'}")
    print(f"Recherche RAG:   {'✅' if evidences is not None else '❌'}")
    print(f"API Papers:      {'✅' if profil else '❌'}")
    print(f"Scoring:         {'✅' if scoring else '❌'}")
    print("=" * 60)

    if all([text, context, evidences is not None, profil, scoring]):
        print("\n🎉 Tous les tests sont passés avec succès!")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez les détails ci-dessus.")


if __name__ == "__main__":
    main()
