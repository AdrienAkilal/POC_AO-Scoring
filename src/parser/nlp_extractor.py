"""Module d'extraction NLP simplifiée (sans OpenAI)"""
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

from ..models import AOContext, Exigence, Question, RedFlag

logger = logging.getLogger(__name__)


class NLPExtractor:
    """Extracteur NLP simplifié utilisant des patterns regex (sans OpenAI)"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialise l'extracteur NLP offline

        Args:
            api_key: Ignoré en mode offline
            model: Ignoré en mode offline
        """
        logger.info("Mode OFFLINE: Extraction basée sur des patterns (sans OpenAI)")

    def extract_context(self, text: str, ao_id: str, sections: Optional[Dict[str, str]] = None) -> AOContext:
        """
        Extrait le contexte structuré d'un dossier AO avec des patterns

        Args:
            text: Texte complet du dossier AO
            ao_id: Identifiant de l'AO
            sections: Sections pré-découpées du document (optionnel)

        Returns:
            AOContext structuré
        """
        logger.info(f"Extraction simplifiée pour AO {ao_id}")

        # Extraire titre et organisme
        titre = self._extract_title(text)
        organisme = self._extract_organization(text)

        # Résumé (premiers 500 caractères)
        resume = text[:500].strip() + "..."

        # Extraire date limite
        date_limite = self._extract_deadline(text)

        # Extraire budget
        budget = self._extract_budget(text)

        # Extraire exigences
        exigences = self._extract_requirements(text)

        # Extraire questions
        questions = self._extract_questions(text)

        # Détecter red flags
        red_flags = self._detect_red_flags(text, date_limite)

        context = AOContext(
            ao_id=ao_id,
            titre=titre,
            organisme=organisme,
            resume=resume,
            date_limite=date_limite,
            budget_indicatif=budget,
            exigences=exigences,
            questions=questions,
            criteres_evaluation={},
            red_flags=red_flags,
            metadata={"extraction_mode": "offline"}
        )

        logger.info(f"Extraction terminée: {len(exigences)} exigences, {len(questions)} questions")
        return context

    def _extract_title(self, text: str) -> str:
        """Extrait le titre de l'AO"""
        # Chercher des patterns de titre
        patterns = [
            r"(?:APPEL D'OFFRES?|CONSULTATION|MARCHÉ)\s*:?\s*(.{10,100})",
            r"(?:Objet|OBJET)\s*:?\s*(.{10,150})",
            r"^(.{10,100})\n",  # Première ligne
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                titre = match.group(1).strip()
                if len(titre) > 10:
                    return titre[:150]

        return "Appel d'Offres (titre non détecté)"

    def _extract_organization(self, text: str) -> str:
        """Extrait l'organisme émetteur"""
        patterns = [
            r"(?:Organisme|ORGANISME|Maître d'ouvrage|MAÎTRE D'OUVRAGE)\s*:?\s*(.{5,100})",
            r"(?:Pouvoir adjudicateur|POUVOIR ADJUDICATEUR)\s*:?\s*(.{5,100})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()[:100]

        return "Organisme non spécifié"

    def _extract_deadline(self, text: str) -> Optional[datetime]:
        """Extrait la date limite"""
        # Patterns de dates françaises
        date_patterns = [
            r"(?:date limite|deadline|avant le|jusqu'au)\s*:?\s*(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})",
            r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})\s*(?:à|avant)\s*(\d{1,2})h?(\d{2})?",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = int(match.group(3))

                    # Ajuster l'année si format court
                    if year < 100:
                        year += 2000

                    return datetime(year, month, day)
                except:
                    continue

        return None

    def _extract_budget(self, text: str) -> Optional[float]:
        """Extrait le budget indicatif"""
        patterns = [
            r"(?:budget|montant|prix)\s*(?:estimé|indicatif|maximum)?\s*:?\s*(\d[\d\s.,]*)\s*(?:€|euros?|EUR)",
            r"(\d[\d\s.,]+)\s*(?:€|euros?|EUR)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount_str = match.group(1).replace(' ', '').replace(',', '.')
                    amount = float(amount_str)
                    if 1000 <= amount <= 100000000:  # Montants réalistes
                        return amount
                except:
                    continue

        return None

    def _extract_requirements(self, text: str) -> List[Exigence]:
        """Extrait les exigences"""
        exigences = []

        # Chercher des listes numérotées ou à puces
        patterns = [
            r"(?:^|\n)\s*(?:\d+\.|[\-\*•])\s+(.{20,300})",
            r"(?:exigence|obligation|requis)\s*:?\s*(.{20,300})",
        ]

        exig_texts = set()  # Éviter les doublons

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                exig_text = match.group(1).strip()

                # Filtrer les exigences trop courtes ou déjà vues
                if len(exig_text) < 20 or exig_text in exig_texts:
                    continue

                exig_texts.add(exig_text)

                # Déterminer la catégorie (simple heuristique)
                if any(word in exig_text.lower() for word in ['technique', 'technologie', 'système', 'logiciel']):
                    categorie = "technique"
                elif any(word in exig_text.lower() for word in ['fonctionnelle', 'fonction', 'service']):
                    categorie = "fonctionnelle"
                elif any(word in exig_text.lower() for word in ['juridique', 'légal', 'contrat']):
                    categorie = "juridique"
                else:
                    categorie = "autre"

                # Déterminer la priorité
                if any(word in exig_text.lower() for word in ['obligatoire', 'impératif', 'doit', 'requis']):
                    priorite = "obligatoire"
                elif any(word in exig_text.lower() for word in ['souhaitable', 'recommandé', 'devrait']):
                    priorite = "souhaitable"
                else:
                    priorite = "obligatoire"  # Par défaut

                exigences.append(Exigence(
                    id=f"EXG-{len(exigences)+1:03d}",
                    description=exig_text[:500],
                    categorie=categorie,
                    priorite=priorite
                ))

                if len(exigences) >= 50:  # Limite
                    break

        logger.info(f"{len(exigences)} exigences extraites")
        return exigences

    def _extract_questions(self, text: str) -> List[Question]:
        """Extrait les questions"""
        questions = []

        # Chercher des questions (terminant par ?)
        pattern = r"(?:^|\n)\s*(?:\d+[\.\)]\s*)?(.{10,300}\?)"
        matches = re.finditer(pattern, text, re.MULTILINE)

        for match in matches:
            question_text = match.group(1).strip()

            questions.append(Question(
                id=f"Q-{len(questions)+1:03d}",
                question=question_text,
                section="Questions extraites",
                points=None
            ))

            if len(questions) >= 30:  # Limite
                break

        logger.info(f"{len(questions)} questions extraites")
        return questions

    def _detect_red_flags(self, text: str, date_limite: Optional[datetime]) -> List[RedFlag]:
        """Détecte les red flags"""
        red_flags = []

        # Red flag: deadline proche ou passée
        if date_limite:
            days_left = (date_limite - datetime.now()).days
            if days_left < 0:
                red_flags.append(RedFlag(
                    type="deadline",
                    description=f"Date limite dépassée ({date_limite.strftime('%d/%m/%Y')})",
                    bloquant=True
                ))
            elif days_left < 5:
                red_flags.append(RedFlag(
                    type="deadline",
                    description=f"Deadline très proche: {days_left} jours",
                    bloquant=True
                ))

        # Red flag: certifications
        cert_patterns = [
            r"(?:certification|certifié)\s+(?:obligatoire|requise?)\s*:?\s*(.{5,50})",
            r"ISO\s*\d+",
        ]

        for pattern in cert_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                red_flags.append(RedFlag(
                    type="certification",
                    description="Certifications spécifiques requises - à vérifier",
                    bloquant=False
                ))
                break

        # Red flag: technologies imposées
        tech_keywords = ['SAP', 'Oracle', 'Salesforce']
        for tech in tech_keywords:
            if re.search(rf'\b{tech}\b', text, re.IGNORECASE):
                red_flags.append(RedFlag(
                    type="technologie",
                    description=f"Technologie imposée: {tech}",
                    bloquant=False
                ))

        logger.info(f"{len(red_flags)} red flags détectés")
        return red_flags

    def extract_key_requirements(self, context: AOContext, max_requirements: int = 10) -> List[str]:
        """
        Extrait les exigences clés pour le RAG

        Args:
            context: Contexte AO
            max_requirements: Nombre maximum d'exigences à retourner

        Returns:
            Liste des descriptions d'exigences prioritaires
        """
        # Filtrer les exigences obligatoires
        obligatoires = [e for e in context.exigences if e.priorite == "obligatoire"]

        # Si pas assez, ajouter les souhaitables
        if len(obligatoires) < max_requirements:
            souhaitables = [e for e in context.exigences if e.priorite == "souhaitable"]
            obligatoires.extend(souhaitables[:max_requirements - len(obligatoires)])

        # Retourner les descriptions
        return [e.description for e in obligatoires[:max_requirements]]
