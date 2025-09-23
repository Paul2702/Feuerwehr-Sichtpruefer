from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QObject
from src.gui.pages import Page
from src.logic.serializer import addToPruefanweisungenXml, speicherePruefanweisungXml
from src.logic.state import AppState
from src.pdfGenerator import PdfGenerator
from ui.ui_main import Ui_MainWindow


class ValidationController(QObject):
    def __init__(self, mainWindow, ui: Ui_MainWindow, state: AppState):
        super().__init__(mainWindow)  # Parent-Objekt an QObject übergeben
        self.mainWindow = mainWindow 
        self.ui = ui
        self.state = state
        # Dictionary mit Validierungsfunktionen pro Page
        self.fertigSeitenValidierungen = {
            Page.SICHTPRUEFUNG_PRUEFABLAUF: self.validiereFertigSichtpruefungPruefablauf,
            Page.SICHTPRUEFUNG_EIGENSCHAFT: self.validiereFertigSichtpruefungEigenschaft,
            Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG: self.validiereFertigSichtpruefungZusammenfassung,
            Page.PRUEFANWEISUNG_AUSWAHL: self.validiereFertigPruefanweisungAuswahl,
            Page.PRUEFANWEISUNG_PRUEFABLAUF: self.validiereFertigPruefanweisungPruefablauf,
            Page.PRUEFANWEISUNG_EIGENSCHAFT: self.validiereFertigPruefanweisungEigenschaft,
            Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG: self.validiereFertigPruefanweisungZusammenfassung
        }

    def istSeiteValide(self, page: Page):
        if page in self.fertigSeitenValidierungen:
            return self.fertigSeitenValidierungen[page]()
            
        return True, "" # TODO siehe goto in mainWindow

    # Sichtprüfung Prüfablauf
    def validiereFertigSichtpruefungPruefablauf(self):
        self.state.aktuelleEigenschaftIndex = 0
        return True, ""
    
    # Sichtprüfung Eigenschaft
    def validiereFertigSichtpruefungEigenschaft(self):
        keinHandlungsbedarf = self.ui.eigenschaftHandlungsbedarf.isChecked()
        massnahmen = self.ui.eigenschaftMassnahmenEingeben.text().strip()
        if not keinHandlungsbedarf and not massnahmen:
            return False, "Bitte eine Maßnahme eingeben, wenn es einen Handlungsbedarf gibt!"
        return True, ""
    
    # Sichtprüfung Zusammenfassung
    def validiereFertigSichtpruefungZusammenfassung(self):
        lagerort = self.ui.zusammenfassungPruefobjektStammdatenLagerortEingeben.text().strip()
        if not lagerort:
            return False, "Bitte den Lagerort des Prüfobjekts eingeben!"
        nummer = self.ui.zusammenfassungPruefobjektStammdatenNummerEingeben.text().strip()
        if not nummer:
            return False, "Bitte die Nummer des Prüfobjekts eingeben!"
        einsatzbereit = self.ui.zusammenfassungEinsatzbereitJa.isChecked()
        nein = self.ui.zusammenfassungEinsatzbereitNein.isChecked()
        if not einsatzbereit and not nein:
            return False, "Bitte auswählen, ob das Prüfobjekt einsatzbereit ist!"
        pruefer = self.ui.zusammenfassungSignaturPrueferEingeben.text().strip()
        if not pruefer:
            return False, "Bitte den Prüfer der Sichtprüfung eingeben!"
        datum = self.ui.zusammenfassungSignaturDatumEingeben.text().strip()
        if not datum:
            return False, "Bitte das Datum der Sichtprüfung eingeben!"
        
        self.state.pdfPfad, _ = QFileDialog.getSaveFileName(self.mainWindow, "Datei speichern unter", self.state.sichtpruefung.pruefanweisung.namePruefobjekt, "PDF-Dateien (*.pdf);;Alle Dateien (*)")
        if not self.state.pdfPfad:
            return False, ""
        return True, ""
    
    # Prüfanweisung Auswahl
    def validiereFertigPruefanweisungAuswahl(self):
        if self.ui.auswahlBildEinfuegen.property("isPlaceholder"):
            return False, "Bitte ein Bild vom Prüfobjekt einfügen!"
        namePruefobjekt = self.ui.auswahlPruefobjektEingeben.text().strip()
        if not namePruefobjekt:
            return False, "Bitte eine Bezeichnung für das Prüfobjekt eingeben!"
        return True, ""

    # Prüfanweisung Prüfablauf
    def validiereFertigPruefanweisungPruefablauf(self):
        self.ui.hinzufuegen.setEnabled(True)
        self.ui.loeschen.setEnabled(True)
        return True, ""
    
    # Prüfanweisung Eigenschaft
    def validierePruefanweisungEigenschaft(self):
        kategorie = self.ui.eigenschaftEditorKategorieEingeben.text().strip()
        if not kategorie:
            return False, "Bitte einen Kategorienamen eingeben!"
        beschreibung = self.ui.eigenschaftEditorEigenschafteingeben.text().strip()
        if not beschreibung:
            return False, "Bitte die zu prüfende Eigenschaft eingeben!"
        return True, ""

    def validiereFertigPruefanweisungEigenschaft(self):
        # Das Bild zur Eigenschaft ist optional und wird nicht gecheckt
        istSeiteValide, statusNachricht = self.validierePruefanweisungEigenschaft()
        if istSeiteValide:
            self.ui.hinzufuegen.setEnabled(False)
            self.ui.loeschen.setEnabled(False)
            return True, ""
        return istSeiteValide, statusNachricht
        
    def validiereHinzufuegenPruefanweisungEigenschaft(self):
        istSeiteValide, statusNachricht = self.validierePruefanweisungEigenschaft()
        return istSeiteValide, statusNachricht

    # Prüfanweisung Zusammenfassung
    def validiereFertigPruefanweisungZusammenfassung(self):
        self.ui.fertig.setEnabled(False)
        self.ui.abbrechen.setEnabled(False)
        return True, ""