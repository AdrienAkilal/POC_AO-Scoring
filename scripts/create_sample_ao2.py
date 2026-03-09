"""Script pour créer un deuxième exemple d'appel d'offres (TMS)"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import AO_PDF_DIR

def create_sample_ao2():
    """Crée un deuxième exemple d'appel d'offres (TMS)"""

    output_path = AO_PDF_DIR / "AO_Exemple_TMS_Transport_2026.pdf"
    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#d32f2f'),
        spaceAfter=20,
        alignment=1
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=13,
        textColor=colors.HexColor('#d32f2f'),
        spaceAfter=10,
        spaceBefore=10
    )

    story = []

    # En-tête
    story.append(Paragraph("CONSULTATION", title_style))
    story.append(Paragraph("Solution TMS - Optimisation Transport National", heading1_style))
    story.append(Spacer(1, 0.5*cm))

    # Informations
    info_data = [
        ["Référence", "CONS-2026-TRANS-042"],
        ["Organisme", "LogiTrans France SAS"],
        ["Date limite", (datetime.now() + timedelta(days=25)).strftime("%d/%m/%Y à 17h00")],
        ["Budget estimé", "280 000 € HT"],
        ["Contact", "achats@logitrans.fr"]
    ]

    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ffebee')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))

    story.append(info_table)
    story.append(Spacer(1, 0.7*cm))

    # Contexte
    story.append(Paragraph("CONTEXTE", heading1_style))

    context = """
    LogiTrans France, entreprise de transport routier de marchandises opérant sur l'ensemble du territoire
    national avec une flotte de 150 véhicules, recherche une solution TMS (Transport Management System)
    pour optimiser la gestion de ses opérations de transport.

    L'objectif est de réduire les coûts de transport de 15% et d'améliorer la qualité de service grâce à
    une meilleure planification des tournées et un suivi en temps réel.
    """
    story.append(Paragraph(context, styles['BodyText']))
    story.append(Spacer(1, 0.4*cm))

    # Exigences principales
    story.append(Paragraph("EXIGENCES PRINCIPALES", heading1_style))

    exigences = [
        "Optimisation automatique des tournées (algorithmes VRP)",
        "Suivi GPS temps réel de la flotte (150 véhicules)",
        "Application mobile chauffeurs (Android obligatoire, iOS souhaitable)",
        "Interface avec notre ERP Microsoft Dynamics 365",
        "Gestion multi-transporteurs (sous-traitants)",
        "Calcul automatique des coûts de transport",
        "Tableau de bord KPI avec indicateurs de performance",
        "Gestion électronique des CMR et preuves de livraison",
        "Hébergement cloud en Europe avec SLA 99.9%",
        "Formation de 20 utilisateurs incluse"
    ]

    for i, exig in enumerate(exigences, 1):
        story.append(Paragraph(f"{i}. {exig}", styles['BodyText']))

    story.append(Spacer(1, 0.4*cm))

    # RED FLAGS / Contraintes
    story.append(Paragraph("CONTRAINTES IMPORTANTES", heading1_style))

    contraintes = """
    <b>ATTENTION :</b><br/>
    - Délai de mise en œuvre maximum : 4 mois<br/>
    - Intégration obligatoire avec Microsoft Dynamics 365 (API REST)<br/>
    - Solution doit être compatible avec nos trackers GPS existants (Geotab)<br/>
    - Données hébergées OBLIGATOIREMENT en Union Européenne<br/>
    - Conformité RGPD obligatoire avec DPO identifié<br/>
    - Support en français pendant heures ouvrées minimum
    """
    story.append(Paragraph(contraintes, styles['BodyText']))
    story.append(Spacer(1, 0.4*cm))

    # Questions
    story.append(Paragraph("QUESTIONS", heading1_style))

    questions = [
        "Quelle est votre expérience dans le secteur du transport routier de marchandises ?",
        "Décrivez le processus d'intégration avec Microsoft Dynamics 365.",
        "Quel est le délai de mise en œuvre réaliste pour notre périmètre ?",
        "Quels sont les coûts de maintenance annuels après la première année ?",
        "Proposez-vous un accompagnement au changement ? Si oui, à quel prix ?"
    ]

    for i, q in enumerate(questions, 1):
        story.append(Paragraph(f"<b>Q{i}:</b> {q}", styles['BodyText']))
        story.append(Spacer(1, 0.15*cm))

    story.append(Spacer(1, 0.4*cm))

    # Critères d'évaluation
    story.append(Paragraph("CRITÈRES D'ÉVALUATION", heading1_style))

    criteres = [
        ["Prix total (licence + déploiement)", "35%"],
        ["Fonctionnalités et ergonomie", "30%"],
        ["Expérience et références", "20%"],
        ["Qualité du support", "15%"]
    ]

    crit_table = Table(criteres, colWidths=[12*cm, 3*cm])
    crit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d32f2f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 0), (1, -1), 'CENTER')
    ]))

    story.append(crit_table)
    story.append(Spacer(1, 0.5*cm))

    # Modalités
    story.append(Paragraph("MODALITÉS DE RÉPONSE", heading1_style))

    modalites = f"""
    <b>Date limite :</b> {(datetime.now() + timedelta(days=25)).strftime("%d/%m/%Y à 17h00")}<br/>
    <b>Format :</b> Réponse par email à achats@logitrans.fr<br/>
    <b>Pièces requises :</b> Offre technique, offre financière, références clients, Kbis
    """
    story.append(Paragraph(modalites, styles['BodyText']))

    # Générer
    doc.build(story)
    print(f"PDF créé avec succès : {output_path}")
    return output_path

if __name__ == "__main__":
    create_sample_ao2()
