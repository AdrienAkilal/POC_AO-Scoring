"""Modèles de données Pydantic pour l'application"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DecisionType(str, Enum):
    """Type de décision pour un AO"""
    GO = "Go"
    GO_RESERVE = "Go sous réserve"
    NO_GO = "No-Go"


class AOStatus(str, Enum):
    """Statut de traitement d'un AO"""
    UPLOADED = "Téléchargé"
    PARSING = "En cours d'analyse"
    SCORED = "Scoré"
    DELIVERED = "Livré"


class Exigence(BaseModel):
    """Une exigence extraite du dossier AO"""
    id: str
    description: str
    categorie: str  # technique, fonctionnelle, juridique, etc.
    priorite: str  # obligatoire, souhaitable, optionnelle


class Question(BaseModel):
    """Une question extraite du dossier AO"""
    id: str
    question: str
    section: str
    points: Optional[int] = None


class RedFlag(BaseModel):
    """Un red flag identifié dans l'AO"""
    type: str
    description: str
    bloquant: bool


class AOContext(BaseModel):
    """Contexte extrait du dossier AO par le Parser NLP"""
    ao_id: str
    titre: str
    organisme: str
    resume: str
    date_limite: Optional[datetime] = None
    budget_indicatif: Optional[float] = None
    exigences: List[Exigence] = []
    questions: List[Question] = []
    criteres_evaluation: Dict[str, Any] = {}
    red_flags: List[RedFlag] = []
    metadata: Dict[str, Any] = {}


class EvidenceREG(BaseModel):
    """Une preuve REG correspondant à une exigence"""
    document_id: str
    document_name: str
    chunk_text: str
    similarity_score: float
    metadata: Dict[str, Any] = {}


class ScoreDetail(BaseModel):
    """Détail du score pour un critère"""
    critere: str
    score: float  # 0-100
    poids: float  # 0-1
    score_pondere: float
    justification: str
    evidences: List[str] = []


class ScoringResult(BaseModel):
    """Résultat complet du scoring"""
    ao_id: str
    score_global: float  # 0-100
    decision: DecisionType
    scores_details: List[ScoreDetail]
    red_flags_bloquants: List[RedFlag] = []
    points_a_clarifier: List[str] = []
    recommandations: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)


class ProfilEntreprise(BaseModel):
    """Profil entreprise depuis API Papers (simulé)"""
    nom: str
    effectif: int
    chiffre_affaires: float
    certifications: List[str] = []
    references_clients: List[Dict[str, Any]] = []
    projets_realises: List[Dict[str, Any]] = []
    competences: List[str] = []


class AOHistorique(BaseModel):
    """Un AO historique pour la similarité"""
    ao_id: str
    titre: str
    secteur: str
    decision: DecisionType
    score: float
    resultat: str  # gagné, perdu, abandonné
    similarite: Optional[float] = None


class AppelOffre(BaseModel):
    """Modèle complet d'un Appel d'Offres dans le système"""
    ao_id: str
    source_file: str
    status: AOStatus
    date_upload: datetime = Field(default_factory=datetime.now)
    context: Optional[AOContext] = None
    scoring: Optional[ScoringResult] = None
    evidences_reg: List[EvidenceREG] = []
    profil_entreprise: Optional[ProfilEntreprise] = None
    ao_similaires: List[AOHistorique] = []
