from src.gui.pages import Page
from src.logic.state import AppState
from ui.ui_main import Ui_MainWindow


class NavigationController:
    def __init__(self, ui: Ui_MainWindow, state: AppState):
        self.ui = ui
        self.state = state
        
    def get_next_page(self):
        match self.state.get_current_page():
            # case "hauptmenue" wird ausgelassen, weil es keine klare nächste Seite gibt

            case Page.SICHTPRUEFUNG_AUSWAHL:
                return Page.SICHTPRUEFUNG_INFOS
            case Page.SICHTPRUEFUNG_INFOS:
                return Page.SICHTPRUEFUNG_VORGABEN
            case Page.SICHTPRUEFUNG_VORGABEN:
                return Page.SICHTPRUEFUNG_PRUEFABLAUF
            case Page.SICHTPRUEFUNG_PRUEFABLAUF:
                return Page.SICHTPRUEFUNG_EIGENSCHAFT
            case Page.SICHTPRUEFUNG_EIGENSCHAFT:
                if self.hatDieSichtpruefungWeitereEigenschaften():
                    return Page.SICHTPRUEFUNG_EIGENSCHAFT
                else:
                    return Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG
            case Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG:
                return Page.ERFOLGREICH_ABGESCHLOSSEN

            case Page.PRUEFANWEISUNG_AUSWAHL:
                return Page.PRUEFANWEISUNG_INFOS
            case Page.PRUEFANWEISUNG_INFOS:
                return Page.PRUEFANWEISUNG_VORGABEN
            case Page.PRUEFANWEISUNG_VORGABEN:
                return Page.PRUEFANWEISUNG_PRUEFABLAUF
            case Page.PRUEFANWEISUNG_PRUEFABLAUF:
                return Page.PRUEFANWEISUNG_TYPISCHE_MAENGEL
            case Page.PRUEFANWEISUNG_TYPISCHE_MAENGEL:
                return Page.PRUEFANWEISUNG_EIGENSCHAFT
            case Page.PRUEFANWEISUNG_EIGENSCHAFT:
                if self.hatDiePruefanweisungWeitereEigenschaften(): # Zur Implemtierung von vorwärts, rückwärts
                    return Page.PRUEFANWEISUNG_EIGENSCHAFT
                else:
                    return Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG
            case Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG:
                return Page.ERFOLGREICH_ABGESCHLOSSEN
                
            case Page.ERFOLGREICH_ABGESCHLOSSEN:
                return Page.HAUPTMENUE

    # TODO noch nicht einsatzbereit wegen erfolgreich abgeschlossen
    def get_previous_page(self):
        match self.state.get_current_page():
            # case "hauptmenue" wird ausgelassen, weil man nach jeder abheschlossenen oder abgebrochenen Aktion nicht zurückkehren können soll. Wäre etwas merkwürdig wegen den Speichervorgängen

            case Page.SICHTPRUEFUNG_AUSWAHL:
                return Page.HAUPTMENUE
            case Page.SICHTPRUEFUNG_INFOS:
                return Page.SICHTPRUEFUNG_AUSWAHL
            case Page.SICHTPRUEFUNG_VORGABEN:
                return Page.SICHTPRUEFUNG_INFOS
            case Page.SICHTPRUEFUNG_PRUEFABLAUF:
                return Page.SICHTPRUEFUNG_VORGABEN
            case Page.SICHTPRUEFUNG_EIGENSCHAFT:
                if self.hatDieSichtpruefungWeitereEigenschaften():
                    return Page.SICHTPRUEFUNG_EIGENSCHAFT
                else:
                    return Page.SICHTPRUEFUNG_PRUEFABLAUF
            case Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG:
                return Page.SICHTPRUEFUNG_EIGENSCHAFT

            case Page.PRUEFANWEISUNG_AUSWAHL:
                return Page.HAUPTMENUE
            case Page.PRUEFANWEISUNG_INFOS:
                return Page.PRUEFANWEISUNG_AUSWAHL
            case Page.PRUEFANWEISUNG_VORGABEN:
                return Page.PRUEFANWEISUNG_INFOS
            case Page.PRUEFANWEISUNG_PRUEFABLAUF:
                return Page.PRUEFANWEISUNG_VORGABEN
            case Page.PRUEFANWEISUNG_TYPISCHE_MAENGEL:
                return Page.PRUEFANWEISUNG_PRUEFABLAUF
            case Page.PRUEFANWEISUNG_EIGENSCHAFT:
                if self.hatDiePruefanweisungWeitereEigenschaften():
                    return Page.PRUEFANWEISUNG_EIGENSCHAFT
                else:
                    return Page.PRUEFANWEISUNG_TYPISCHE_MAENGEL
            case Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG:
                return Page.PRUEFANWEISUNG_EIGENSCHAFT
                
            case Page.ERFOLGREICH_ABGESCHLOSSEN:
                return Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG
                return Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG

    def goto(self, page: Page):
        self.state.set_current_page(page)
        self.ui.content.setCurrentIndex(page.value)

    # TODO überprüfen
    def hatDieSichtpruefungWeitereEigenschaften(self):
        eigenschaftspruefungen = self.state.sichtpruefung.eigenschaftspruefungen
        return self.state.aktuelleEigenschaftIndex < len(eigenschaftspruefungen)

    # TODO überprüfen
    def hatDiePruefanweisungWeitereEigenschaften(self):
        eigenschaften = self.state.pruefanweisung.eigenschaften
        return self.state.aktuelleEigenschaftIndex < len(eigenschaften)
    
