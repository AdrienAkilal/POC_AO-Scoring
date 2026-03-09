"""Moteur de scoring multi-critères pour les AO"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

from ..models import (
    AOContext, EvidenceREG, ProfilEntreprise, AOHistorique,
    ScoringResult, ScoreDetail, DecisionType, RedFlag
)
from ..config import (
    SCORING_WEIGHTS,
    SCORE_THRESHOLD_GO,
    SCORE_THRESHOLD_RESERVE,
    RED_FLAGS
)

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Moteur de scoring pour évaluer la pertinence d'un AO"""

    def __init__(
        self,
        weights: Dict[str, float] = SCORING_WEIGHTS,
        threshold_go: int = SCORE_THRESHOLD_GO,
        threshold_reserve: int = SCORE_THRESHOLD_RESERVE
    ):
        """
        Initialise le moteur de scoring

        Args:
            weights: Pondérations des critères
            threshold_go: Seuil pour décision Go
            threshold_reserve: Seuil pour décision Go sous réserve
        """
        self.weights = weights
        self.threshold_go = threshold_go
        self.threshold_reserve = threshold_reserve

    def score_ao(
        self,
        context: AOContext,
        evidences: List[EvidenceREG],
        profil: ProfilEntreprise,
        historique: List[AOHistorique]
    ) -> ScoringResult:
        """
        Calcule le score complet d'un AO

        Args:
            context: Contexte extrait de l'AO
            evidences: Preuves REG trouvées
            profil: Profil de l'entreprise
            historique: AO similaires historiques

        Returns:
            ScoringResult complet
        """
        logger.info(f"Calcul du score pour AO {context.ao_id}")

        # Vérifier les red flags bloquants
        red_flags_bloquants = self._check_red_flags(context, profil)

        # Si red flag bloquant, No-Go automatique
        if red_flags_bloquants:
            return self._create_no_go_result(context, red_flags_bloquants)

        # Calculer les scores par dimension
        scores_details = []

        # 1. Matching produit/service (30%)
        score_matching = self._score_matching_produit(context, evidences, profil)
        scores_details.append(ScoreDetail(
            critere="Matching produit/service",
            score=score_matching,
            poids=self.weights["matching_produit"],
            score_pondere=score_matching * self.weights["matching_produit"],
            justification=self._justify_matching(context, evidences),
            evidences=[e.document_name for e in evidences[:3]]
        ))

        # 2. Faisabilité (20%)
        score_faisabilite = self._score_faisabilite(context, profil)
        scores_details.append(ScoreDetail(
            critere="Faisabilité (délais/techno)",
            score=score_faisabilite,
            poids=self.weights["faisabilite"],
            score_pondere=score_faisabilite * self.weights["faisabilite"],
            justification=self._justify_faisabilite(context),
            evidences=[]
        ))

        # 3. Conformité (20%)
        score_conformite = self._score_conformite(context, profil)
        scores_details.append(ScoreDetail(
            critere="Conformité (RGPD/sécurité)",
            score=score_conformite,
            poids=self.weights["conformite"],
            score_pondere=score_conformite * self.weights["conformite"],
            justification=self._justify_conformite(context, profil),
            evidences=[]
        ))

        # 4. Similarité historique (15%)
        score_historique = self._score_historique(context, historique)
        scores_details.append(ScoreDetail(
            critere="Similarité historique",
            score=score_historique,
            poids=self.weights["similarite_historique"],
            score_pondere=score_historique * self.weights["similarite_historique"],
            justification=self._justify_historique(historique),
            evidences=[]
        ))

        # 5. Rentabilité (15%)
        score_rentabilite = self._score_rentabilite(context, profil)
        scores_details.append(ScoreDetail(
            critere="Rentabilité estimée",
            score=score_rentabilite,
            poids=self.weights["rentabilite"],
            score_pondere=score_rentabilite * self.weights["rentabilite"],
            justification=self._justify_rentabilite(context),
            evidences=[]
        ))

        # Calculer le score global
        score_global = sum(s.score_pondere for s in scores_details)

        # Déterminer la décision
        if score_global >= self.threshold_go:
            decision = DecisionType.GO
        elif score_global >= self.threshold_reserve:
            decision = DecisionType.GO_RESERVE
        else:
            decision = DecisionType.NO_GO

        # Identifier les points à clarifier (pour Go sous réserve)
        points_a_clarifier = self._identify_clarifications(context, evidences, scores_details)

        # Générer des recommandations
        recommandations = self._generate_recommendations(decision, scores_details, context)

        result = ScoringResult(
            ao_id=context.ao_id,
            score_global=round(score_global, 2),
            decision=decision,
            scores_details=scores_details,
            red_flags_bloquants=[],
            points_a_clarifier=points_a_clarifier,
            recommandations=recommandations
        )

        logger.info(f"Score calculé: {result.score_global}/100, Décision: {result.decision}")
        return result

    def _check_red_flags(self, context: AOContext, profil: ProfilEntreprise) -> List[RedFlag]:
        """Vérifie les red flags bloquants"""
        red_flags = []

        # Vérifier deadline
        if context.date_limite:
            days_left = (context.date_limite - datetime.now()).days
            if days_left < 0:
                red_flags.append(RedFlag(
                    type="deadline",
                    description="La deadline de l'AO est dépassée",
                    bloquant=True
                ))
            elif days_left < RED_FLAGS["deadline_days_min"]:
                red_flags.append(RedFlag(
                    type="deadline",
                    description=f"Délai très court: {days_left} jours seulement",
                    bloquant=True
                ))

        # Vérifier certifications dans les exigences
        for exig in context.exigences:
            for cert_required in RED_FLAGS["certifications_required"]:
                if cert_required.lower() in exig.description.lower():
                    if cert_required not in profil.certifications:
                        red_flags.append(RedFlag(
                            type="certification",
                            description=f"Certification {cert_required} requise mais non détenue",
                            bloquant=True
                        ))

        # Vérifier technologies incompatibles
        for exig in context.exigences:
            for tech in RED_FLAGS["technologies_incompatibles"]:
                if tech.lower() in exig.description.lower():
                    red_flags.append(RedFlag(
                        type="technologie",
                        description=f"Technologie incompatible requise: {tech}",
                        bloquant=True
                    ))

        # Ajouter les red flags du contexte qui sont bloquants
        for flag in context.red_flags:
            if flag.bloquant:
                red_flags.append(flag)

        return red_flags

    def _score_matching_produit(
        self,
        context: AOContext,
        evidences: List[EvidenceREG],
        profil: ProfilEntreprise
    ) -> float:
        """Score le matching produit/service (0-100)"""

        # Base: nombre d'exigences couvertes par le REG
        if context.exigences:
            coverage_ratio = min(len(evidences) / len(context.exigences), 1.0)
        else:
            coverage_ratio = 0.5

        # Bonus: qualité des matches (similarity scores)
        if evidences:
            avg_similarity = sum(e.similarity_score for e in evidences) / len(evidences)
        else:
            avg_similarity = 0.0

        # Bonus: compétences de l'entreprise
        competence_match = 0
        for exig in context.exigences:
            for comp in profil.competences:
                if comp.lower() in exig.description.lower():
                    competence_match += 1
                    break

        if context.exigences:
            competence_ratio = min(competence_match / len(context.exigences), 1.0)
        else:
            competence_ratio = 0.5

        # Score final (pondéré)
        score = (coverage_ratio * 40) + (avg_similarity * 30) + (competence_ratio * 30)
        return min(score, 100)

    def _score_faisabilite(self, context: AOContext, profil: ProfilEntreprise) -> float:
        """Score la faisabilité technique et calendaire (0-100)"""
        score = 70  # Base

        # Pénalité si délai court
        if context.date_limite:
            days_left = (context.date_limite - datetime.now()).days
            if days_left < 15:
                score -= 30
            elif days_left < 30:
                score -= 15

        # Pénalité si beaucoup d'exigences complexes
        if len(context.exigences) > 50:
            score -= 20
        elif len(context.exigences) > 30:
            score -= 10

        # Bonus si l'effectif est adapté
        if profil.effectif >= 50:
            score += 10

        return max(min(score, 100), 0)

    def _score_conformite(self, context: AOContext, profil: ProfilEntreprise) -> float:
        """Score la conformité réglementaire (0-100)"""
        score = 80  # Base élevée

        # Vérifier les certifications dans les exigences
        cert_count = 0
        cert_matched = 0

        for exig in context.exigences:
            # Chercher des mentions de certifications
            if any(keyword in exig.description.lower() for keyword in ["iso", "certifi", "rgpd", "gdpr"]):
                cert_count += 1
                # Vérifier si on a la certification
                for cert in profil.certifications:
                    if cert.lower() in exig.description.lower():
                        cert_matched += 1
                        break

        if cert_count > 0:
            cert_ratio = cert_matched / cert_count
            score = cert_ratio * 100

        return score

    def _score_historique(self, context: AOContext, historique: List[AOHistorique]) -> float:
        """Score basé sur l'historique d'AO similaires (0-100)"""
        if not historique:
            return 50  # Neutre si pas d'historique

        # Filtrer les AO pertinents (avec similarité si disponible)
        relevant_ao = [ao for ao in historique if ao.similarite and ao.similarite > 0.5]

        if not relevant_ao:
            return 50

        # Calculer le taux de succès
        gagnes = len([ao for ao in relevant_ao if ao.resultat == "gagné"])
        taux_succes = gagnes / len(relevant_ao)

        # Score moyen des AO similaires
        avg_score_historique = sum(ao.score for ao in relevant_ao) / len(relevant_ao)

        # Combiner les deux
        score = (taux_succes * 50) + (avg_score_historique * 0.5)
        return min(score, 100)

    def _score_rentabilite(self, context: AOContext, profil: ProfilEntreprise) -> float:
        """Score la rentabilité estimée (0-100)"""
        if not context.budget_indicatif:
            return 50  # Neutre si pas de budget

        budget = context.budget_indicatif

        # Estimation très simplifiée du coût (% du budget)
        if budget < 50000:
            return 20  # Trop petit
        elif budget < 100000:
            return 50
        elif budget < 300000:
            return 70
        elif budget < 500000:
            return 85
        else:
            return 95  # Très rentable

    def _justify_matching(self, context: AOContext, evidences: List[EvidenceREG]) -> str:
        """Génère la justification du score matching"""
        if not evidences:
            return "Aucune preuve REG trouvée pour les exigences de cet AO."

        return f"{len(evidences)} preuves REG identifiées couvrant {len(context.exigences)} exigences. " \
               f"Similarité moyenne: {sum(e.similarity_score for e in evidences) / len(evidences):.2f}"

    def _justify_faisabilite(self, context: AOContext) -> str:
        """Génère la justification du score faisabilité"""
        if context.date_limite:
            days_left = (context.date_limite - datetime.now()).days
            return f"Délai de réponse: {days_left} jours. " \
                   f"{len(context.exigences)} exigences à traiter."
        return f"{len(context.exigences)} exigences à traiter."

    def _justify_conformite(self, context: AOContext, profil: ProfilEntreprise) -> str:
        """Génère la justification du score conformité"""
        return f"Certifications détenues: {', '.join(profil.certifications)}. " \
               f"Analyse des exigences de conformité en cours."

    def _justify_historique(self, historique: List[AOHistorique]) -> str:
        """Génère la justification du score historique"""
        if not historique:
            return "Aucun AO similaire dans l'historique."

        gagnes = len([ao for ao in historique if ao.resultat == "gagné"])
        return f"{len(historique)} AO similaires dans l'historique, {gagnes} gagnés."

    def _justify_rentabilite(self, context: AOContext) -> str:
        """Génère la justification du score rentabilité"""
        if context.budget_indicatif:
            return f"Budget indicatif: {context.budget_indicatif:,.0f} €"
        return "Budget non communiqué dans le dossier AO."

    def _identify_clarifications(
        self,
        context: AOContext,
        evidences: List[EvidenceREG],
        scores: List[ScoreDetail]
    ) -> List[str]:
        """Identifie les points à clarifier pour un Go sous réserve"""
        points = []

        # Vérifier les scores faibles
        for score in scores:
            if score.score < 60:
                points.append(f"Clarifier {score.critere.lower()} (score: {score.score:.0f}/100)")

        # Vérifier les exigences sans preuve
        if len(evidences) < len(context.exigences) * 0.7:
            points.append("Certaines exigences ne sont pas couvertes par le REG actuel")

        # Vérifier budget
        if not context.budget_indicatif:
            points.append("Obtenir le budget indicatif de l'AO")

        return points

    def _generate_recommendations(
        self,
        decision: DecisionType,
        scores: List[ScoreDetail],
        context: AOContext
    ) -> List[str]:
        """Génère des recommandations basées sur le scoring"""
        reco = []

        if decision == DecisionType.GO:
            reco.append("Décision GO: Préparer le dossier de réponse complet")
            reco.append("Mobiliser les experts techniques pour les questions complexes")

            # Identifier le point fort
            best_score = max(scores, key=lambda s: s.score)
            reco.append(f"Point fort à valoriser: {best_score.critere}")

        elif decision == DecisionType.GO_RESERVE:
            reco.append("Décision GO sous réserve: Valider les points à clarifier avant engagement")

            # Identifier les faiblesses
            weak_scores = [s for s in scores if s.score < 60]
            if weak_scores:
                reco.append(f"Points faibles à renforcer: {', '.join(s.critere for s in weak_scores)}")

        else:  # NO_GO
            reco.append("Décision NO-GO: Ne pas répondre à cet AO")

            # Expliquer pourquoi
            worst_score = min(scores, key=lambda s: s.score)
            reco.append(f"Raison principale: {worst_score.critere} insuffisant ({worst_score.score:.0f}/100)")

        return reco

    def _create_no_go_result(self, context: AOContext, red_flags: List[RedFlag]) -> ScoringResult:
        """Crée un résultat No-Go automatique en cas de red flag bloquant"""
        return ScoringResult(
            ao_id=context.ao_id,
            score_global=0.0,
            decision=DecisionType.NO_GO,
            scores_details=[],
            red_flags_bloquants=red_flags,
            points_a_clarifier=[],
            recommandations=[
                "NO-GO automatique en raison de red flags bloquants",
                f"Red flags: {', '.join(f.description for f in red_flags)}"
            ]
        )
