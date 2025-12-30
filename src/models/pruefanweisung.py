from typing import Optional
from src.models.eigenschaft import Eigenschaft


class Pruefanweisung:
    def __init__(self) -> None:
        self.pfadVorschauBild: str = ''
        self.namePruefobjekt: str = ''
        self.pruefart: str = ''
        self.pruefvorgabe: str = ''
        self.pruefvorgabeZusatz: str = ''
        self.prueffrist: str = ''
        self.sachkundiger: str = ''
        self.zusatzausbildung: str = ''
        self.hersteller: str = ''
        self.aussonderungsfrist: str = ''
        self.vorgabenText: str = ''
        self.pruefablaufText: str = ''
        self.eigenschaften: list[Eigenschaft] = []
        self.hinweis: str = ''

    def auswahlHinzufuegen(self, pfadVorschauBild: str, namePruefobjekt: str) -> None:
        self.pfadVorschauBild = pfadVorschauBild
        self.namePruefobjekt = namePruefobjekt

    def infosHinzufuegen(self, pruefart: str = '', pruefvorgabe: str = '', pruefvorgabeZusatz: str = '', prueffrist: str = '', sachkundiger: str = '', zusatzausbildung: str = '', hersteller: str = '', aussonderungsfrist: str = '') -> None:
        self.pruefart = pruefart
        self.pruefvorgabe = pruefvorgabe
        self.pruefvorgabeZusatz = pruefvorgabeZusatz
        self.prueffrist = prueffrist
        self.sachkundiger = sachkundiger
        self.zusatzausbildung = zusatzausbildung
        self.hersteller = hersteller
        self.aussonderungsfrist = aussonderungsfrist

    def vorgabenHinzufuegen(self, text: str = '') -> None:
        self.vorgabenText = text

    def pruefablaufHinzufuegen(self, text: str = '') -> None:
        self.pruefablaufText = text

    def eigenschaftHinzufuegen(self, kategorie: str, beschreibung: str, bilder: list[tuple[str | None, str]] = []) -> None:
        self.eigenschaften.append(Eigenschaft(kategorie, beschreibung, bilder))

    def hinweisHinzufuegen(self, hinweis: str) -> None:
        self.hinweis = hinweis

    def __str__(self) -> str:
        eigenschaften_text = "\n".join([str(e) for e in self.eigenschaften])
        return (f"Prüfanweisung für: {self.namePruefobjekt}\n"
                f"Vorschau: {self.pfadVorschauBild}\n"
                f"Disclaimer: {self.vorgabenText}\n"
                f"Eigenschaften:\n{eigenschaften_text}")