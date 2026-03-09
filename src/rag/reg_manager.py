"""Gestionnaire du référentiel REG avec RAG (FAISS - Mode Offline sans OpenAI)"""
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from ..models import EvidenceREG
from ..config import (
    PDF_CHUNK_SIZE,
    PDF_CHUNK_OVERLAP,
    REG_DOCS_DIR
)
from ..ingestion import PDFProcessor

logger = logging.getLogger(__name__)


class REGManager:
    """Gestionnaire du référentiel interne REG avec recherche vectorielle (FAISS - Mode Offline)"""

    def __init__(self, persist_directory: str = None):
        """
        Initialise le gestionnaire REG en mode offline

        Args:
            persist_directory: Répertoire de persistence
        """
        if persist_directory is None:
            from ..config import CHROMA_PERSIST_DIRECTORY
            persist_directory = CHROMA_PERSIST_DIRECTORY

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.index_file = self.persist_directory / "faiss_index"

        logger.info("Initialisation des embeddings locaux (sentence-transformers)...")
        # Utiliser un modèle d'embeddings local français/multilingue
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logger.info("Embeddings locaux chargés avec succès")

        # Charger ou initialiser le vectorstore
        self.vectorstore = None
        self._load_vectorstore()

    def _load_vectorstore(self):
        """Charge le vectorstore depuis le disque"""
        if self.index_file.exists():
            try:
                self.vectorstore = FAISS.load_local(
                    str(self.persist_directory),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("Vectorstore FAISS chargé depuis le disque")
            except Exception as e:
                logger.warning(f"Impossible de charger le vectorstore: {e}")
                self.vectorstore = None
        else:
            logger.info("Aucun vectorstore trouvé, il sera créé lors de l'indexation")

    def index_documents(self, docs_directory: Path = REG_DOCS_DIR, force_reindex: bool = False):
        """
        Indexe les documents REG dans FAISS

        Args:
            docs_directory: Répertoire contenant les documents REG
            force_reindex: Forcer la réindexation même si des docs existent
        """
        # Vérifier si déjà indexé
        if self.vectorstore is not None and not force_reindex:
            logger.info("Vectorstore déjà chargé. Utiliser force_reindex=True pour réindexer.")
            return

        logger.info(f"Indexation des documents REG depuis {docs_directory}")

        # Lister les fichiers PDF et MD
        pdf_files = list(docs_directory.glob("*.pdf"))
        md_files = list(docs_directory.glob("*.md"))

        if not pdf_files and not md_files:
            logger.warning(f"Aucun document trouvé dans {docs_directory}")
            return

        all_chunks = []
        all_metadatas = []

        # Traiter les PDF
        pdf_processor = PDFProcessor(use_ocr=False)
        for pdf_file in pdf_files:
            try:
                logger.info(f"Traitement de {pdf_file.name}")
                result = pdf_processor.extract_text(pdf_file)
                chunks = self._split_text(result["text"], pdf_file.name)

                for chunk in chunks:
                    all_chunks.append(chunk["text"])
                    all_metadatas.append({
                        "source": pdf_file.name,
                        "type": "pdf",
                        "chunk_index": chunk["chunk_index"]
                    })
            except Exception as e:
                logger.error(f"Erreur traitement {pdf_file.name}: {e}")

        # Traiter les fichiers Markdown
        for md_file in md_files:
            try:
                logger.info(f"Traitement de {md_file.name}")
                with open(md_file, 'r', encoding='utf-8') as f:
                    text = f.read()

                chunks = self._split_text(text, md_file.name)

                for chunk in chunks:
                    all_chunks.append(chunk["text"])
                    all_metadatas.append({
                        "source": md_file.name,
                        "type": "markdown",
                        "chunk_index": chunk["chunk_index"]
                    })
            except Exception as e:
                logger.error(f"Erreur traitement {md_file.name}: {e}")

        # Indexer dans FAISS
        if all_chunks:
            logger.info(f"Indexation de {len(all_chunks)} chunks dans FAISS (cela peut prendre 1-2 minutes)...")

            # Créer le vectorstore
            self.vectorstore = FAISS.from_texts(
                texts=all_chunks,
                embedding=self.embeddings,
                metadatas=all_metadatas
            )

            # Sauvegarder
            self.vectorstore.save_local(str(self.persist_directory))
            logger.info(f"Indexation terminée: {len(all_chunks)} chunks sauvegardés")
        else:
            logger.warning("Aucun chunk à indexer")

    def _split_text(self, text: str, source_name: str) -> List[Dict]:
        """
        Découpe le texte en chunks

        Args:
            text: Texte à découper
            source_name: Nom du fichier source

        Returns:
            Liste de chunks avec métadonnées
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=PDF_CHUNK_SIZE,
            chunk_overlap=PDF_CHUNK_OVERLAP,
            length_function=len
        )

        chunks = splitter.split_text(text)

        return [
            {
                "text": chunk,
                "chunk_index": idx,
                "source": source_name
            }
            for idx, chunk in enumerate(chunks)
        ]

    def search_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[EvidenceREG]:
        """
        Recherche les chunks pertinents pour une requête

        Args:
            query: Requête de recherche
            top_k: Nombre de résultats à retourner
            filter_metadata: Filtres sur les métadonnées (non supporté par FAISS)

        Returns:
            Liste d'EvidenceREG
        """
        if not self.vectorstore:
            logger.warning("Vectorstore non initialisé")
            return []

        try:
            # Recherche avec similarité
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=top_k
            )

            evidences = []
            for doc, score in results:
                evidence = EvidenceREG(
                    document_id=doc.metadata.get("source", "unknown"),
                    document_name=doc.metadata.get("source", "unknown"),
                    chunk_text=doc.page_content,
                    similarity_score=float(1 / (1 + score)),  # Convertir distance en similarité
                    metadata=doc.metadata
                )
                evidences.append(evidence)

            logger.info(f"Recherche '{query[:50]}...': {len(evidences)} résultats")
            return evidences

        except Exception as e:
            logger.error(f"Erreur recherche RAG: {e}")
            return []

    def search_for_requirements(self, requirements: List[str], top_k_per_req: int = 3) -> List[EvidenceREG]:
        """
        Recherche des preuves REG pour une liste d'exigences

        Args:
            requirements: Liste d'exigences à matcher
            top_k_per_req: Nombre de résultats par exigence

        Returns:
            Liste consolidée d'EvidenceREG
        """
        all_evidences = []
        seen_chunks = set()

        for req in requirements:
            evidences = self.search_relevant_chunks(req, top_k=top_k_per_req)

            for evidence in evidences:
                # Éviter les doublons
                chunk_id = f"{evidence.document_id}_{evidence.metadata.get('chunk_index', 0)}"
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    all_evidences.append(evidence)

        logger.info(f"Recherche pour {len(requirements)} exigences: {len(all_evidences)} preuves trouvées")
        return all_evidences

    def get_collection_stats(self) -> Dict:
        """Retourne les statistiques de la collection"""
        try:
            if self.vectorstore is None:
                return {
                    "name": "faiss_index",
                    "count": 0,
                    "persist_directory": str(self.persist_directory)
                }

            # FAISS ne fournit pas directement le nombre de vecteurs
            # On estime à partir de l'index
            count = self.vectorstore.index.ntotal if hasattr(self.vectorstore, 'index') else 0

            return {
                "name": "faiss_index_offline",
                "count": count,
                "persist_directory": str(self.persist_directory),
                "mode": "offline (embeddings locaux)"
            }
        except Exception as e:
            logger.error(f"Erreur récupération stats: {e}")
            return {
                "name": "faiss_index_offline",
                "count": 0,
                "error": str(e)
            }
