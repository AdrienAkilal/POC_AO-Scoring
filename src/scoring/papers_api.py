"""API Papers simulée pour récupérer le profil entreprise"""
import json
import logging
from pathlib import Path
from typing import Optional

from ..models import ProfilEntreprise
from ..config import PAPERS_MOCK_DIR

logger = logging.getLogger(__name__)


class PapersAPI:
    """Simulateur de l'API Papers pour le POC"""

    def __init__(self, mock_data_file: Optional[Path] = None):
        """
        Initialise l'API Papers simulée

        Args:
            mock_data_file: Fichier JSON contenant les données simulées
        """
        if mock_data_file is None:
            mock_data_file = PAPERS_MOCK_DIR / "profil_entreprise.json"

        self.mock_data_file = mock_data_file
        self.profil = self._load_mock_data()

    def _load_mock_data(self) -> Optional[ProfilEntreprise]:
        """Charge les données simulées depuis le fichier JSON"""
        try:
            if self.mock_data_file.exists():
                with open(self.mock_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profil = ProfilEntreprise(**data)
                    logger.info(f"Profil entreprise chargé: {profil.nom}")
                    return profil
            else:
                logger.warning(f"Fichier mock non trouvé: {self.mock_data_file}")
                return self._get_default_profil()
        except Exception as e:
            logger.error(f"Erreur chargement profil: {e}")
            return self._get_default_profil()

    def _get_default_profil(self) -> ProfilEntreprise:
        """Retourne un profil par défaut"""
        return ProfilEntreprise(
            nom="LogiSoft Solutions",
            effectif=85,
            chiffre_affaires=12500000.0,
            certifications=["ISO 9001", "ISO 27001"],
            references_clients=[
                {
                    "nom": "Carrefour Supply Chain",
                    "secteur": "Grande distribution",
                    "annee": 2023,
                    "solution": "WMS",
                    "budget": 450000
                },
                {
                    "nom": "Renault Logistics",
                    "secteur": "Automobile",
                    "annee": 2022,
                    "solution": "TMS",
                    "budget": 380000
                }
            ],
            projets_realises=[
                {
                    "titre": "Déploiement WMS multi-sites",
                    "client": "Carrefour Supply Chain",
                    "duree_mois": 12,
                    "succes": True
                },
                {
                    "titre": "Intégration TMS avec ERP SAP",
                    "client": "Renault Logistics",
                    "duree_mois": 8,
                    "succes": True
                }
            ],
            competences=[
                "WMS (Warehouse Management System)",
                "TMS (Transport Management System)",
                "ERP Logistique",
                "Traçabilité RFID",
                "Intégration EDI",
                "API REST",
                "Cloud AWS/Azure"
            ]
        )

    def get_profil_entreprise(self) -> ProfilEntreprise:
        """
        Récupère le profil entreprise

        Returns:
            ProfilEntreprise
        """
        if self.profil:
            return self.profil
        else:
            return self._get_default_profil()

    def has_certification(self, certification: str) -> bool:
        """
        Vérifie si l'entreprise possède une certification

        Args:
            certification: Nom de la certification

        Returns:
            True si la certification est détenue
        """
        profil = self.get_profil_entreprise()
        return any(cert.lower() == certification.lower() for cert in profil.certifications)

    def has_competence(self, competence: str) -> bool:
        """
        Vérifie si l'entreprise a une compétence

        Args:
            competence: Nom de la compétence

        Returns:
            True si la compétence existe
        """
        profil = self.get_profil_entreprise()
        competence_lower = competence.lower()
        return any(competence_lower in comp.lower() for comp in profil.competences)

    def get_similar_projects(self, secteur: Optional[str] = None, solution: Optional[str] = None) -> list:
        """
        Recherche des projets similaires

        Args:
            secteur: Secteur d'activité
            solution: Type de solution

        Returns:
            Liste de projets correspondants
        """
        profil = self.get_profil_entreprise()
        projets = profil.projets_realises

        if secteur or solution:
            filtered = []
            for projet in projets:
                match = True
                if secteur and projet.get("secteur", "").lower() != secteur.lower():
                    match = False
                if solution and solution.lower() not in projet.get("titre", "").lower():
                    match = False
                if match:
                    filtered.append(projet)
            return filtered

        return projets
