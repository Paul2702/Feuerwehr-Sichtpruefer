"""
Tests für die Manager-Klassen (PruefanweisungManager und SichtpruefungManager).
Hier verwenden wir ausführliches Mocking für UI-Komponenten.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from src.logic.pruefanweisungManager import PruefanweisungManager
from src.logic.sichtpruefungManager import SichtpruefungManager
from src.logic.state import AppState
from src.models.pruefanweisung import Pruefanweisung
from src.models.sichtpruefung import Sichtpruefung
from src.gui.pages import Page


class TestPruefanweisungManager:
    """Test-Klasse für PruefanweisungManager"""
    
    @pytest.fixture
    def mock_ui(self):
        """Fixture: Erstellt ein Mock-UI-Objekt"""
        ui = MagicMock()
        ui.auswahlBildEinfuegen = Mock()
        ui.auswahlBildEinfuegen.property = Mock(return_value="bild.jpg")
        ui.auswahlPruefobjektEingeben = Mock(text=Mock(return_value="Test-Objekt"))
        ui.pruefanweisungInfosPruefartEingeben = Mock(toPlainText=Mock(return_value="Sichtprüfung"))
        ui.pruefanweisungInfosPruefvorgabeEingeben = Mock(toPlainText=Mock(return_value="DIN 12345"))
        ui.pruefanweisungInfosPruefvorgabeZusatzEingeben = Mock(toPlainText=Mock(return_value=""))
        ui.pruefanweisungInfosPrueffristEingeben = Mock(toPlainText=Mock(return_value="12 Monate"))
        ui.pruefanweisungInfosSachkundigerEingeben = Mock(toPlainText=Mock(return_value="Max Mustermann"))
        ui.pruefanweisungInfosZusatzausbildungEingeben = Mock(toPlainText=Mock(return_value=""))
        ui.pruefanweisungInfosHerstellerEingeben = Mock(toPlainText=Mock(return_value="Hersteller"))
        ui.pruefanweisungInfosAussonderungsfristEingeben = Mock(toPlainText=Mock(return_value=""))
        ui.vorgabenTextEingeben = Mock(toHtml=Mock(return_value="<p>Vorgaben</p>"))
        ui.pruefablaufTextEingeben = Mock(toHtml=Mock(return_value="<p>Prüfablauf</p>"))
        ui.eigenschaftEditorKategorieEingeben = Mock(text=Mock(return_value="Kategorie"))
        ui.eigenschaftEditorEigenschafteingeben = Mock(text=Mock(return_value="Beschreibung"))
        ui.verticalLayout_11 = Mock(count=Mock(return_value=1))
        ui.zusammenfassungHinweisEingeben = Mock(toPlainText=Mock(return_value="Hinweis"))
        return ui
    
    @pytest.fixture
    def mock_app_state(self):
        """Fixture: Erstellt einen Mock-AppState"""
        state = Mock(spec=AppState)
        state.aktuelleEigenschaftIndex = 0
        return state
    
    @pytest.fixture
    def pruefanweisung_manager(self, mock_ui, mock_app_state):
        """Fixture: Erstellt einen PruefanweisungManager"""
        manager = PruefanweisungManager(mock_ui, mock_app_state)
        manager.pruefanweisung = Pruefanweisung()
        return manager
    
    def test_speichere_pruefanweisung_auswahl(self, pruefanweisung_manager, mock_ui):
        """Test: Speichern der Prüfanweisung-Auswahl"""
        mock_ui.auswahlBildEinfuegen.property.return_value = "test_bild.jpg"
        mock_ui.auswahlPruefobjektEingeben.text.return_value = "Feuerwehrhelm"
        
        pruefanweisung_manager.speicherePruefanweisungAuswahl()
        
        assert pruefanweisung_manager.pruefanweisung.pfadVorschauBild == "test_bild.jpg"
        assert pruefanweisung_manager.pruefanweisung.namePruefobjekt == "Feuerwehrhelm"
    
    def test_speichere_pruefanweisung_auswahl_ohne_pruefanweisung(self, pruefanweisung_manager):
        """Test: Fehler wenn Prüfanweisung nicht initialisiert ist"""
        pruefanweisung_manager.pruefanweisung = None
        
        with pytest.raises(ValueError, match="nicht initialisiert"):
            pruefanweisung_manager.speicherePruefanweisungAuswahl()
    
    def test_speichere_pruefanweisung_infos(self, pruefanweisung_manager, mock_ui):
        """Test: Speichern der Prüfanweisung-Infos"""
        pruefanweisung_manager.speicherePruefanweisungInfos()
        
        assert pruefanweisung_manager.pruefanweisung.pruefart == "Sichtprüfung"
        assert pruefanweisung_manager.pruefanweisung.pruefvorgabe == "DIN 12345"
        assert pruefanweisung_manager.pruefanweisung.prueffrist == "12 Monate"
        assert pruefanweisung_manager.pruefanweisung.sachkundiger == "Max Mustermann"
    
    def test_speichere_pruefanweisung_vorgaben(self, pruefanweisung_manager, mock_ui):
        """Test: Speichern der Prüfanweisung-Vorgaben"""
        mock_ui.vorgabenTextEingeben.toHtml.return_value = "<p>Neue Vorgaben</p>"
        
        pruefanweisung_manager.speicherePruefanweisungVorgaben()
        
        assert pruefanweisung_manager.pruefanweisung.vorgabenText == "<p>Neue Vorgaben</p>"
    
    def test_speichere_pruefanweisung_pruefablauf(self, pruefanweisung_manager, mock_ui):
        """Test: Speichern des Prüfablaufs"""
        mock_ui.pruefablaufTextEingeben.toHtml.return_value = "<p>Neuer Prüfablauf</p>"
        
        pruefanweisung_manager.speicherePruefanweisungPruefablauf()
        
        assert pruefanweisung_manager.pruefanweisung.pruefablaufText == "<p>Neuer Prüfablauf</p>"
    
    def test_speichere_pruefanweisung_eigenschaft(self, pruefanweisung_manager, mock_ui, mock_app_state):
        """Test: Speichern einer Eigenschaft"""
        mock_ui.eigenschaftEditorKategorieEingeben.text.return_value = "Schutz"
        mock_ui.eigenschaftEditorEigenschafteingeben.text.return_value = "Helm prüfen"
        mock_ui.verticalLayout_11.count.return_value = 1
        
        initial_index = mock_app_state.aktuelleEigenschaftIndex
        pruefanweisung_manager.speicherePruefanweisungEigenschaft()
        
        assert len(pruefanweisung_manager.pruefanweisung.eigenschaften) == 1
        assert pruefanweisung_manager.pruefanweisung.eigenschaften[0].kategorie == "Schutz"
        assert pruefanweisung_manager.pruefanweisung.eigenschaften[0].beschreibung == "Helm prüfen"
        assert mock_app_state.aktuelleEigenschaftIndex == initial_index + 1
    
    def test_speichere_seiteninhalte(self, pruefanweisung_manager):
        """Test: Speichern von Seiteninhalten delegiert an richtige Methode"""
        pruefanweisung_manager.speicherePruefanweisungAuswahl = Mock()
        
        pruefanweisung_manager.speichereSeiteninhalte(Page.PRUEFANWEISUNG_AUSWAHL)
        
        pruefanweisung_manager.speicherePruefanweisungAuswahl.assert_called_once()
    
    def test_speichere_seiteninhalte_unbekannte_seite(self, pruefanweisung_manager):
        """Test: Speichern von unbekannter Seite führt zu keinem Fehler"""
        # Sollte keine Exception werfen
        pruefanweisung_manager.speichereSeiteninhalte(Page.HAUPTMENUE)

    def test_speichere_pruefanweisung_zusammenfassung_propagates_serializer_error(self, pruefanweisung_manager):
        """Test: Fehler aus dem Serializer wird weitergereicht"""
        pruefanweisung_manager.ui.zusammenfassungHinweisEingeben = Mock(toPlainText=Mock(return_value="hinweis"))
        with patch('src.logic.pruefanweisungManager.speicherePruefanweisungXml', side_effect=RuntimeError('xml failed')):
            with pytest.raises(RuntimeError, match='xml failed'):
                pruefanweisung_manager.speicherePruefanweisungZusammenfassung()


class TestSichtpruefungManager:
    """Test-Klasse für SichtpruefungManager"""
    
    @pytest.fixture
    def mock_ui(self):
        """Fixture: Erstellt ein Mock-UI-Objekt"""
        ui = MagicMock()
        ui.eigenschaftHandlungsbedarf = Mock(isChecked=Mock(return_value=True))
        ui.eigenschaftMassnahmenEingeben = Mock(text=Mock(return_value=""))
        ui.zusammenfassungPruefobjektStammdatenLagerortEingeben = Mock(text=Mock(return_value="Lager 1"))
        ui.zusammenfassungPruefobjektStammdatenNummerEingeben = Mock(text=Mock(return_value="12345"))
        ui.zusammenfassungEinsatzbereitJa = Mock(isChecked=Mock(return_value=True))
        ui.zusammenfassungSignaturPrueferEingeben = Mock(text=Mock(return_value="Max Mustermann"))
        ui.zusammenfassungSignaturDatumEingeben = Mock(text=Mock(return_value="2024-01-15"))
        ui.zusammenfassungEinsatzbereitBemerkungenEingeben = Mock(toPlainText=Mock(return_value="Bemerkung"))
        return ui
    
    @pytest.fixture
    def mock_app_state(self):
        """Fixture: Erstellt einen Mock-AppState"""
        state = Mock(spec=AppState)
        state.aktuelleEigenschaftIndex = 0
        return state
    
    @pytest.fixture
    def sichtpruefung_manager(self, mock_ui, mock_app_state):
        """Fixture: Erstellt einen SichtpruefungManager"""
        manager = SichtpruefungManager(mock_ui, mock_app_state)
        manager.sichtpruefung = Sichtpruefung()
        return manager
    
    def test_speichere_sichtpruefung_eigenschaft(self, sichtpruefung_manager, mock_ui, mock_app_state):
        """Test: Speichern einer Sichtprüfung-Eigenschaft"""
        mock_ui.eigenschaftHandlungsbedarf.isChecked.return_value = False
        mock_ui.eigenschaftMassnahmenEingeben.text.return_value = "Helm reparieren"
        
        # Füge zuerst eine Eigenschaftsprüfung hinzu
        sichtpruefung_manager.sichtpruefung.eigenschaftspruefungHinzufuegen("Schutz", "Helm", [], True, "")
        
        initial_index = mock_app_state.aktuelleEigenschaftIndex
        sichtpruefung_manager.speichereSichtpruefungEigenschaft()
        
        assert sichtpruefung_manager.sichtpruefung.eigenschaftspruefungen[0].keinHandlungsbedarf is False
        assert sichtpruefung_manager.sichtpruefung.eigenschaftspruefungen[0].massnahmen == "Helm reparieren"
        assert mock_app_state.aktuelleEigenschaftIndex == initial_index + 1
    
    def test_speichere_sichtpruefung_eigenschaft_ohne_sichtpruefung(self, sichtpruefung_manager):
        """Test: Fehler wenn Sichtprüfung nicht initialisiert ist"""
        sichtpruefung_manager.sichtpruefung = None
        
        with pytest.raises(ValueError, match="nicht initialisiert"):
            sichtpruefung_manager.speichereSichtpruefungEigenschaft()
    
    @patch('src.logic.sichtpruefungManager.PdfGenerator')
    def test_speichere_sichtpruefung_zusammenfassung(self, mock_pdf_generator, sichtpruefung_manager, mock_ui):
        """Test: Speichern der Sichtprüfung-Zusammenfassung"""
        sichtpruefung_manager.pdfPfad = "test.pdf"
        mock_pdf_instance = Mock()
        mock_pdf_generator.return_value = mock_pdf_instance
        
        sichtpruefung_manager.speichereSichtpruefungZusammenfassung()
        
        assert sichtpruefung_manager.sichtpruefung.lagerort == "Lager 1"
        assert sichtpruefung_manager.sichtpruefung.nummer == "12345"
        assert sichtpruefung_manager.sichtpruefung.einsatzbereit is True
        assert sichtpruefung_manager.sichtpruefung.pruefer == "Max Mustermann"
        assert sichtpruefung_manager.sichtpruefung.datum == "2024-01-15"
        mock_pdf_instance.erstelle_pdf.assert_called_once_with("test.pdf", sichtpruefung_manager.sichtpruefung)
    
    def test_speichere_sichtpruefung_zusammenfassung_ohne_sichtpruefung(self, sichtpruefung_manager):
        """Test: Fehler wenn Sichtprüfung nicht initialisiert ist"""
        sichtpruefung_manager.sichtpruefung = None
        
        with pytest.raises(ValueError, match="nicht initialisiert"):
            sichtpruefung_manager.speichereSichtpruefungZusammenfassung()
    
    def test_speichere_seiteninhalte(self, sichtpruefung_manager):
        """Test: Speichern von Seiteninhalten delegiert an richtige Methode"""
        sichtpruefung_manager.speichereSichtpruefungEigenschaft = Mock()
        
        sichtpruefung_manager.speichereSeiteninhalte(Page.SICHTPRUEFUNG_EIGENSCHAFT)
        
        sichtpruefung_manager.speichereSichtpruefungEigenschaft.assert_called_once()
    
    def test_speichere_seiteninhalte_unbekannte_seite(self, sichtpruefung_manager):
        """Test: Speichern von unbekannter Seite führt zu keinem Fehler"""
        sichtpruefung_manager.speichereSeiteninhalte(Page.HAUPTMENUE)

    def test_speichere_sichtpruefung_eigenschaft_raises_indexerror_when_no_eigenschaft(self, sichtpruefung_manager):
        """Test: speichereSichtpruefungEigenschaft wirft IndexError wenn keine Eigenschaft vorhanden ist"""
        sichtpruefung_manager.sichtpruefung.eigenschaftspruefungen = []
        sichtpruefung_manager.ui.eigenschaftHandlungsbedarf = Mock(isChecked=Mock(return_value=False))
        sichtpruefung_manager.ui.eigenschaftMassnahmenEingeben = Mock(text=Mock(return_value='m'))
        with pytest.raises(IndexError):
            sichtpruefung_manager.speichereSichtpruefungEigenschaft()

    @patch('src.logic.sichtpruefungManager.PdfGenerator')
    def test_speichere_sichtpruefung_zusammenfassung_propagates_pdf_error(self, mock_pdf_generator, sichtpruefung_manager):
        """Test: Fehler beim Erstellen des PDFs wird weitergereicht"""
        sichtpruefung_manager.pdfPfad = 'test.pdf'
        mock_pdf_instance = Mock()
        mock_pdf_instance.erstelle_pdf.side_effect = RuntimeError('pdf error')
        mock_pdf_generator.return_value = mock_pdf_instance
        sichtpruefung_manager.ui.zusammenfassungPruefobjektStammdatenLagerortEingeben = Mock(text=Mock(return_value='Lager'))
        sichtpruefung_manager.ui.zusammenfassungPruefobjektStammdatenNummerEingeben = Mock(text=Mock(return_value='123'))
        sichtpruefung_manager.ui.zusammenfassungEinsatzbereitJa = Mock(isChecked=Mock(return_value=True))
        sichtpruefung_manager.ui.zusammenfassungSignaturPrueferEingeben = Mock(text=Mock(return_value='Pruefer'))
        sichtpruefung_manager.ui.zusammenfassungSignaturDatumEingeben = Mock(text=Mock(return_value='2025-01-01'))
        sight = sichtpruefung_manager
        sight.ui.zusammenfassungEinsatzbereitBemerkungenEingeben = Mock(toPlainText=Mock(return_value=''))
        with pytest.raises(RuntimeError, match='pdf error'):
            sichtpruefung_manager.speichereSichtpruefungZusammenfassung()
        # Sollte keine Exception werfen

