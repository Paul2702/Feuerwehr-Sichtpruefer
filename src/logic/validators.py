import logging
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QFileDialog, QMainWindow
from PySide6.QtCore import QObject
from src.gui.pages import Page
from src.logic.serializer import addToPruefanweisungenXml, speicherePruefanweisungXml
from src.logic.state import AppState
from src.pdfGenerator import PdfGenerator
from ui.ui_main import Ui_MainWindow

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ValidationController(QObject):
    def __init__(self, mainWindow: QMainWindow, ui: Ui_MainWindow, state: AppState) -> None:
        super().__init__()
        self.mainWindow: QMainWindow = mainWindow 
        self.ui: Ui_MainWindow = ui
        self.state: AppState = state
        # Dictionary mit Validierungsfunktionen pro Page
        self.fertigSeitenValidierungen: dict[Page, callable] = {
            Page.SICHTPRUEFUNG_PRUEFABLAUF: self.validiereFertigSichtpruefungPruefablauf,
            Page.SICHTPRUEFUNG_EIGENSCHAFT: self.validiereFertigSichtpruefungEigenschaft,
            Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG: self.validiereFertigSichtpruefungZusammenfassung,
            Page.PRUEFANWEISUNG_AUSWAHL: self.validiereFertigPruefanweisungAuswahl,
            Page.PRUEFANWEISUNG_PRUEFABLAUF: self.validiereFertigPruefanweisungPruefablauf,
            Page.PRUEFANWEISUNG_EIGENSCHAFT: self.validiereFertigPruefanweisungEigenschaft,
            Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG: self.validiereFertigPruefanweisungZusammenfassung
        }

    def istSeiteValide(self, page: Page) -> tuple[bool, str]:
        logger.debug(f"Validiere Seite: {page}")
        if page in self.fertigSeitenValidierungen:
            ist_valide, nachricht = self.fertigSeitenValidierungen[page]()
            if ist_valide:
                logger.debug(f"Seite {page} ist valide")
            else:
                logger.warning(f"Seite {page} ist nicht valide: {nachricht}")
            return ist_valide, nachricht
            
        logger.debug(f"Keine Validierung für Seite {page} definiert, akzeptiere als valide")
        return True, "" # TODO siehe goto in mainWindow

    # Sichtprüfung Prüfablauf
    def validiereFertigSichtpruefungPruefablauf(self) -> tuple[bool, str]:
        logger.debug("Validiere Sichtprüfung-Prüfablauf")
        self.state.aktuelleEigenschaftIndex = 0
        logger.debug("Eigenschaftsindex auf 0 zurückgesetzt")
        return True, ""
    
    # Sichtprüfung Eigenschaft
    def validiereFertigSichtpruefungEigenschaft(self) -> tuple[bool, str]:
        logger.debug("Validiere Sichtprüfung-Eigenschaft")
        keinHandlungsbedarf = self.ui.eigenschaftHandlungsbedarf.isChecked()
        massnahmen = self.ui.eigenschaftMassnahmenEingeben.text().strip()
        if not keinHandlungsbedarf and not massnahmen:
            logger.warning("Validierung fehlgeschlagen: Handlungsbedarf ohne Maßnahmen")
            return False, "Bitte eine Maßnahme eingeben, wenn es einen Handlungsbedarf gibt!"
        logger.debug(f"Validierung erfolgreich: keinHandlungsbedarf={keinHandlungsbedarf}")
        return True, ""
    
    # Sichtprüfung Zusammenfassung
    def validiereFertigSichtpruefungZusammenfassung(self) -> tuple[bool, str]:
        logger.debug("Validiere Sichtprüfung-Zusammenfassung")
        lagerort = self.ui.zusammenfassungPruefobjektStammdatenLagerortEingeben.text().strip()
        if not lagerort:
            logger.warning("Validierung fehlgeschlagen: Lagerort fehlt")
            return False, "Bitte den Lagerort des Prüfobjekts eingeben!"
        nummer = self.ui.zusammenfassungPruefobjektStammdatenNummerEingeben.text().strip()
        if not nummer:
            logger.warning("Validierung fehlgeschlagen: Nummer fehlt")
            return False, "Bitte die Nummer des Prüfobjekts eingeben!"
        einsatzbereit = self.ui.zusammenfassungEinsatzbereitJa.isChecked()
        nein = self.ui.zusammenfassungEinsatzbereitNein.isChecked()
        if not einsatzbereit and not nein:
            logger.warning("Validierung fehlgeschlagen: Einsatzbereitschaft nicht ausgewählt")
            return False, "Bitte auswählen, ob das Prüfobjekt einsatzbereit ist!"
        pruefer = self.ui.zusammenfassungSignaturPrueferEingeben.text().strip()
        if not pruefer:
            logger.warning("Validierung fehlgeschlagen: Prüfer fehlt")
            return False, "Bitte den Prüfer der Sichtprüfung eingeben!"
        datum = self.ui.zusammenfassungSignaturDatumEingeben.text().strip()
        if not datum:
            logger.warning("Validierung fehlgeschlagen: Datum fehlt")
            return False, "Bitte das Datum der Sichtprüfung eingeben!"
        
        if self.state.sichtpruefungManager.sichtpruefung is None:
            logger.error("Sichtpruefung wurde nicht initialisiert")
            return False, "Sichtprüfung wurde nicht korrekt geladen!"
        
        logger.debug("Öffne Dateidialog für PDF-Speicherung")
        self.state.sichtpruefungManager.pdfPfad, _ = QFileDialog.getSaveFileName(
            self.mainWindow, 
            "Datei speichern unter", 
            self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.namePruefobjekt, 
            "PDF-Dateien (*.pdf);;Alle Dateien (*)"
        )
        if not self.state.sichtpruefungManager.pdfPfad:
            logger.warning("PDF-Speicherung abgebrochen")
            return False, ""
        logger.info(f"PDF-Speicherpfad ausgewählt: {self.state.sichtpruefungManager.pdfPfad}")
        return True, ""
    
    # Prüfanweisung Auswahl
    def validiereFertigPruefanweisungAuswahl(self) -> tuple[bool, str]:
        if self.ui.auswahlBildEinfuegen.property("isPlaceholder"):
            return False, "Bitte ein Bild vom Prüfobjekt einfügen!"
        namePruefobjekt = self.ui.auswahlPruefobjektEingeben.text().strip()
        if not namePruefobjekt:
            return False, "Bitte eine Bezeichnung für das Prüfobjekt eingeben!"
        return True, ""

    # Prüfanweisung Prüfablauf
    def validiereFertigPruefanweisungPruefablauf(self) -> tuple[bool, str]:
        self.ui.hinzufuegen.setEnabled(True)
        self.ui.loeschen.setEnabled(True)
        return True, ""
    
    # Prüfanweisung Eigenschaft
    def validierePruefanweisungEigenschaft(self) -> tuple[bool, str]:
        kategorie: str = self.ui.eigenschaftEditorKategorieEingeben.text().strip()
        if not kategorie:
            return False, "Bitte einen Kategorienamen eingeben!"
        beschreibung: str = self.ui.eigenschaftEditorEigenschafteingeben.text().strip()
        if not beschreibung:
            return False, "Bitte die zu prüfende Eigenschaft eingeben!"
        return True, ""

    def validiereFertigPruefanweisungEigenschaft(self) -> tuple[bool, str]:
        # Das Bild zur Eigenschaft ist optional und wird nicht gecheckt
        istSeiteValide, statusNachricht = self.validierePruefanweisungEigenschaft()
        if istSeiteValide:
            self.ui.hinzufuegen.setEnabled(False)
            self.ui.loeschen.setEnabled(False)
            return True, ""
        return istSeiteValide, statusNachricht
        
    def validiereHinzufuegenPruefanweisungEigenschaft(self) -> tuple[bool, str]:
        istSeiteValide, statusNachricht = self.validierePruefanweisungEigenschaft()
        return istSeiteValide, statusNachricht

    # Prüfanweisung Zusammenfassung
    def validiereFertigPruefanweisungZusammenfassung(self) -> tuple[bool, str]:
        self.ui.fertig.setEnabled(False)
        self.ui.abbrechen.setEnabled(False)
        return True, ""