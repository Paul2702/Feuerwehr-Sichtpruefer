from typing import Optional
from src.models.eigenschaft import Eigenschaft
from src.models.eigenschaftpruefung import Eigenschaftspruefung
from src.models.pruefanweisung import Pruefanweisung


class Sichtpruefung:
    def __init__(self) -> None:
        self.pruefanweisung: Optional[Pruefanweisung] = None
        self.lagerort: str = ''
        self.nummer: str = ''
        self.einsatzbereit: bool = False
        self.bemerkungen: str = ''
        self.pruefer: str = ''
        self.datum: str = ''
        self.eigenschaftspruefungen: list[Eigenschaftspruefung] = []  

    def labelsBefuellen(self, pruefanweisung: Pruefanweisung) -> None:
        self.pruefanweisung = pruefanweisung

    def eigenschaftspruefungHinzufuegen(self, kategorie: str, beschreibung: str, bilder: list[tuple[str | None, str]] = [], keinHandlungsbedarf: bool = True, massnahmen: str = '') -> None:
        eigenschaft: Eigenschaft = Eigenschaft(kategorie, beschreibung, bilder)
        self.eigenschaftspruefungen.append(Eigenschaftspruefung(eigenschaft, keinHandlungsbedarf, massnahmen))

    def pruefErgebnisEinfuegen(self, eigenschaftsIndex: int, keinHandlungsbedarf: bool = True, massnahmen: str = '') -> None:
        self.eigenschaftspruefungen[eigenschaftsIndex].setKeinHandlungsbedarf(keinHandlungsbedarf)
        self.eigenschaftspruefungen[eigenschaftsIndex].setMassnahmen(massnahmen)

    def finalesErgebnisEinfuegen(self, lagerort: str, nummer: str, einsatzbereit: bool, pruefer: str, datum: str, bemerkungen: str = '') -> None:
        self.lagerort = lagerort
        self.nummer = nummer
        self.einsatzbereit = einsatzbereit
        self.bemerkungen = bemerkungen
        self.pruefer = pruefer
        self.datum = datum