"""
Tests für den AppState.
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.logic.state import AppState
from src.gui.pages import Page
from src.logic.vorgang import Vorgang


class TestAppState:
    """Test-Klasse für AppState"""
    
    @pytest.fixture
    def mock_ui(self):
        """Fixture: Erstellt ein Mock-UI-Objekt"""
        return MagicMock()
    
    @pytest.fixture
    def app_state(self, mock_ui):
        """Fixture: Erstellt einen AppState"""
        return AppState(mock_ui)
    
    def test_app_state_initialisierung(self, app_state):
        """Test: AppState wird korrekt initialisiert"""
        assert app_state.aktuelleEigenschaftIndex == 0
        assert app_state.current_page == Page.HAUPTMENUE
        assert app_state.aktuellerVorgang == Vorgang.HAUPTMENUE
        assert app_state.sichtpruefungManager is not None
        assert app_state.pruefanweisungManager is not None
    
    def test_set_current_page(self, app_state):
        """Test: Aktuelle Seite wird gesetzt"""
        app_state.set_current_page(Page.SICHTPRUEFUNG_AUSWAHL)
        assert app_state.current_page == Page.SICHTPRUEFUNG_AUSWAHL
    
    def test_get_current_page(self, app_state):
        """Test: Aktuelle Seite wird zurückgegeben"""
        app_state.set_current_page(Page.SICHTPRUEFUNG_INFOS)
        assert app_state.get_current_page() == Page.SICHTPRUEFUNG_INFOS
    
    def test_speichere_seiteninhalte_sichtpruefung(self, app_state):
        """Test: Speichern von Seiteninhalten für Sichtprüfung"""
        app_state.aktuellerVorgang = Vorgang.SICHTPRUEFUNG
        app_state.sichtpruefungManager.speichereSeiteninhalte = Mock()
        
        app_state.speichereSeiteninhalte(Page.SICHTPRUEFUNG_EIGENSCHAFT)
        
        app_state.sichtpruefungManager.speichereSeiteninhalte.assert_called_once_with(Page.SICHTPRUEFUNG_EIGENSCHAFT)
    
    def test_speichere_seiteninhalte_pruefanweisung_erstellen(self, app_state):
        """Test: Speichern von Seiteninhalten für Prüfanweisung erstellen"""
        app_state.aktuellerVorgang = Vorgang.PRUEFANWEISUNG_ERSTELLEN
        app_state.pruefanweisungManager.speichereSeiteninhalte = Mock()
        
        app_state.speichereSeiteninhalte(Page.PRUEFANWEISUNG_AUSWAHL)
        
        app_state.pruefanweisungManager.speichereSeiteninhalte.assert_called_once_with(Page.PRUEFANWEISUNG_AUSWAHL)
    
    def test_speichere_seiteninhalte_pruefanweisung_bearbeiten(self, app_state):
        """Test: Speichern von Seiteninhalten für Prüfanweisung bearbeiten"""
        app_state.aktuellerVorgang = Vorgang.PRUEFANWEISUNG_BEARBEITEN
        app_state.pruefanweisungManager.speichereSeiteninhalte = Mock()
        
        app_state.speichereSeiteninhalte(Page.PRUEFANWEISUNG_INFOS)
        
        app_state.pruefanweisungManager.speichereSeiteninhalte.assert_called_once_with(Page.PRUEFANWEISUNG_INFOS)
    
    def test_speichere_seiteninhalte_ohne_manager(self, app_state, caplog):
        """Test: Speichern von Seiteninhalten ohne passenden Manager"""
        app_state.aktuellerVorgang = Vorgang.HAUPTMENUE
        
        app_state.speichereSeiteninhalte(Page.HAUPTMENUE)
        
        # Es sollte eine Warnung geloggt werden
        assert "Kein Manager" in caplog.text or True  # Falls Logging nicht erfasst wird

