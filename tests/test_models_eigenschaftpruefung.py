"""
Tests für das Eigenschaftspruefung-Modell.
"""
import pytest
from src.models.eigenschaft import Eigenschaft
from src.models.eigenschaftpruefung import Eigenschaftspruefung


class TestEigenschaftspruefung:
    """Test-Klasse für Eigenschaftspruefung"""
    
    def test_eigenschaftspruefung_initialisierung(self):
        """Test: Eigenschaftspruefung wird korrekt initialisiert"""
        eigenschaft = Eigenschaft("Schutz", "Helm prüfen", [])
        kein_handlungsbedarf = True
        massnahmen = ""
        
        pruefung = Eigenschaftspruefung(eigenschaft, kein_handlungsbedarf, massnahmen)
        
        assert pruefung.eigenschaft == eigenschaft
        assert pruefung.keinHandlungsbedarf == kein_handlungsbedarf
        assert pruefung.massnahmen == massnahmen
    
    def test_eigenschaftspruefung_mit_handlungsbedarf(self):
        """Test: Eigenschaftspruefung mit Handlungsbedarf"""
        eigenschaft = Eigenschaft("Schutz", "Helm prüfen", [])
        pruefung = Eigenschaftspruefung(eigenschaft, False, "Helm austauschen")
        
        assert pruefung.keinHandlungsbedarf is False
        assert pruefung.massnahmen == "Helm austauschen"
    
    def test_set_kein_handlungsbedarf(self):
        """Test: setKeinHandlungsbedarf ändert den Wert"""
        eigenschaft = Eigenschaft("Test", "Test", [])
        pruefung = Eigenschaftspruefung(eigenschaft, True, "")
        
        pruefung.setKeinHandlungsbedarf(False)
        assert pruefung.keinHandlungsbedarf is False
        
        pruefung.setKeinHandlungsbedarf(True)
        assert pruefung.keinHandlungsbedarf is True
    
    def test_set_massnahmen(self):
        """Test: setMassnahmen ändert die Maßnahmen"""
        eigenschaft = Eigenschaft("Test", "Test", [])
        pruefung = Eigenschaftspruefung(eigenschaft, False, "")
        
        pruefung.setMassnahmen("Neue Maßnahme")
        assert pruefung.massnahmen == "Neue Maßnahme"
        
        pruefung.setMassnahmen("Andere Maßnahme")
        assert pruefung.massnahmen == "Andere Maßnahme"

