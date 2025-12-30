"""
Tests für das Sichtpruefung-Modell.
"""
import pytest
from src.models.sichtpruefung import Sichtpruefung
from src.models.pruefanweisung import Pruefanweisung
from src.models.eigenschaft import Eigenschaft


class TestSichtpruefung:
    """Test-Klasse für Sichtpruefung"""
    
    def test_sichtpruefung_initialisierung(self):
        """Test: Sichtpruefung wird korrekt initialisiert"""
        sichtpruefung = Sichtpruefung()
        
        assert sichtpruefung.pruefanweisung is None
        assert sichtpruefung.lagerort == ''
        assert sichtpruefung.nummer == ''
        assert sichtpruefung.einsatzbereit is False
        assert sichtpruefung.bemerkungen == ''
        assert sichtpruefung.pruefer == ''
        assert sichtpruefung.datum == ''
        assert sichtpruefung.eigenschaftspruefungen == []
    
    def test_labels_befuellen(self):
        """Test: Prüfanweisung wird zugewiesen"""
        sichtpruefung = Sichtpruefung()
        pruefanweisung = Pruefanweisung()
        pruefanweisung.auswahlHinzufuegen("bild.jpg", "Test-Objekt")
        
        sichtpruefung.labelsBefuellen(pruefanweisung)
        
        assert sichtpruefung.pruefanweisung == pruefanweisung
        assert sichtpruefung.pruefanweisung.namePruefobjekt == "Test-Objekt"
    
    def test_eigenschaftspruefung_hinzufuegen(self):
        """Test: Eigenschaftsprüfung wird hinzugefügt"""
        sichtpruefung = Sichtpruefung()
        assert len(sichtpruefung.eigenschaftspruefungen) == 0
        
        sichtpruefung.eigenschaftspruefungHinzufuegen(
            "Schutz", "Helm prüfen", [], True, ""
        )
        
        assert len(sichtpruefung.eigenschaftspruefungen) == 1
        assert sichtpruefung.eigenschaftspruefungen[0].eigenschaft.kategorie == "Schutz"
        assert sichtpruefung.eigenschaftspruefungen[0].keinHandlungsbedarf is True
    
    def test_eigenschaftspruefung_hinzufuegen_mit_handlungsbedarf(self):
        """Test: Eigenschaftsprüfung mit Handlungsbedarf wird hinzugefügt"""
        sichtpruefung = Sichtpruefung()
        sichtpruefung.eigenschaftspruefungHinzufuegen(
            "Schutz", "Helm prüfen", [], False, "Helm austauschen"
        )
        
        assert sichtpruefung.eigenschaftspruefungen[0].keinHandlungsbedarf is False
        assert sichtpruefung.eigenschaftspruefungen[0].massnahmen == "Helm austauschen"
    
    def test_eigenschaftspruefung_hinzufuegen_mit_bildern(self):
        """Test: Eigenschaftsprüfung mit Bildern wird hinzugefügt"""
        sichtpruefung = Sichtpruefung()
        bilder = [("bild1.jpg", "Beschreibung 1")]
        sichtpruefung.eigenschaftspruefungHinzufuegen("Schutz", "Helm", bilder)
        
        assert len(sichtpruefung.eigenschaftspruefungen[0].eigenschaft.bilder) == 1
    
    def test_pruef_ergebnis_einfuegen(self):
        """Test: Prüfergebnis wird in bestehende Eigenschaftsprüfung eingefügt"""
        sichtpruefung = Sichtpruefung()
        sichtpruefung.eigenschaftspruefungHinzufuegen("Schutz", "Helm", [], True, "")
        
        sichtpruefung.pruefErgebnisEinfuegen(0, False, "Helm reparieren")
        
        assert sichtpruefung.eigenschaftspruefungen[0].keinHandlungsbedarf is False
        assert sichtpruefung.eigenschaftspruefungen[0].massnahmen == "Helm reparieren"
    
    def test_pruef_ergebnis_einfuegen_mehrere(self):
        """Test: Prüfergebnisse für mehrere Eigenschaften werden eingefügt"""
        sichtpruefung = Sichtpruefung()
        sichtpruefung.eigenschaftspruefungHinzufuegen("Schutz", "Helm", [], True, "")
        sichtpruefung.eigenschaftspruefungHinzufuegen("Funktion", "Atemschutz", [], True, "")
        
        sichtpruefung.pruefErgebnisEinfuegen(0, True, "")
        sichtpruefung.pruefErgebnisEinfuegen(1, False, "Atemschutz prüfen")
        
        assert sichtpruefung.eigenschaftspruefungen[0].keinHandlungsbedarf is True
        assert sichtpruefung.eigenschaftspruefungen[1].keinHandlungsbedarf is False
        assert sichtpruefung.eigenschaftspruefungen[1].massnahmen == "Atemschutz prüfen"
    
    def test_finales_ergebnis_einfuegen(self):
        """Test: Finales Ergebnis wird eingefügt"""
        sichtpruefung = Sichtpruefung()
        sichtpruefung.finalesErgebnisEinfuegen(
            lagerort="Lager 1",
            nummer="12345",
            einsatzbereit=True,
            pruefer="Max Mustermann",
            datum="2024-01-15",
            bemerkungen="Alles in Ordnung"
        )
        
        assert sichtpruefung.lagerort == "Lager 1"
        assert sichtpruefung.nummer == "12345"
        assert sichtpruefung.einsatzbereit is True
        assert sichtpruefung.pruefer == "Max Mustermann"
        assert sichtpruefung.datum == "2024-01-15"
        assert sichtpruefung.bemerkungen == "Alles in Ordnung"
    
    def test_finales_ergebnis_einfuegen_ohne_bemerkungen(self):
        """Test: Finales Ergebnis ohne Bemerkungen wird eingefügt"""
        sichtpruefung = Sichtpruefung()
        sichtpruefung.finalesErgebnisEinfuegen(
            lagerort="Lager 1",
            nummer="12345",
            einsatzbereit=False,
            pruefer="Max Mustermann",
            datum="2024-01-15"
        )
        
        assert sichtpruefung.lagerort == "Lager 1"
        assert sichtpruefung.einsatzbereit is False
        assert sichtpruefung.bemerkungen == ''

