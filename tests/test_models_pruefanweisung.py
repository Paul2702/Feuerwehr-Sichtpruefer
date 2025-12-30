"""
Tests für das Pruefanweisung-Modell.
"""
import pytest
from src.models.pruefanweisung import Pruefanweisung
from src.models.eigenschaft import Eigenschaft


class TestPruefanweisung:
    """Test-Klasse für Pruefanweisung"""
    
    def test_pruefanweisung_initialisierung(self):
        """Test: Pruefanweisung wird korrekt initialisiert"""
        pruefanweisung = Pruefanweisung()
        
        assert pruefanweisung.pfadVorschauBild == ''
        assert pruefanweisung.namePruefobjekt == ''
        assert pruefanweisung.eigenschaften == []
        assert pruefanweisung.hinweis == ''
    
    def test_auswahl_hinzufuegen(self):
        """Test: Auswahl-Daten werden korrekt hinzugefügt"""
        pruefanweisung = Pruefanweisung()
        pruefanweisung.auswahlHinzufuegen("bild.jpg", "Feuerwehrhelm")
        
        assert pruefanweisung.pfadVorschauBild == "bild.jpg"
        assert pruefanweisung.namePruefobjekt == "Feuerwehrhelm"
    
    def test_infos_hinzufuegen(self):
        """Test: Info-Daten werden korrekt hinzugefügt"""
        pruefanweisung = Pruefanweisung()
        pruefanweisung.infosHinzufuegen(
            pruefart="Sichtprüfung",
            pruefvorgabe="DIN 12345",
            prueffrist="12 Monate",
            sachkundiger="Max Mustermann"
        )
        
        assert pruefanweisung.pruefart == "Sichtprüfung"
        assert pruefanweisung.pruefvorgabe == "DIN 12345"
        assert pruefanweisung.prueffrist == "12 Monate"
        assert pruefanweisung.sachkundiger == "Max Mustermann"
    
    def test_infos_hinzufuegen_teilweise(self):
        """Test: Info-Daten können teilweise hinzugefügt werden"""
        pruefanweisung = Pruefanweisung()
        pruefanweisung.infosHinzufuegen(pruefart="Sichtprüfung")
        
        assert pruefanweisung.pruefart == "Sichtprüfung"
        assert pruefanweisung.pruefvorgabe == ''
        assert pruefanweisung.prueffrist == ''
    
    def test_vorgaben_hinzufuegen(self):
        """Test: Vorgaben-Text wird hinzugefügt"""
        pruefanweisung = Pruefanweisung()
        text = "Dies ist ein Vorgaben-Text"
        pruefanweisung.vorgabenHinzufuegen(text)
        
        assert pruefanweisung.vorgabenText == text
    
    def test_pruefablauf_hinzufuegen(self):
        """Test: Prüfablauf-Text wird hinzugefügt"""
        pruefanweisung = Pruefanweisung()
        text = "Prüfablauf-Schritte"
        pruefanweisung.pruefablaufHinzufuegen(text)
        
        assert pruefanweisung.pruefablaufText == text
    
    def test_eigenschaft_hinzufuegen(self):
        """Test: Eigenschaft wird zur Liste hinzugefügt"""
        pruefanweisung = Pruefanweisung()
        assert len(pruefanweisung.eigenschaften) == 0
        
        pruefanweisung.eigenschaftHinzufuegen("Schutz", "Helm prüfen", [])
        assert len(pruefanweisung.eigenschaften) == 1
        assert pruefanweisung.eigenschaften[0].kategorie == "Schutz"
        assert pruefanweisung.eigenschaften[0].beschreibung == "Helm prüfen"
    
    def test_eigenschaft_hinzufuegen_mit_bildern(self):
        """Test: Eigenschaft mit Bildern wird hinzugefügt"""
        pruefanweisung = Pruefanweisung()
        bilder = [("bild1.jpg", "Beschreibung 1"), ("bild2.jpg", "Beschreibung 2")]
        pruefanweisung.eigenschaftHinzufuegen("Schutz", "Helm prüfen", bilder)
        
        assert len(pruefanweisung.eigenschaften) == 1
        assert len(pruefanweisung.eigenschaften[0].bilder) == 2
    
    def test_mehrere_eigenschaften_hinzufuegen(self):
        """Test: Mehrere Eigenschaften können hinzugefügt werden"""
        pruefanweisung = Pruefanweisung()
        pruefanweisung.eigenschaftHinzufuegen("Schutz", "Helm", [])
        pruefanweisung.eigenschaftHinzufuegen("Funktion", "Atemschutz", [])
        pruefanweisung.eigenschaftHinzufuegen("Optik", "Sichtfeld", [])
        
        assert len(pruefanweisung.eigenschaften) == 3
        assert pruefanweisung.eigenschaften[0].kategorie == "Schutz"
        assert pruefanweisung.eigenschaften[1].kategorie == "Funktion"
        assert pruefanweisung.eigenschaften[2].kategorie == "Optik"
    
    def test_hinweis_hinzufuegen(self):
        """Test: Hinweis wird hinzugefügt"""
        pruefanweisung = Pruefanweisung()
        hinweis = "Wichtiger Hinweis zur Prüfung"
        pruefanweisung.hinweisHinzufuegen(hinweis)
        
        assert pruefanweisung.hinweis == hinweis
    
    def test_str_representation(self):
        """Test: String-Darstellung der Prüfanweisung"""
        pruefanweisung = Pruefanweisung()
        pruefanweisung.auswahlHinzufuegen("bild.jpg", "Test-Objekt")
        pruefanweisung.vorgabenHinzufuegen("Vorgaben-Text")
        pruefanweisung.eigenschaftHinzufuegen("Kategorie", "Beschreibung", [])
        
        str_repr = str(pruefanweisung)
        assert "Test-Objekt" in str_repr
        assert "Vorgaben-Text" in str_repr
        assert "Kategorie" in str_repr

