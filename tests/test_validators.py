"""
Tests für die Validatoren.
Hier verwenden wir Mocking, um die UI-Komponenten zu simulieren.
"""
import pytest
from unittest.mock import Mock, MagicMock
from src.logic.validators import ValidationController
from src.logic.state import AppState
from src.gui.pages import Page


class TestValidationController:
    """Test-Klasse für ValidationController"""
    
    @pytest.fixture
    def mock_ui(self):
        """Fixture: Erstellt ein Mock-UI-Objekt"""
        ui = MagicMock()
        # Standard-Werte für UI-Elemente
        ui.eigenschaftHandlungsbedarf = Mock(isChecked=Mock(return_value=True))
        ui.eigenschaftMassnahmenEingeben = Mock(text=Mock(return_value=""))
        ui.zusammenfassungPruefobjektStammdatenLagerortEingeben = Mock(text=Mock(return_value=""))
        ui.zusammenfassungPruefobjektStammdatenNummerEingeben = Mock(text=Mock(return_value=""))
        ui.zusammenfassungEinsatzbereitJa = Mock(isChecked=Mock(return_value=False))
        ui.zusammenfassungEinsatzbereitNein = Mock(isChecked=Mock(return_value=False))
        ui.zusammenfassungSignaturPrueferEingeben = Mock(text=Mock(return_value=""))
        ui.zusammenfassungSignaturDatumEingeben = Mock(text=Mock(return_value=""))
        ui.auswahlBildEinfuegen = Mock(property=Mock(return_value=False))
        ui.auswahlPruefobjektEingeben = Mock(text=Mock(return_value=""))
        ui.eigenschaftEditorKategorieEingeben = Mock(text=Mock(return_value=""))
        ui.eigenschaftEditorEigenschafteingeben = Mock(text=Mock(return_value=""))
        ui.hinzufuegen = Mock(setEnabled=Mock())
        ui.loeschen = Mock(setEnabled=Mock())
        ui.fertig = Mock(setEnabled=Mock())
        ui.abbrechen = Mock(setEnabled=Mock())
        return ui
    
    @pytest.fixture
    def mock_main_window(self):
        """Fixture: Erstellt ein Mock-Hauptfenster"""
        return Mock()
    
    @pytest.fixture
    def mock_state(self, mock_ui):
        """Fixture: Erstellt einen Mock-AppState"""
        state = Mock(spec=AppState)
        state.aktuelleEigenschaftIndex = 0
        state.sichtpruefungManager = Mock()
        state.sichtpruefungManager.sichtpruefung = Mock()
        state.sichtpruefungManager.pdfPfad = ""
        return state
    
    @pytest.fixture
    def validation_controller(self, mock_main_window, mock_ui, mock_state):
        """Fixture: Erstellt einen ValidationController mit Mocks"""
        return ValidationController(mock_main_window, mock_ui, mock_state)
    
    def test_ist_seite_valide_ohne_validierung(self, validation_controller):
        """Test: Seite ohne Validierung wird als valide akzeptiert"""
        ist_valide, nachricht = validation_controller.istSeiteValide(Page.HAUPTMENUE)
        assert ist_valide is True
        assert nachricht == ""
    
    def test_validiere_fertig_sichtpruefung_pruefablauf(self, validation_controller, mock_state):
        """Test: Validierung für Sichtprüfung-Prüfablauf"""
        ist_valide, nachricht = validation_controller.validiereFertigSichtpruefungPruefablauf()
        assert ist_valide is True
        assert nachricht == ""
        assert mock_state.aktuelleEigenschaftIndex == 0
    
    def test_validiere_fertig_sichtpruefung_eigenschaft_kein_handlungsbedarf(self, validation_controller, mock_ui):
        """Test: Validierung für Sichtprüfung-Eigenschaft ohne Handlungsbedarf"""
        mock_ui.eigenschaftHandlungsbedarf.isChecked.return_value = True
        mock_ui.eigenschaftMassnahmenEingeben.text.return_value = ""
        
        ist_valide, nachricht = validation_controller.validiereFertigSichtpruefungEigenschaft()
        assert ist_valide is True
        assert nachricht == ""
    
    def test_validiere_fertig_sichtpruefung_eigenschaft_mit_handlungsbedarf_und_massnahmen(self, validation_controller, mock_ui):
        """Test: Validierung für Sichtprüfung-Eigenschaft mit Handlungsbedarf und Maßnahmen"""
        mock_ui.eigenschaftHandlungsbedarf.isChecked.return_value = False
        mock_ui.eigenschaftMassnahmenEingeben.text.return_value = "Helm reparieren"
        
        ist_valide, nachricht = validation_controller.validiereFertigSichtpruefungEigenschaft()
        assert ist_valide is True
        assert nachricht == ""
    
    def test_validiere_fertig_sichtpruefung_eigenschaft_mit_handlungsbedarf_ohne_massnahmen(self, validation_controller, mock_ui):
        """Test: Validierung schlägt fehl wenn Handlungsbedarf ohne Maßnahmen"""
        mock_ui.eigenschaftHandlungsbedarf.isChecked.return_value = False
        mock_ui.eigenschaftMassnahmenEingeben.text.return_value = ""
        
        ist_valide, nachricht = validation_controller.validiereFertigSichtpruefungEigenschaft()
        assert ist_valide is False
        assert "Maßnahme" in nachricht
    
    def test_validiere_fertig_sichtpruefung_zusammenfassung_fehlende_daten(self, validation_controller, mock_ui):
        """Test: Validierung für Sichtprüfung-Zusammenfassung mit fehlenden Daten"""
        # Alle Felder leer
        ist_valide, nachricht = validation_controller.validiereFertigSichtpruefungZusammenfassung()
        assert ist_valide is False
        assert "Lagerort" in nachricht
    
    def test_validiere_fertig_sichtpruefung_zusammenfassung_alle_daten(self, validation_controller, mock_ui, mock_state, mock_main_window):
        """Test: Validierung für Sichtprüfung-Zusammenfassung mit allen Daten"""
        mock_ui.zusammenfassungPruefobjektStammdatenLagerortEingeben.text.return_value = "Lager 1"
        mock_ui.zusammenfassungPruefobjektStammdatenNummerEingeben.text.return_value = "12345"
        mock_ui.zusammenfassungEinsatzbereitJa.isChecked.return_value = True
        mock_ui.zusammenfassungSignaturPrueferEingeben.text.return_value = "Max Mustermann"
        mock_ui.zusammenfassungSignaturDatumEingeben.text.return_value = "2024-01-15"
        
        # Mock für QFileDialog.getSaveFileName
        from unittest.mock import patch
        with patch('src.logic.validators.QFileDialog.getSaveFileName', return_value=("test.pdf", "")):
            ist_valide, nachricht = validation_controller.validiereFertigSichtpruefungZusammenfassung()
            assert ist_valide is True
    
    def test_validiere_fertig_pruefanweisung_auswahl_ohne_bild(self, validation_controller, mock_ui):
        """Test: Validierung für Prüfanweisung-Auswahl ohne Bild"""
        mock_ui.auswahlBildEinfuegen.property.return_value = True  # isPlaceholder = True
        mock_ui.auswahlPruefobjektEingeben.text.return_value = "Test-Objekt"
        
        ist_valide, nachricht = validation_controller.validiereFertigPruefanweisungAuswahl()
        assert ist_valide is False
        assert "Bild" in nachricht
    
    def test_validiere_fertig_pruefanweisung_auswahl_ohne_name(self, validation_controller, mock_ui):
        """Test: Validierung für Prüfanweisung-Auswahl ohne Name"""
        mock_ui.auswahlBildEinfuegen.property.return_value = False  # isPlaceholder = False
        mock_ui.auswahlPruefobjektEingeben.text.return_value = ""
        
        ist_valide, nachricht = validation_controller.validiereFertigPruefanweisungAuswahl()
        assert ist_valide is False
        assert "Bezeichnung" in nachricht
    
    def test_validiere_fertig_pruefanweisung_auswahl_valide(self, validation_controller, mock_ui):
        """Test: Validierung für Prüfanweisung-Auswahl mit allen Daten"""
        mock_ui.auswahlBildEinfuegen.property.return_value = False  # isPlaceholder = False
        mock_ui.auswahlPruefobjektEingeben.text.return_value = "Test-Objekt"
        
        ist_valide, nachricht = validation_controller.validiereFertigPruefanweisungAuswahl()
        assert ist_valide is True
    
    def test_validiere_pruefanweisung_eigenschaft_ohne_kategorie(self, validation_controller, mock_ui):
        """Test: Validierung für Prüfanweisung-Eigenschaft ohne Kategorie"""
        mock_ui.eigenschaftEditorKategorieEingeben.text.return_value = ""
        mock_ui.eigenschaftEditorEigenschafteingeben.text.return_value = "Beschreibung"
        
        ist_valide, nachricht = validation_controller.validierePruefanweisungEigenschaft()
        assert ist_valide is False
        assert "Kategoriename" in nachricht
    
    def test_validiere_pruefanweisung_eigenschaft_ohne_beschreibung(self, validation_controller, mock_ui):
        """Test: Validierung für Prüfanweisung-Eigenschaft ohne Beschreibung"""
        mock_ui.eigenschaftEditorKategorieEingeben.text.return_value = "Kategorie"
        mock_ui.eigenschaftEditorEigenschafteingeben.text.return_value = ""
        
        ist_valide, nachricht = validation_controller.validierePruefanweisungEigenschaft()
        assert ist_valide is False
        assert "Eigenschaft" in nachricht
    
    def test_validiere_pruefanweisung_eigenschaft_valide(self, validation_controller, mock_ui):
        """Test: Validierung für Prüfanweisung-Eigenschaft mit allen Daten"""
        mock_ui.eigenschaftEditorKategorieEingeben.text.return_value = "Kategorie"
        mock_ui.eigenschaftEditorEigenschafteingeben.text.return_value = "Beschreibung"
        
        ist_valide, nachricht = validation_controller.validierePruefanweisungEigenschaft()
        assert ist_valide is True

