"""Script pour créer un exemple d'appel d'offres en PDF"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import AO_PDF_DIR

def create_sample_ao():
    """Crée un exemple d'appel d'offres"""

    # Créer le fichier PDF
    output_path = AO_PDF_DIR / "AO_Exemple_WMS_2026.pdf"
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm)

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=20,
        alignment=1  # Center
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=12,
        spaceBefore=12
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#424242'),
        spaceAfter=10,
        spaceBefore=10
    )

    # Contenu du document
    story = []

    # En-tête
    story.append(Paragraph("RÉPUBLIQUE FRANÇAISE", styles['Normal']))
    story.append(Paragraph("Région Île-de-France", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # Titre
    story.append(Paragraph("APPEL D'OFFRES OUVERT", title_style))
    story.append(Paragraph("Solution WMS pour Plateforme Logistique Régionale", heading1_style))
    story.append(Spacer(1, 0.5*cm))

    # Informations administratives
    info_data = [
        ["Référence", "AO-2026-LOG-001"],
        ["Type de procédure", "Appel d'offres ouvert"],
        ["Date de publication", datetime.now().strftime("%d/%m/%Y")],
        ["Date limite de réponse", (datetime.now() + timedelta(days=45)).strftime("%d/%m/%Y à 16h00")],
        ["Pouvoir adjudicateur", "Conseil Régional Île-de-France"],
        ["Contact", "direction.achats@iledefrance.fr"]
    ]

    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))

    story.append(info_table)
    story.append(Spacer(1, 0.7*cm))

    # 1. CONTEXTE
    story.append(Paragraph("1. CONTEXTE ET OBJET", heading1_style))

    context_text = """
    La Région Île-de-France souhaite moderniser la gestion de sa plateforme logistique située à Évry-Courcouronnes
    (91). Cette plateforme centralisée de 15 000 m² gère la distribution de fournitures et équipements pour
    l'ensemble des lycées de la région (environ 470 établissements).

    Le système actuel, vieillissant et peu performant, nécessite un remplacement complet par une solution WMS
    (Warehouse Management System) moderne, intégrée et évolutive.
    """
    story.append(Paragraph(context_text, styles['BodyText']))
    story.append(Spacer(1, 0.3*cm))

    # Objet du marché
    story.append(Paragraph("Objet du marché:", heading2_style))
    objet_text = """
    Fourniture, déploiement et maintenance d'une solution WMS complète incluant :
    - Le logiciel WMS avec toutes ses fonctionnalités
    - L'infrastructure technique (serveurs, réseau, équipements mobiles)
    - La formation des utilisateurs
    - L'accompagnement au changement
    - La maintenance et le support pendant 5 ans
    """
    story.append(Paragraph(objet_text, styles['BodyText']))
    story.append(Spacer(1, 0.5*cm))

    # 2. CARACTÉRISTIQUES PRINCIPALES
    story.append(Paragraph("2. CARACTÉRISTIQUES PRINCIPALES", heading1_style))

    carac_text = """
    <b>Volume d'activité :</b><br/>
    - 25 000 références produits gérées<br/>
    - 150 000 mouvements par an<br/>
    - 50 utilisateurs simultanés<br/>
    - 2 000 livraisons par mois<br/>
    <br/>
    <b>Budget indicatif :</b> 450 000 € TTC<br/>
    <b>Durée du marché :</b> 5 ans (déploiement + maintenance)<br/>
    <b>Délai de mise en œuvre :</b> Maximum 6 mois après notification
    """
    story.append(Paragraph(carac_text, styles['BodyText']))
    story.append(Spacer(1, 0.5*cm))

    # 3. EXIGENCES TECHNIQUES
    story.append(Paragraph("3. EXIGENCES TECHNIQUES ET FONCTIONNELLES", heading1_style))

    story.append(Paragraph("3.1. Exigences fonctionnelles obligatoires", heading2_style))

    exigences_fonc = [
        "Gestion complète des réceptions avec contrôle qualité et génération d'étiquettes",
        "Optimisation des emplacements de stockage et gestion multi-zones",
        "Préparation de commandes assistée avec optimisation des parcours",
        "Gestion des inventaires permanents et tournants",
        "Traçabilité complète des lots et numéros de série",
        "Gestion FIFO/FEFO pour les produits avec date de péremption",
        "Interface avec le système ERP existant (SAP)",
        "Édition automatique des documents de transport (bons de livraison, étiquettes)",
        "Tableaux de bord et reporting en temps réel",
        "Application mobile pour les opérateurs (Android)"
    ]

    for i, exig in enumerate(exigences_fonc, 1):
        story.append(Paragraph(f"{i}. {exig}", styles['BodyText']))

    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3.2. Exigences techniques obligatoires", heading2_style))

    exigences_tech = [
        "Architecture cloud-native avec hébergement en France métropolitaine",
        "Disponibilité garantie minimum : 99.5%",
        "Temps de réponse moyen < 2 secondes",
        "Support de 50 utilisateurs simultanés minimum",
        "API REST documentée pour intégrations futures",
        "Sauvegarde quotidienne automatique avec rétention 30 jours",
        "Conformité RGPD et certification ISO 27001 de l'hébergeur",
        "Support de lecteurs code-barres et terminaux mobiles durcis",
        "Interface utilisateur en français",
        "Documentation technique et utilisateur en français"
    ]

    for i, exig in enumerate(exigences_tech, 1):
        story.append(Paragraph(f"{i}. {exig}", styles['BodyText']))

    story.append(PageBreak())

    # 4. EXIGENCES DE SÉCURITÉ ET CONFORMITÉ
    story.append(Paragraph("4. EXIGENCES DE SÉCURITÉ ET CONFORMITÉ", heading1_style))

    securite_text = """
    <b>Obligatoire :</b><br/>
    - Chiffrement des données en transit (TLS 1.3) et au repos (AES-256)<br/>
    - Authentification multi-facteurs (MFA) pour tous les utilisateurs<br/>
    - Gestion des droits d'accès par profil utilisateur<br/>
    - Logs d'audit complets et conservés 1 an minimum<br/>
    - Conformité RGPD avec registre des traitements<br/>
    - Certification ISO 27001 de l'hébergeur obligatoire<br/>
    - Plan de continuité d'activité (PCA) et plan de reprise d'activité (PRA)<br/>
    - Tests de sécurité (pentest) annuels<br/>
    <br/>
    <b>Souhaitable :</b><br/>
    - Certification ISO 9001 du prestataire<br/>
    - Référencement SecNumCloud de l'hébergeur
    """
    story.append(Paragraph(securite_text, styles['BodyText']))
    story.append(Spacer(1, 0.5*cm))

    # 5. QUESTIONS AUX CANDIDATS
    story.append(Paragraph("5. QUESTIONS AUX CANDIDATS", heading1_style))

    questions = [
        "Décrivez votre expérience dans le déploiement de solutions WMS pour des collectivités territoriales (minimum 3 références à fournir).",
        "Quel est le délai de mise en œuvre proposé de la solution complète ?",
        "Quelle est votre stratégie de formation et d'accompagnement au changement ?",
        "Décrivez votre plan de migration des données depuis le système actuel.",
        "Quels sont les niveaux de support proposés et les délais d'intervention garantis ?",
        "La solution propose-t-elle une extension pour la gestion du transport (TMS) ? Si oui, à quel coût ?",
        "Décrivez les évolutions fonctionnelles prévues dans votre roadmap produit sur les 3 prochaines années.",
        "Quelles sont les options de personnalisation disponibles sans développement spécifique ?"
    ]

    for i, question in enumerate(questions, 1):
        story.append(Paragraph(f"<b>Question {i} :</b> {question}", styles['BodyText']))
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.5*cm))

    # 6. CRITÈRES D'ÉVALUATION
    story.append(Paragraph("6. CRITÈRES D'ÉVALUATION", heading1_style))

    criteres_data = [
        ["Critère", "Pondération"],
        ["Prix", "30%"],
        ["Valeur technique de l'offre", "40%"],
        ["Capacité du candidat et références", "15%"],
        ["Qualité de l'accompagnement", "10%"],
        ["Performance énergétique", "5%"]
    ]

    criteres_table = Table(criteres_data, colWidths=[12*cm, 3*cm])
    criteres_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(criteres_table)
    story.append(Spacer(1, 0.5*cm))

    # 7. MODALITÉS DE RÉPONSE
    story.append(Paragraph("7. MODALITÉS DE RÉPONSE", heading1_style))

    modalites_text = f"""
    <b>Date limite de réponse :</b> {(datetime.now() + timedelta(days=45)).strftime("%d/%m/%Y à 16h00")}<br/>
    <br/>
    <b>Dossier à fournir :</b><br/>
    - DC1 et DC2 (lettre de candidature et déclaration du candidat)<br/>
    - DUME (Document Unique de Marché Européen)<br/>
    - Kbis de moins de 3 mois<br/>
    - Attestations fiscales et sociales<br/>
    - Références clients (minimum 3 projets similaires)<br/>
    - Mémoire technique répondant aux exigences du CCTP<br/>
    - Offre financière détaillée (décomposition du prix global et forfaitaire)<br/>
    - Planning prévisionnel de déploiement<br/>
    - Certifications ISO 27001 et ISO 9001 (si détenues)<br/>
    <br/>
    <b>Modalités de transmission :</b><br/>
    Les offres doivent être transmises exclusivement par voie dématérialisée sur la plateforme
    PLACE (https://www.place.marches-publics.gouv.fr) avant la date limite.<br/>
    <br/>
    <b>Renseignements complémentaires :</b><br/>
    Contact : direction.achats@iledefrance.fr<br/>
    Téléphone : 01 XX XX XX XX<br/>
    <br/>
    Une visite du site peut être organisée sur demande avant le {(datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")}.
    """
    story.append(Paragraph(modalites_text, styles['BodyText']))

    # Générer le PDF
    doc.build(story)

    print(f"PDF créé avec succès : {output_path}")
    return output_path

if __name__ == "__main__":
    create_sample_ao()
