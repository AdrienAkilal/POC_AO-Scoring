# Documentation REG - Référentiel Interne

Ce dossier contient la documentation interne de l'entreprise qui sera indexée dans la base vectorielle ChromaDB pour le système RAG.

## Documents Actuels

### Fiches Produits
- **REG_WMS_Fiche_Produit.md** - Solution de gestion d'entrepôt
- **REG_TMS_Fiche_Produit.md** - Solution de gestion de transport

### Documentation Technique et Conformité
- **REG_Securite_RGPD.md** - Politique de sécurité et conformité RGPD

## Ajouter de Nouveaux Documents

Pour enrichir le référentiel REG:

1. **Formats supportés**: PDF, Markdown (.md)

2. **Types de documents recommandés**:
   - Fiches produits détaillées
   - Architecture techniques
   - SLA (Service Level Agreements)
   - Conditions de sécurité
   - Certifications détaillées
   - Méthodologies de déploiement
   - Cas clients (anonymisés)
   - Procédures et processus

3. **Bonnes pratiques**:
   - Utiliser des titres clairs et hiérarchiques
   - Inclure des mots-clés pertinents
   - Structurer le contenu de manière logique
   - Ajouter des métadonnées (produit, domaine, version)

4. **Après l'ajout**:
   ```bash
   # Méthode 1: Via script
   python scripts/init_reg.py

   # Méthode 2: Via interface Streamlit
   # Cliquer sur "🔄 Réindexer REG" dans la sidebar
   ```

## Structure Recommandée d'un Document

```markdown
# [Titre du Document]

## Description Générale
[Vue d'ensemble du sujet]

## Fonctionnalités / Points Clés
- Point 1
- Point 2
- Point 3

## Caractéristiques Techniques
[Détails techniques]

## Conformité et Certifications
[Standards, normes, certifications]

## Déploiement
[Informations sur l'implémentation]

## Support et Maintenance
[Niveaux de support]

## Tarification
[Fourchettes de prix si applicable]
```

## Conseils pour une Bonne Couverture RAG

1. **Couvrir tous les aspects métier**: WMS, TMS, ERP, Traçabilité, etc.
2. **Détailler les capacités techniques**: APIs, intégrations, architectures
3. **Documenter la conformité**: RGPD, ISO, certifications sectorielles
4. **Inclure des cas d'usage**: Secteurs, tailles de projet, complexités
5. **Préciser les contraintes**: Délais, prérequis, limitations

Plus votre REG est riche et précis, meilleure sera la qualité des réponses automatiques aux exigences des AO !
