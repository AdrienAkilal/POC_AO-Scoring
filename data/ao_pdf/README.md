# 📄 Exemples d'Appels d'Offres pour Tests

Ce dossier contient des exemples d'appels d'offres créés pour tester le système de scoring.

## 📋 Fichiers Disponibles

### 1. AO_Exemple_WMS_2026.pdf
**Appel d'Offres - Solution WMS pour Plateforme Logistique**

- **Organisme**: Conseil Régional Île-de-France
- **Objet**: Déploiement d'un WMS pour plateforme de 15 000 m²
- **Budget**: 450 000 € TTC
- **Délai de réponse**: 45 jours
- **Complexité**: Moyenne-Élevée
- **Score attendu**: ~75-80/100 (devrait être **GO**)

**Caractéristiques**:
- 10 exigences fonctionnelles obligatoires
- 10 exigences techniques obligatoires
- Certification ISO 27001 obligatoire
- Intégration SAP requise
- 8 questions à répondre

### 2. AO_Exemple_TMS_Transport_2026.pdf
**Consultation - Solution TMS pour Transport National**

- **Organisme**: LogiTrans France SAS (entreprise privée)
- **Objet**: TMS pour optimisation de flotte de 150 véhicules
- **Budget**: 280 000 € HT
- **Délai de réponse**: 25 jours ⚠️ (COURT)
- **Complexité**: Moyenne
- **Score attendu**: ~65-70/100 (devrait être **GO sous réserve** ou **GO**)

**Caractéristiques**:
- Intégration Microsoft Dynamics 365 obligatoire
- Délai court (red flag potentiel)
- Compatibilité GPS Geotab requise
- 5 questions à répondre

## 🧪 Comment Tester

### Option 1: Via l'Interface Streamlit

1. Ouvrez l'application: `streamlit run src/ui/app.py`
2. Dans la sidebar, cliquez sur "📤 Uploader un AO"
3. Sélectionnez un des PDF ci-dessus
4. Cliquez sur "🚀 Analyser"
5. Consultez le score et les détails

### Option 2: Via le Script de Test

```bash
python scripts/test_pipeline.py
```

Ce script va automatiquement analyser le premier PDF trouvé dans ce dossier.

## 📊 Résultats Attendus

### Pour l'AO WMS (450k€, 45 jours)

**Score global attendu**: ~75-80/100

- ✅ **Matching produit**: ÉLEVÉ (WMS est notre cœur de métier)
- ✅ **Faisabilité**: BON (délai raisonnable de 45 jours)
- ✅ **Conformité**: EXCELLENT (ISO 27001 ok)
- ⚠️ **Historique**: MOYEN (dépend des données historiques)
- ✅ **Rentabilité**: BON (budget 450k€)

**Décision**: **GO** ✅

### Pour l'AO TMS (280k€, 25 jours)

**Score global attendu**: ~65-70/100

- ✅ **Matching produit**: BON (TMS disponible)
- ⚠️ **Faisabilité**: MOYEN (délai court = 25 jours)
- ✅ **Conformité**: BON (RGPD ok)
- ⚠️ **Historique**: MOYEN
- ⚠️ **Rentabilité**: MOYEN (budget plus modeste)

**Décision**: **GO sous réserve** ⚠️ (à cause du délai court)

**Points à clarifier**:
- Confirmer faisabilité du délai de 25 jours
- Vérifier compatibilité avec Microsoft Dynamics 365
- Valider intégration GPS Geotab

## 🎯 Ajouter Vos Propres AO

Pour tester avec vos vrais appels d'offres :

1. Placez vos PDF dans ce dossier (`data/ao_pdf/`)
2. Uploadez-les via l'interface Streamlit
3. Le système les analysera automatiquement

## 🔄 Régénérer les Exemples

Si vous voulez recréer les PDF avec de nouvelles dates :

```bash
python scripts/create_sample_ao.py
python scripts/create_sample_ao2.py
```

Les dates seront automatiquement ajustées par rapport à aujourd'hui.
