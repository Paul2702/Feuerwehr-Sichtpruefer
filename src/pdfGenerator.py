import os
import sys
import logging
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

from src.logic.serializer import eigenschaftspruefungenNachKategorienGruppieren
from src.models.pruefanweisung import Pruefanweisung
from src.models.sichtpruefung import Sichtpruefung
from src.util import cleanHtml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logger = logging.getLogger(__name__)


class PdfGenerator():
    def __init__(self):
        logger.debug("PdfGenerator wird initialisiert")
        # Seitenbreite und -höhe
        self.PAGE_WIDTH, self.PAGE_HEIGHT = A4
        self.logo_path = "assets/pdf_Feuerwehr_Logo.png"
        logger.debug(f"Logo-Pfad: {self.logo_path}")

        # SourceSans3-Schriftarten registrieren
        try:
            pdfmetrics.registerFont(TTFont("SourceSans3", "resources/fonts/Source_Sans_3/static/SourceSans3-Regular.ttf"))
            pdfmetrics.registerFont(TTFont("SourceSans3-SemiBold", "resources/fonts/Source_Sans_3/static/SourceSans3-SemiBold.ttf"))
            pdfmetrics.registerFont(TTFont("SourceSans3-SemiBold-Italic", "resources/fonts/Source_Sans_3/static/SourceSans3-SemiBoldItalic.ttf"))
            pdfmetrics.registerFont(TTFont("SourceSans3-Italic", "resources/fonts/Source_Sans_3/static/SourceSans3-Italic.ttf"))
            pdfmetrics.registerFont(TTFont("SourceSans3-Light", "resources/fonts/Source_Sans_3/static/SourceSans3-Light.ttf"))
            pdfmetrics.registerFont(TTFont("SourceSans3-Light-Italic", "resources/fonts/Source_Sans_3/static/SourceSans3-LightItalic.ttf"))
            logger.debug("Schriftarten erfolgreich registriert")
        except Exception as e:
            logger.error(f"Fehler beim Registrieren der Schriftarten: {e}", exc_info=True)
            raise
        
        pdfmetrics.registerFontFamily(
            "SourceSans3",
            normal="SourceSans3",
            bold="SourceSans3-SemiBold",
            italic="SourceSans3-Italic",
            boldItalic="SourceSans3-SemiBold-Italic"
        )

        self.checkboxJaX = 194.5
        self.checkboxNeinX = 246.5
        self.checkboxY = 654.4
        self.checkboxYPos = 0

        self.sichtpruefung = None
        self.pruefungenNachKategorienGruppiert = {}
        self.hinweisHoehe = 0
        self.bemerkungenHoehe = 0


    def erstelle_pdf(self, pdfPfad: str, sichtpruefung: Sichtpruefung) -> None:
        logger.info(f"Erstelle PDF: {pdfPfad}")
        logger.debug(f"Prüfobjekt: {sichtpruefung.pruefanweisung.namePruefobjekt}")
        
        self.checkboxYPos = self.checkboxY
        self.sichtpruefung = sichtpruefung
        self.pruefungenNachKategorienGruppiert = eigenschaftspruefungenNachKategorienGruppieren(self.sichtpruefung.eigenschaftspruefungen)
        logger.debug(f"Eigenschaftsprüfungen gruppiert in {len(self.pruefungenNachKategorienGruppiert)} Kategorien")
        
        doc = SimpleDocTemplate(pdfPfad, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        styles["Title"].fontName = "SourceSans3"
        styles["Heading2"].fontName = "SourceSans3"
        styles["Normal"].fontName = "SourceSans3-Light"

        # Titel "Prüfanweisung"
        elements.append(Spacer(1, 32))
        elements.append(Paragraph("Prüfanweisung", ParagraphStyle(name="RightAligned", textColor=HexColor("#4472C4"), fontSize=38, parent=styles["Title"], alignment=TA_RIGHT, rightIndent=-40)))
        elements.append(Spacer(1, 18))

        # Titel "Prüfobjekt Name"
        elements.append(Paragraph(f"<b>{self.sichtpruefung.pruefanweisung.namePruefobjekt}</b>", ParagraphStyle("RightAligned", textColor=HexColor("#4472C4"), fontSize=36, fontName="SourceSans3-Light", parent=styles["Title"], alignment=TA_RIGHT, rightIndent=-40)))
        elements.append(Spacer(1, 36.5))

        # Titel "Prüfobjekt Name"
        elements.append(Paragraph(f"<b>{self.sichtpruefung.pruefanweisung.pruefart}</b>", ParagraphStyle("RightAligned", textColor=HexColor("#575756"), fontSize=21, fontName="SourceSans3-SemiBold", parent=styles["Title"], alignment=TA_RIGHT, rightIndent=-40)))
        elements.append(Spacer(1, -2.5))

        # Titel "Prüfobjekt Name"
        elements.append(Paragraph(f"<b>gemäß {self.sichtpruefung.pruefanweisung.pruefvorgabe}</b>", ParagraphStyle("RightAligned", textColor=HexColor("#575756"), fontSize=21, fontName="SourceSans3-SemiBold", parent=styles["Title"], alignment=TA_RIGHT, rightIndent=-40)))

        # Prüfinformationen in einer Tabelle
        prueftabelle = [
            ["Prüfvorgabe", f"{self.sichtpruefung.pruefanweisung.pruefvorgabe or '-'} {self.sichtpruefung.pruefanweisung.pruefvorgabeZusatz or ''}"],
            ["Prüffrist", f"{self.sichtpruefung.pruefanweisung.prueffrist or '-'}"],
            ["Sachkundiger", f"{self.sichtpruefung.pruefanweisung.sachkundiger or '-'}"],
            [Paragraph("<b>Weitergehende Prüfungen</b><br/>(mit Zusatzausbildung)", ParagraphStyle(name="TableText", fontName="SourceSans3", fontSize=12, parent=styles["Normal"], alignment=TA_CENTER, leading=13)), f"{self.sichtpruefung.pruefanweisung.zusatzausbildung or '-'}"],
            [Paragraph("<b>Weitergehende Prüfungen</b><br/>(nur durch Hersteller)", ParagraphStyle(name="TableText", fontName="SourceSans3", fontSize=12, parent=styles["Normal"], alignment=TA_CENTER, leading=13)), f"{self.sichtpruefung.pruefanweisung.hersteller or '-'}"],
            ["Aussonderungsfrist", f"{self.sichtpruefung.pruefanweisung.aussonderungsfrist or '-'}"],
        ]

        tabelle = Table(prueftabelle, colWidths=[219.5, 249])
        tabelle.setStyle(TableStyle([
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (0, -1), "SourceSans3-SemiBold"),
            ("FONTNAME", (1, 0), (1, -1), "SourceSans3"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 4.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8.5),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ]))

        # Berechne, wie viel Platz über der Tabelle bleibt
        margin = 72
        titelTextFeldHoehe = 200
        _, tabellenHoehe = tabelle.wrap(0, 0)  # Bestimme die tatsächliche Größe der Tabelle
        spacerHoehe = self.PAGE_HEIGHT - margin - titelTextFeldHoehe - tabellenHoehe - margin - 13.5

        # Elemente für das PDF
        elements.append(Spacer(1, max(0, spacerHoehe)))  # Platzhalter dynamisch berechnen
        elements.append(tabelle)  # Tabelle unten einfügen

        elements.append(PageBreak())
        elements.append(Spacer(1, -7))

        # Vorgaben Abschnitt
        header = Table(
            [[Paragraph("Vorgaben", ParagraphStyle(name="BlauerTitel", textColor=HexColor("#FFFFFF"), fontName="SourceSans3-SemiBold", fontSize=20, parent=styles["Title"], alignment=TA_LEFT))]],  # Text in die Tabelle packen
            colWidths=[459]  # Hier die gewünschte Breite setzen
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#4472C4")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1.5),
            ("TOPPADDING", (0, 0), (-1, -1), -1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))

        elements.append(header)
        elements.append(Spacer(1, 18))
        elements.append(Paragraph(f"{cleanHtml(self.sichtpruefung.pruefanweisung.vorgabenText)}", styles["Normal"]))

        elements.append(PageBreak())
        elements.append(Spacer(1, -7))

        # Prüfablauf Abschnitt
        header = Table(
            [[Paragraph("Beschreibung des Prüfablaufs", ParagraphStyle(name="BlauerTitel", textColor=HexColor("#FFFFFF"), fontName="SourceSans3-SemiBold", fontSize=20, parent=styles["Title"], alignment=TA_LEFT))]],  # Text in die Tabelle packen
            colWidths=[459]  # Hier die gewünschte Breite setzen
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#4472C4")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1.5),
            ("TOPPADDING", (0, 0), (-1, -1), -1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))

        elements.append(header)
        elements.append(Spacer(1, 18))
        elements.append(Paragraph(f"{cleanHtml(self.sichtpruefung.pruefanweisung.pruefablaufText)}", styles["Normal"]))

        elements.append(PageBreak())
        elements.append(Spacer(1, -7))

        # Checkliste Tabelle
        header = Table(
            [[Paragraph("Checkliste", ParagraphStyle(name="BlauerTitel", textColor=HexColor("#FFFFFF"), fontName="SourceSans3-SemiBold", fontSize=20, parent=styles["Title"], alignment=TA_LEFT))]],  # Text in die Tabelle packen
            colWidths=[459]  # Hier die gewünschte Breite setzen
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#4472C4")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1.5),
            ("TOPPADDING", (0, 0), (-1, -1), -1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ]))

        elements.append(header)
        elements.append(Spacer(1, 19.5))

        header = Table(
            [[Paragraph(f"Prüfobjekt: {self.sichtpruefung.pruefanweisung.namePruefobjekt}", ParagraphStyle(name="BlauerTitel", textColor=HexColor("#FFFFFF"), fontName="SourceSans3-SemiBold", fontSize=16, parent=styles["Title"], alignment=TA_LEFT, leading=20.9))]],  # Text in die Tabelle packen
            colWidths=[482]
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#4472C4")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("TOPPADDING", (0, 0), (-1, -1), -0.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
        ]))
        
        _, nameHoehe = header.wrap(0, 0)
        self.checkboxYPos -= nameHoehe
        elements.append(header)

        header = Table(
            [[Paragraph(f"<b>Lagerort:</b> {self.sichtpruefung.lagerort}", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=16, parent=styles["Title"], alignment=TA_LEFT, leading=21)),
              Paragraph(f"<b>Nummer:</b> {self.sichtpruefung.nummer}", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=16, parent=styles["Title"], alignment=TA_LEFT, leading=21))]],  # Text in die Tabelle packen
            colWidths=[241, 241]  # Hier die gewünschte Breite setzen
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#FFFFFF")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("TOPPADDING", (0, 0), (-1, -1), -0.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
        ]))

        _, stammdatenHoehe = header.wrap(0, 0)
        self.checkboxYPos -= stammdatenHoehe
        elements.append(header)

        header = Table(
            [[Paragraph("Sichtprüfung", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=16, parent=styles["Title"], alignment=TA_CENTER))]],  # Text in die Tabelle packen
            colWidths=[482]
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#A1C0E4")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("TOPPADDING", (0, 0), (-1, -1), -1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), -1),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
        ]))

        elements.append(header)

        header = Table(
            [[Paragraph("√ = kein Handlungsbedarf", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=9, parent=styles["Title"], alignment=TA_RIGHT)),
             Paragraph("Maßnahmen festlegen", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=9, parent=styles["Title"], alignment=TA_LEFT))]],  # Text in die Tabelle packen
            colWidths=[283, 199]  # Hier die gewünschte Breite setzen
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#FFFFFF")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), -10),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
        ]))

        elements.append(header)

        header = Table(
            [[Paragraph("", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=12, parent=styles["Title"], alignment=TA_LEFT)),
             Paragraph("√", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=12, parent=styles["Title"], alignment=TA_CENTER)),
             Paragraph("Maßnahmen", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=12, parent=styles["Title"], alignment=TA_LEFT))]],  # Text in die Tabelle packen
            colWidths=[262, 21, 199]  # Hier die gewünschte Breite setzen
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#FFFFFF")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), -6.5),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
        ]))

        elements.append(header)

        for kategorie, pruefungen in self.pruefungenNachKategorienGruppiert.items():
            header = Table(
                [[Paragraph(f"{kategorie}", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=12, parent=styles["Title"], alignment=TA_LEFT, leading=16))]],  # Text in die Tabelle packen
                colWidths=[482]
            )

            header.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), HexColor("#A1C0E4")),  # Blauer Hintergrund
                ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
            ]))

            _, kategorieHoehe = header.wrap(0, 0)
            self.checkboxYPos -= kategorieHoehe
            elements.append(header)

            for pruefung in pruefungen:
                header = Table(
                    [[Paragraph(f"{pruefung.eigenschaft.beschreibung}", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=9, parent=styles["Title"], alignment=TA_LEFT, leading=11.5)),
                     Paragraph(f"{'√' if pruefung.keinHandlungsbedarf else ''}", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=9, parent=styles["Title"], alignment=TA_CENTER, leading=11.5)),
                     Paragraph(f"{pruefung.massnahmen}", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=9, parent=styles["Title"], alignment=TA_LEFT, leading=11.5))]],  # Text in die Tabelle packen
                    colWidths=[262, 21, 199]  # Hier die gewünschte Breite setzen
                )

                header.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), HexColor("#FFFFFF")),  # Blauer Hintergrund
                    ("VALIGN", (0, 0), (2, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
                ]))

                _, pruefungHoehe = header.wrap(0, 0)
                self.checkboxYPos -= pruefungHoehe
                elements.append(header)
        #elements.append(Spacer(1, 14))

        header = Table(
            [[Paragraph(f"<b>Hinweis:</b><br/>{self.sichtpruefung.pruefanweisung.hinweis}", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=9, parent=styles["Title"], alignment=TA_LEFT, leading=10.5))]],  # Text in die Tabelle packen
            colWidths=[482]
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#FFFFFF")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("TOPPADDING", (0, 0), (-1, -1), 0.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
        ]))

        _, hinweisHoehe = header.wrap(0, 0)
        self.checkboxYPos -= hinweisHoehe
        elements.append(header)

        header = Table(
            [[Paragraph("Einsatzbereit", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=12, parent=styles["Title"], alignment=TA_LEFT)),
             Paragraph("Ja", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=12, parent=styles["Title"], alignment=TA_LEFT)),
             Paragraph("Nein", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3-SemiBold", fontSize=12, parent=styles["Title"], alignment=TA_LEFT)),
             Paragraph(f"<b><u>Bemerkungen:</u></b><br/>{self.sichtpruefung.bemerkungen}", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=12, parent=styles["Title"], alignment=TA_LEFT, leading=13.5))]],  # Text in die Tabelle packen
            colWidths=[117, 40, 46, 279]  # Hier die gewünschte Breite setzen
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), HexColor("#A1C0E4")),  # Blauer Hintergrund
            ("BACKGROUND", (3, 0), (-1, -1), HexColor("#FFFFFF")),  # Blauer Hintergrund
            ("VALIGN", (0, 0), (2, -1), "MIDDLE"),
            ("VALIGN", (3, 0), (3, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("TOPPADDING", (0, 0), (2, -1), 14.5),
            ("BOTTOMPADDING", (0, 0), (2, -1), 8.5),
            ("TOPPADDING", (3, 0), (3, -1), 0),
            ("BOTTOMPADDING", (3, 0), (3, -1), 4.5),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
        ]))

        bemerkungenHoehe = 0
        _, wrap = header.wrap(0, 0)
        if wrap > 45:
            bemerkungenHoehe = (wrap - 45) / 2
        self.checkboxYPos -= bemerkungenHoehe
        elements.append(header)

        header = Table(
            [[Paragraph(f"<b>{self.sichtpruefung.pruefer}</b><br/>Prüfer", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=12, parent=styles["Title"], alignment=TA_LEFT, leading=25)),
             Paragraph(f"<b>{self.sichtpruefung.datum}</b><br/>Datum", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=12, parent=styles["Title"], alignment=TA_LEFT, leading=25)),
             Paragraph("Unterschrift", ParagraphStyle(name="BlauerTitel", fontName="SourceSans3", fontSize=12, parent=styles["Title"], alignment=TA_LEFT, leading=25))]],  # Text in die Tabelle packen
            colWidths=[188, 131, 163]  # Hier die gewünschte Breite setzen
        )

        header.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HexColor("#FFFFFF")),  # Blauer Hintergrund
            ("FONTNAME", (0, 0), (-1, -1), "SourceSans3-SemiBold"),
            ("TOPPADDING", (0, 0), (-1, -1), 18.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), -9.5),
            ("GRID", (0, 0), (-1, -1), 1, HexColor("#4472C4")),
        ]))

        elements.append(header)

        # PDF speichern
        try:
            logger.debug("Baue PDF-Dokument auf")
            doc.build(elements, onFirstPage=self.draw_header, onLaterPages=self.weitereDesignElementeHinzufuegen)
            logger.info(f"PDF erfolgreich erstellt: {pdfPfad}")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des PDFs: {e}", exc_info=True)
            raise

    def weitereDesignElementeHinzufuegen(self, canvas: canvas.Canvas, doc: SimpleDocTemplate) -> None:
        self.draw_header(canvas, doc)
        if self.sichtpruefung and doc.page == 4:  # Prüft, ob aktuelle Seite 3 ist
            self.draw_checkbox(canvas, self.checkboxJaX, self.checkboxYPos, checked=self.sichtpruefung.einsatzbereit)  # Checkbox in der Mitte
            self.draw_checkbox(canvas, self.checkboxNeinX, self.checkboxYPos, checked=not self.sichtpruefung.einsatzbereit)  # Checkbox in der Mitte

    def draw_header(self, canvas: canvas.Canvas, doc: SimpleDocTemplate) -> None:
        # Bildgröße (angepasst an dein gewünschtes Layout)
        logo_width = 181
        logo_height = 47.5

        # Berechnung für zentrierte Position
        logo_x = (self.PAGE_WIDTH - logo_width) / 2  # Zentriert auf der Seite
        logo_y = self.PAGE_HEIGHT - logo_height - 11  # Abstand vom oberen Rand
        canvas.drawImage(self.logo_path, logo_x, logo_y, width=logo_width, height=logo_height, mask="auto")

    def draw_checkbox(self, c: canvas.Canvas, x: float, y: float, size: float = 9.5, checked: bool = False) -> None:
        """Zeichnet eine Checkbox an Position (x, y)"""
        c.setLineWidth(0.8)
        c.rect(x, y, size, size, stroke=1, fill=0)  # Zeichne Quadrat (Checkbox)

        if checked:
            c.line(x + 2, y + 2, x + size - 2, y + size - 2)  # Erste Linie für Haken
            c.line(x + 2, y + size - 2, x + size - 2, y + 2)  # Zweite Linie für Haken

