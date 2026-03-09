"""Script d'initialisation de la base REG"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import REGManager
from src.config import REG_DOCS_DIR
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Initialise et indexe la base REG"""
    print("=" * 60)
    print("INITIALISATION DE LA BASE REG")
    print("=" * 60)
    print()

    # Vérifier que le dossier REG existe
    if not REG_DOCS_DIR.exists():
        logger.error(f"Le dossier REG n'existe pas: {REG_DOCS_DIR}")
        return

    # Lister les documents
    pdf_files = list(REG_DOCS_DIR.glob("*.pdf"))
    md_files = list(REG_DOCS_DIR.glob("*.md"))

    print(f"Documents trouvés dans {REG_DOCS_DIR}:")
    print(f"  - Fichiers PDF: {len(pdf_files)}")
    print(f"  - Fichiers Markdown: {len(md_files)}")
    print()

    if not pdf_files and not md_files:
        logger.warning("Aucun document trouvé dans le dossier REG!")
        logger.info("Ajoutez des documents PDF ou MD dans le dossier data/reg_docs/")
        return

    # Créer le REG Manager
    print("Initialisation du REG Manager...")
    reg_manager = REGManager()

    # Indexer les documents
    print("Indexation des documents...")
    print("(Cela peut prendre quelques minutes selon le nombre de documents)")
    print()

    try:
        reg_manager.index_documents(force_reindex=True)

        # Afficher les statistiques
        stats = reg_manager.get_collection_stats()

        print()
        print("=" * 60)
        print("INDEXATION TERMINÉE")
        print("=" * 60)
        print(f"Documents indexés: {stats.get('count', 0)}")
        print(f"Collection: {stats.get('name', 'N/A')}")
        print()

        # Test de recherche
        print("Test de recherche...")
        results = reg_manager.search_relevant_chunks("gestion d'entrepôt WMS", top_k=3)

        if results:
            print(f"✅ {len(results)} résultats trouvés pour 'gestion d'entrepôt WMS'")
            print()
            print("Exemple de résultat:")
            print(f"  - Document: {results[0].document_name}")
            print(f"  - Similarité: {results[0].similarity_score:.2f}")
            print(f"  - Extrait: {results[0].chunk_text[:200]}...")
        else:
            print("⚠️ Aucun résultat trouvé")

        print()
        print("✅ Initialisation terminée avec succès!")

    except Exception as e:
        logger.error(f"Erreur lors de l'indexation: {e}", exc_info=True)
        print()
        print("❌ Erreur lors de l'indexation. Vérifiez les logs ci-dessus.")


if __name__ == "__main__":
    main()
