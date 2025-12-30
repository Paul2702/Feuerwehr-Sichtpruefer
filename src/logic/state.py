import logging
from typing import TYPE_CHECKING
from src.logic.pruefanweisungManager import PruefanweisungManager
from src.logic.sichtpruefungManager import SichtpruefungManager
from src.logic.vorgang import Vorgang
from src.gui.pages import Page
from ui.ui_main import Ui_MainWindow

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class AppState:
    def __init__(self, ui: Ui_MainWindow) -> None:
        logger.debug("AppState wird initialisiert")
        self.aktuelleEigenschaftIndex: int = 0
        self.current_page: Page = Page.HAUPTMENUE
        self.aktuellerVorgang: Vorgang = Vorgang.HAUPTMENUE
        logger.debug(f"Initialer Zustand: page={self.current_page}, vorgang={self.aktuellerVorgang}")
        
        # Manager nach aktuellerVorgang initialisieren, damit sie auf self zugreifen können
        self.sichtpruefungManager: SichtpruefungManager = SichtpruefungManager(ui, self)
        self.pruefanweisungManager: PruefanweisungManager = PruefanweisungManager(ui, self)
        logger.debug("Manager initialisiert")

    def set_current_page(self, page: Page) -> None:
        logger.debug(f"Seite geändert: {self.current_page} -> {page}")
        self.current_page = page

    def get_current_page(self) -> Page:
        return self.current_page
    
    def speichereSeiteninhalte(self, page: Page) -> None:
        """Delegiert die Speicherung an den entsprechenden Manager basierend auf dem aktuellen Vorgang."""
        logger.debug(f"Speichere Seiteninhalte für Seite {page} (Vorgang: {self.aktuellerVorgang})")
        if self.aktuellerVorgang == Vorgang.SICHTPRUEFUNG:
            self.sichtpruefungManager.speichereSeiteninhalte(page)
        elif self.aktuellerVorgang in [Vorgang.PRUEFANWEISUNG_ERSTELLEN, Vorgang.PRUEFANWEISUNG_BEARBEITEN]:
            self.pruefanweisungManager.speichereSeiteninhalte(page)
        else:
            logger.warning(f"Kein Manager für Vorgang {self.aktuellerVorgang} gefunden")