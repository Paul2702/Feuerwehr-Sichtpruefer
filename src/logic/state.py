from typing import Optional

from src.logic.serializer import addToPruefanweisungenXml, speicherePruefanweisungXml
from src.models.pruefanweisung import Pruefanweisung
from src.models.sichtpruefung import Sichtpruefung
from src.gui.pages import Page
from src.pdfGenerator import PdfGenerator
from ui.ui_main import Ui_MainWindow


class AppState:
    def __init__(self, ui: Ui_MainWindow):
        self.ui = ui

        self.aktuelleEigenschaftIndex = 0
        self.current_page = Page.HAUPTMENUE
        self.sichtpruefung: Optional[Sichtpruefung] = None
        self.pruefanweisung: Optional[Pruefanweisung] = None
        self.bearbeitungsmodus = False
        self.pdfPfad = ""

        self.speicherbareSeitenInhalte = {
            Page.SICHTPRUEFUNG_EIGENSCHAFT: self.speichereSichtpruefungEigenschaft,
            Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG: self.speichereSichtpruefungZusammenfassung,
            Page.PRUEFANWEISUNG_AUSWAHL: self.speicherePruefanweisungAuswahl,
            Page.PRUEFANWEISUNG_INFOS: self.speicherePruefanweisungInfos,
            Page.PRUEFANWEISUNG_VORGABEN: self.speicherePruefanweisungVorgaben,
            Page.PRUEFANWEISUNG_PRUEFABLAUF: self.speicherePruefanweisungPruefablauf,
            Page.PRUEFANWEISUNG_EIGENSCHAFT: self.speicherePruefanweisungEigenschaft,
            Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG: self.speicherePruefanweisungZusammenfassung
        }

    def set_current_page(self, page: Page):
        self.current_page = page

    def get_current_page(self) -> Page:
        return self.current_page
    
    def speichereSeiteninhalte(self, page: Page):
        if page in self.speicherbareSeitenInhalte:
            self.speicherbareSeitenInhalte[page]()

    def speichereSichtpruefungEigenschaft(self):
        keinHandlungsbedarf = self.ui.eigenschaftHandlungsbedarf.isChecked()
        massnahmen = self.ui.eigenschaftMassnahmenEingeben.text().strip()
        self.sichtpruefung.pruefErgebnisEinfuegen(self.aktuelleEigenschaftIndex, keinHandlungsbedarf, massnahmen)
        self.aktuelleEigenschaftIndex += 1

    def speichereSichtpruefungZusammenfassung(self):
        lagerort = self.ui.zusammenfassungPruefobjektStammdatenLagerortEingeben.text().strip()
        nummer = self.ui.zusammenfassungPruefobjektStammdatenNummerEingeben.text().strip()
        einsatzbereit = self.ui.zusammenfassungEinsatzbereitJa.isChecked()
        pruefer = self.ui.zusammenfassungSignaturPrueferEingeben.text().strip()
        datum = self.ui.zusammenfassungSignaturDatumEingeben.text().strip()
        # TODO self.sichtpruefung mittels Daten aus Zusammmenfassung aktualisieren
        bemerkungen = self.ui.zusammenfassungEinsatzbereitBemerkungenEingeben.toPlainText().strip()
        self.sichtpruefung.finalesErgebnisEinfuegen(lagerort, nummer, einsatzbereit, pruefer, datum, bemerkungen)
        PdfGenerator().erstelle_pdf(self.pdfPfad, self.sichtpruefung)

    def speicherePruefanweisungAuswahl(self):
        bildPfad = self.ui.auswahlBildEinfuegen.property("imagePath")
        namePruefobjekt = self.ui.auswahlPruefobjektEingeben.text().strip()
        self.pruefanweisung.auswahlHinzufuegen(bildPfad, namePruefobjekt)

    def speicherePruefanweisungInfos(self):
        pruefart = self.ui.pruefanweisungInfosPruefartEingeben.toPlainText().strip()
        pruefvorgabe = self.ui.pruefanweisungInfosPruefvorgabeEingeben.toPlainText().strip()
        pruefvorgabeZusatz = self.ui.pruefanweisungInfosPruefvorgabeZusatzEingeben.toPlainText().strip()
        prueffrist = self.ui.pruefanweisungInfosPrueffristEingeben.toPlainText().strip()
        sachkundiger = self.ui.pruefanweisungInfosSachkundigerEingeben.toPlainText().strip()
        zusatzausbildung = self.ui.pruefanweisungInfosZusatzausbildungEingeben.toPlainText().strip()
        hersteller = self.ui.pruefanweisungInfosHerstellerEingeben.toPlainText().strip()
        aussonderungsfrist = self.ui.pruefanweisungInfosAussonderungsfristEingeben.toPlainText().strip()
        self.pruefanweisung.infosHinzufuegen(pruefart, pruefvorgabe, pruefvorgabeZusatz, prueffrist, sachkundiger, zusatzausbildung, hersteller, aussonderungsfrist)

    def speicherePruefanweisungVorgaben(self):
        vorgaben = self.ui.vorgabenTextEingeben.toHtml()
        self.pruefanweisung.vorgabenHinzufuegen(vorgaben)

    def speicherePruefanweisungPruefablauf(self):
        pruefablauf = self.ui.pruefablaufTextEingeben.toHtml()
        self.pruefanweisung.pruefablaufHinzufuegen(pruefablauf)

    def speicherePruefanweisungEigenschaft(self):
        kategorie = self.ui.eigenschaftEditorKategorieEingeben.text().strip()
        beschreibung = self.ui.eigenschaftEditorEigenschafteingeben.text().strip()
        anzahlWidgets = self.ui.verticalLayout_11.count()
        bilder = []
        if anzahlWidgets > 1:
            for i in range(0, anzahlWidgets-2, 2):
                # Bild
                widget = self.ui.verticalLayout_11.itemAt(i).widget()
                bildPfad = widget.property('imagePath')
                # Beschreibung
                widget = self.ui.verticalLayout_11.itemAt(i+1).widget()
                bildBeschreibung = widget.toPlainText().strip()
                bilder.append((bildPfad, bildBeschreibung))

        self.pruefanweisung.eigenschaftHinzufuegen(kategorie, beschreibung, bilder)
        self.aktuelleEigenschaftIndex += 1

    def speicherePruefanweisungZusammenfassung(self):
        hinweis = self.ui.zusammenfassungHinweisEingeben.toPlainText().strip()
        self.pruefanweisung.hinweisHinzufuegen(hinweis)
        pruefanweisungXmlPfad = speicherePruefanweisungXml(self.pruefanweisung)
        addToPruefanweisungenXml(self.pruefanweisung, pruefanweisungXmlPfad)


