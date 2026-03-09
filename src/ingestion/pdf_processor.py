"""Module d'extraction de texte depuis les PDF"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional
import logging
from PIL import Image
import io

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("Tesseract n'est pas disponible. L'OCR ne fonctionnera pas.")


logger = logging.getLogger(__name__)


class PDFProcessor:
    """Processeur pour extraire le texte des PDF (natif + OCR fallback)"""

    def __init__(self, use_ocr: bool = True):
        """
        Initialise le processeur PDF

        Args:
            use_ocr: Utiliser l'OCR (Tesseract) pour les PDF scannés
        """
        self.use_ocr = use_ocr and TESSERACT_AVAILABLE

    def extract_text(self, pdf_path: Path) -> Dict[str, any]:
        """
        Extrait le texte d'un PDF

        Args:
            pdf_path: Chemin vers le fichier PDF

        Returns:
            Dict contenant le texte extrait et les métadonnées
        """
        try:
            doc = fitz.open(str(pdf_path))

            full_text = []
            pages_data = []
            total_images = 0

            for page_num, page in enumerate(doc, start=1):
                # Extraction texte natif
                page_text = page.get_text()

                # Si le texte est vide ou presque, essayer l'OCR
                if self.use_ocr and len(page_text.strip()) < 50:
                    logger.info(f"Page {page_num} semble scannée, utilisation de l'OCR")
                    page_text = self._extract_with_ocr(page)

                full_text.append(page_text)

                # Compter les images
                images = page.get_images()
                total_images += len(images)

                pages_data.append({
                    "page_num": page_num,
                    "text_length": len(page_text),
                    "images_count": len(images)
                })

            metadata = doc.metadata or {}
            doc.close()

            result = {
                "text": "\n\n".join(full_text),
                "num_pages": len(full_text),
                "pages_data": pages_data,
                "total_images": total_images,
                "metadata": {
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "subject": metadata.get("subject", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": metadata.get("producer", ""),
                },
                "file_path": str(pdf_path),
                "file_size": pdf_path.stat().st_size
            }

            logger.info(f"PDF extrait: {pdf_path.name}, {result['num_pages']} pages, "
                       f"{len(result['text'])} caractères")

            return result

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du PDF {pdf_path}: {e}")
            raise

    def _extract_with_ocr(self, page) -> str:
        """
        Extrait le texte d'une page avec OCR (Tesseract)

        Args:
            page: Page PyMuPDF

        Returns:
            Texte extrait par OCR
        """
        if not TESSERACT_AVAILABLE:
            return ""

        try:
            # Convertir la page en image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom x2 pour meilleure qualité
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Appliquer l'OCR
            text = pytesseract.image_to_string(img, lang='fra')
            return text

        except Exception as e:
            logger.warning(f"Erreur OCR: {e}")
            return ""

    def extract_sections(self, text: str, section_markers: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Découpe le texte en sections basées sur des marqueurs

        Args:
            text: Texte complet du document
            section_markers: Liste de marqueurs de section (regex possibles)

        Returns:
            Dict {section_name: section_text}
        """
        if not section_markers:
            # Marqueurs par défaut pour les AO
            section_markers = [
                "CONTEXTE",
                "OBJET",
                "CONTRAINTES",
                "CRITÈRES",
                "CRITERES",
                "CALENDRIER",
                "DÉLAI",
                "DELAI",
                "EXIGENCES",
                "QUESTIONS"
            ]

        sections = {}
        current_section = "INTRODUCTION"
        current_text = []

        lines = text.split('\n')

        for line in lines:
            # Vérifier si la ligne contient un marqueur de section
            found_marker = None
            for marker in section_markers:
                if marker.upper() in line.upper():
                    found_marker = marker
                    break

            if found_marker:
                # Sauvegarder la section précédente
                if current_text:
                    sections[current_section] = '\n'.join(current_text)

                # Commencer nouvelle section
                current_section = found_marker.upper()
                current_text = [line]
            else:
                current_text.append(line)

        # Sauvegarder la dernière section
        if current_text:
            sections[current_section] = '\n'.join(current_text)

        return sections

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, any]]:
        """
        Découpe le texte en chunks pour le RAG

        Args:
            text: Texte à découper
            chunk_size: Taille approximative en tokens (on utilise des mots comme proxy)
            overlap: Nombre de mots de chevauchement entre chunks

        Returns:
            Liste de chunks avec métadonnées
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)

            chunks.append({
                "text": chunk_text,
                "chunk_index": len(chunks),
                "start_word": i,
                "end_word": i + len(chunk_words),
                "word_count": len(chunk_words)
            })

        logger.info(f"Texte découpé en {len(chunks)} chunks")
        return chunks
