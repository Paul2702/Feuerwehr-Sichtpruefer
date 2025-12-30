# - Erstellen aus einer Prüfanweisung
# - Ergebnisse erfassen
# - Speichern als PDF
# - Prüferdaten übernehmen

import logging
from typing import TYPE_CHECKING, Optional
from src.gui.pages import Page
from src.models.sichtpruefung import Sichtpruefung
from src.pdfGenerator import PdfGenerator
from ui.ui_main import Ui_MainWindow

if TYPE_CHECKING:
    from src.logic.state import AppState

logger = logging.getLogger(__name__)


class SichtpruefungManager:
    def __init__(self, ui: Ui_MainWindow, app_state: "AppState") -> None:
        self.ui: Ui_MainWindow = ui
        self.app_state: "AppState" = app_state
        self.sichtpruefung: Optional[Sichtpruefung] = None
        self.pdfPfad: str = ""

        self.speicherbareSeitenInhalte: dict[Page, callable] = {
            Page.SICHTPRUEFUNG_EIGENSCHAFT: self.speichereSichtpruefungEigenschaft,
            Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG: self.speichereSichtpruefungZusammenfassung
        }
    
    def speichereSeiteninhalte(self, page: Page) -> None:
        if page in self.speicherbareSeitenInhalte:
            self.speicherbareSeitenInhalte[page]()

    def speichereSichtpruefungEigenschaft(self) -> None:
        logger.debug(f"Speichere Sichtprüfung-Eigenschaft (Index: {self.app_state.aktuelleEigenschaftIndex})")
        keinHandlungsbedarf = self.ui.eigenschaftHandlungsbedarf.isChecked()
        massnahmen = self.ui.eigenschaftMassnahmenEingeben.text().strip()
        logger.debug(f"Ergebnis: keinHandlungsbedarf={keinHandlungsbedarf}, massnahmen={massnahmen[:50] if massnahmen else 'keine'}...")
        if self.sichtpruefung is None:
            raise ValueError("Sichtpruefung wurde nicht initialisiert")
        self.sichtpruefung.pruefErgebnisEinfuegen(self.app_state.aktuelleEigenschaftIndex, keinHandlungsbedarf, massnahmen)
        self.app_state.aktuelleEigenschaftIndex += 1
        logger.info(f"Eigenschaft gespeichert, Index erhöht auf: {self.app_state.aktuelleEigenschaftIndex}")

    def speichereSichtpruefungZusammenfassung(self) -> None:
        logger.info("Speichere Sichtprüfung-Zusammenfassung")
        lagerort = self.ui.zusammenfassungPruefobjektStammdatenLagerortEingeben.text().strip()
        nummer = self.ui.zusammenfassungPruefobjektStammdatenNummerEingeben.text().strip()
        einsatzbereit = self.ui.zusammenfassungEinsatzbereitJa.isChecked()
        pruefer = self.ui.zusammenfassungSignaturPrueferEingeben.text().strip()
        datum = self.ui.zusammenfassungSignaturDatumEingeben.text().strip()
        # TODO self.sichtpruefung mittels Daten aus Zusammmenfassung aktualisieren
        bemerkungen = self.ui.zusammenfassungEinsatzbereitBemerkungenEingeben.toPlainText().strip()
        
        logger.debug(f"Zusammenfassung: lagerort={lagerort}, nummer={nummer}, einsatzbereit={einsatzbereit}, pruefer={pruefer}, datum={datum}")
        
        if self.sichtpruefung is None:
            raise ValueError("Sichtpruefung wurde nicht initialisiert")
        self.sichtpruefung.finalesErgebnisEinfuegen(lagerort, nummer, einsatzbereit, pruefer, datum, bemerkungen)
        logger.info(f"Erstelle PDF: {self.pdfPfad}")
        try:
            PdfGenerator().erstelle_pdf(self.pdfPfad, self.sichtpruefung)
            logger.info(f"PDF erfolgreich erstellt: {self.pdfPfad}")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des PDFs: {e}", exc_info=True)
            raise

        