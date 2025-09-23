from src.models.eigenschaft import Eigenschaft
from src.models.eigenschaftpruefung import Eigenschaftspruefung
from src.models.pruefanweisung import Pruefanweisung


class Sichtpruefung:
    def __init__(self):
        self.pruefanweisung = None
        self.lagerort = ''
        self.nummer = ''
        self.einsatzbereit = ''
        self.bemerkungen = ''
        self.pruefer = ''
        self.datum = ''
        self.eigenschaftspruefungen = []  

    def labelsBefuellen(self, pruefanweisung: Pruefanweisung):
        self.pruefanweisung = pruefanweisung

    def eigenschaftspruefungHinzufuegen(self, kategorie: str, beschreibung: str, bilder= [], keinHandlungsbedarf = True, massnahmen = ''):
        eigenschaft = Eigenschaft(kategorie, beschreibung, bilder)
        self.eigenschaftspruefungen.append(Eigenschaftspruefung(eigenschaft, keinHandlungsbedarf, massnahmen))

    def pruefErgebnisEinfuegen(self, eigenschaftsIndex: int, keinHandlungsbedarf = True, massnahmen = ''):
        self.eigenschaftspruefungen[eigenschaftsIndex].setKeinHandlungsbedarf(keinHandlungsbedarf)
        self.eigenschaftspruefungen[eigenschaftsIndex].setMassnahmen(massnahmen)

    def finalesErgebnisEinfuegen(self, lagerort: str, nummer: str, einsatzbereit: bool, pruefer: str, datum: str, bemerkungen = ''):
        self.lagerort = lagerort
        self.nummer = nummer
        self.einsatzbereit = einsatzbereit
        self.bemerkungen = bemerkungen
        self.pruefer = pruefer
        self.datum = datum