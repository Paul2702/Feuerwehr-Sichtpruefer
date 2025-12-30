"""
Tests für das Eigenschaft-Modell.
Vergleichbar mit JUnit-Tests in Java, aber mit pytest-Syntax.
"""
import pytest
from src.models.eigenschaft import Eigenschaft


class TestEigenschaft:
    """Test-Klasse für Eigenschaft (ähnlich wie @Test-Klassen in JUnit)"""
    
    def test_eigenschaft_initialisierung(self):
        """Test: Eigenschaft wird korrekt initialisiert"""
        # Arrange (Vorbereitung)
        kategorie = "Schutz"
        beschreibung = "Helm ist intakt"
        bilder = [("pfad1.jpg", "Beschreibung 1")]
        
        # Act (Ausführung)
        eigenschaft = Eigenschaft(kategorie, beschreibung, bilder)
        
        # Assert (Überprüfung) - in Python einfach mit assert
        assert eigenschaft.kategorie == kategorie
        assert eigenschaft.beschreibung == beschreibung
        assert eigenschaft.bilder == bilder
    
    def test_eigenschaft_ohne_bilder(self):
        """Test: Eigenschaft kann ohne Bilder erstellt werden"""
        eigenschaft = Eigenschaft("Kategorie", "Beschreibung", [])
        assert eigenschaft.kategorie == "Kategorie"
        assert eigenschaft.beschreibung == "Beschreibung"
        assert eigenschaft.bilder == []
    
    def test_eigenschaft_str_representation(self):
        """Test: String-Darstellung der Eigenschaft"""
        eigenschaft = Eigenschaft("Test", "Beschreibung", [("bild.jpg", "Text")])
        str_repr = str(eigenschaft)
        assert "Test" in str_repr
        assert "Beschreibung" in str_repr
        assert "bild.jpg" in str_repr or "Text" in str_repr
    
    def test_eigenschaft_mehrere_bilder(self):
        """Test: Eigenschaft mit mehreren Bildern"""
        bilder = [
            ("pfad1.jpg", "Beschreibung 1"),
            ("pfad2.jpg", "Beschreibung 2"),
            ("pfad3.jpg", "Beschreibung 3")
        ]
        eigenschaft = Eigenschaft("Kategorie", "Beschreibung", bilder)
        assert len(eigenschaft.bilder) == 3
        assert eigenschaft.bilder[0] == ("pfad1.jpg", "Beschreibung 1")

