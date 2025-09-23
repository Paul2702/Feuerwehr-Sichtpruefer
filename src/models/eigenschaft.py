

class Eigenschaft:
    def __init__(self, kategorie: str, beschreibung: str, bilder = []):
        self.kategorie = kategorie
        self.beschreibung = beschreibung
        self.bilder = bilder

    def __str__(self):
        return f"- [{self.kategorie}] {self.beschreibung} {self.bilder}"