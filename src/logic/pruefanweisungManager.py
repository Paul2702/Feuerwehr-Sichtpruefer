# - Erstellen einer neuen Prüfanweisung
# - Bearbeiten / Klonen
# - Speichern / Löschen
# - Bild hinzufügen
# - Validieren

import logging
from typing import TYPE_CHECKING, Optional
from src.gui.pages import Page
from src.logic.serializer import addToPruefanweisungenXml, speicherePruefanweisungXml
from src.models.pruefanweisung import Pruefanweisung
from ui.ui_main import Ui_MainWindow

if TYPE_CHECKING:
    from src.logic.state import AppState

logger = logging.getLogger(__name__)


class PruefanweisungManager:
    def __init__(self, ui: Ui_MainWindow, app_state: "AppState") -> None:
        self.ui: Ui_MainWindow = ui
        self.app_state: "AppState" = app_state
        self.pruefanweisung: Optional[Pruefanweisung] = None

        # Store method names so tests can monkeypatch instance methods and
        # speichereSeiteninhalte will call the current attribute.
        self.speicherbareSeitenInhalte: dict[Page, str] = {
            Page.PRUEFANWEISUNG_AUSWAHL: "speicherePruefanweisungAuswahl",
            Page.PRUEFANWEISUNG_INFOS: "speicherePruefanweisungInfos",
            Page.PRUEFANWEISUNG_VORGABEN: "speicherePruefanweisungVorgaben",
            Page.PRUEFANWEISUNG_PRUEFABLAUF: "speicherePruefanweisungPruefablauf",
            Page.PRUEFANWEISUNG_EIGENSCHAFT: "speicherePruefanweisungEigenschaft",
            Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG: "speicherePruefanweisungZusammenfassung"
        }
    
    def speichereSeiteninhalte(self, page: Page) -> None:
        if page in self.speicherbareSeitenInhalte:
            method_name = self.speicherbareSeitenInhalte[page]
            getattr(self, method_name)()
        
    def speicherePruefanweisungAuswahl(self) -> None:
        logger.debug("Speichere Prüfanweisung-Auswahl")
        bildPfad = self.ui.auswahlBildEinfuegen.property("imagePath")
        namePruefobjekt = self.ui.auswahlPruefobjektEingeben.text().strip()
        logger.debug(f"Auswahl: namePruefobjekt={namePruefobjekt}, bildPfad={bildPfad}")
        if self.pruefanweisung is None:
            raise ValueError("Pruefanweisung wurde nicht initialisiert")
        self.pruefanweisung.auswahlHinzufuegen(bildPfad or "", namePruefobjekt)

    def speicherePruefanweisungInfos(self) -> None:
        pruefart = self.ui.pruefanweisungInfosPruefartEingeben.toPlainText().strip()
        pruefvorgabe = self.ui.pruefanweisungInfosPruefvorgabeEingeben.toPlainText().strip()
        pruefvorgabeZusatz = self.ui.pruefanweisungInfosPruefvorgabeZusatzEingeben.toPlainText().strip()
        prueffrist = self.ui.pruefanweisungInfosPrueffristEingeben.toPlainText().strip()
        sachkundiger = self.ui.pruefanweisungInfosSachkundigerEingeben.toPlainText().strip()
        zusatzausbildung = self.ui.pruefanweisungInfosZusatzausbildungEingeben.toPlainText().strip()
        hersteller = self.ui.pruefanweisungInfosHerstellerEingeben.toPlainText().strip()
        aussonderungsfrist = self.ui.pruefanweisungInfosAussonderungsfristEingeben.toPlainText().strip()
        if self.pruefanweisung is None:
            raise ValueError("Pruefanweisung wurde nicht initialisiert")
        self.pruefanweisung.infosHinzufuegen(pruefart, pruefvorgabe, pruefvorgabeZusatz, prueffrist, sachkundiger, zusatzausbildung, hersteller, aussonderungsfrist)

    def speicherePruefanweisungVorgaben(self) -> None:
        vorgaben = self.ui.vorgabenTextEingeben.toHtml()
        if self.pruefanweisung is None:
            raise ValueError("Pruefanweisung wurde nicht initialisiert")
        self.pruefanweisung.vorgabenHinzufuegen(vorgaben)

    def speicherePruefanweisungPruefablauf(self) -> None:
        pruefablauf = self.ui.pruefablaufTextEingeben.toHtml()
        if self.pruefanweisung is None:
            raise ValueError("Pruefanweisung wurde nicht initialisiert")
        self.pruefanweisung.pruefablaufHinzufuegen(pruefablauf)

    def speicherePruefanweisungEigenschaft(self) -> None:
        logger.debug(f"Speichere Prüfanweisung-Eigenschaft (Index: {self.app_state.aktuelleEigenschaftIndex})")
        kategorie = self.ui.eigenschaftEditorKategorieEingeben.text().strip()
        beschreibung = self.ui.eigenschaftEditorEigenschafteingeben.text().strip()
        logger.debug(f"Eigenschaft: kategorie={kategorie}, beschreibung={beschreibung[:50]}...")
        
        anzahlWidgets = self.ui.verticalLayout_11.count()
        bilder = []
        if anzahlWidgets > 1:
            for i in range(0, anzahlWidgets-2, 2):
                # Bild
                widget = self.ui.verticalLayout_11.itemAt(i).widget()
                bildPfad = widget.property('imagePath') if widget else None
                # Beschreibung
                widget = self.ui.verticalLayout_11.itemAt(i+1).widget()
                bildBeschreibung = widget.toPlainText().strip() if widget else ""
                bilder.append((bildPfad, bildBeschreibung))
        
        logger.debug(f"Eigenschaft hat {len(bilder)} Bilder")
        if self.pruefanweisung is None:
            raise ValueError("Pruefanweisung wurde nicht initialisiert")
        self.pruefanweisung.eigenschaftHinzufuegen(kategorie, beschreibung, bilder)
        self.app_state.aktuelleEigenschaftIndex += 1
        logger.info(f"Eigenschaft gespeichert, Index erhöht auf: {self.app_state.aktuelleEigenschaftIndex}")

    def speicherePruefanweisungZusammenfassung(self) -> None:
        logger.info("Speichere Prüfanweisung-Zusammenfassung")
        hinweis = self.ui.zusammenfassungHinweisEingeben.toPlainText().strip()
        if self.pruefanweisung is None:
            raise ValueError("Pruefanweisung wurde nicht initialisiert")
        self.pruefanweisung.hinweisHinzufuegen(hinweis)
        logger.debug(f"Hinweis hinzugefügt: {hinweis[:50] if hinweis else 'kein Hinweis'}...")
        
        try:
            pruefanweisungXmlPfad = speicherePruefanweisungXml(self.pruefanweisung)
            logger.info(f"Prüfanweisung-XML gespeichert: {pruefanweisungXmlPfad}")
            addToPruefanweisungenXml(self.pruefanweisung, pruefanweisungXmlPfad)
            logger.info("Prüfanweisung erfolgreich gespeichert und zur Übersicht hinzugefügt")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Prüfanweisung: {e}", exc_info=True)
            raise

        