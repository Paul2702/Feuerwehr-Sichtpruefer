from src.models.eigenschaft import Eigenschaft


class Pruefanweisung:
    def __init__(self):
        self.pfadVorschauBild = ''
        self.namePruefobjekt = ''
        self.pruefart = ''
        self.pruefvorgabe = ''
        self.pruefvorgabeZusatz = ''
        self.prueffrist = ''
        self.sachkundiger = ''
        self.zusatzausbildung = ''
        self.hersteller = ''
        self.aussonderungsfrist = ''
        self.vorgabenText = ''
        self.pruefablaufText = ''
        self.eigenschaften = []
        self.hinweis = ''

    def auswahlHinzufuegen(self, pfadVorschauBild: str, namePruefobjekt: str):
        self.pfadVorschauBild = pfadVorschauBild
        self.namePruefobjekt = namePruefobjekt

    def infosHinzufuegen(self, pruefart = '', pruefvorgabe = '', pruefvorgabeZusatz = '', prueffrist = '', sachkundiger = '', zusatzausbildung = '', hersteller = '', aussonderungsfrist = ''):
        self.pruefart = pruefart
        self.pruefvorgabe = pruefvorgabe
        self.pruefvorgabeZusatz = pruefvorgabeZusatz
        self.prueffrist = prueffrist
        self.sachkundiger = sachkundiger
        self.zusatzausbildung = zusatzausbildung
        self.hersteller = hersteller
        self.aussonderungsfrist = aussonderungsfrist

    def vorgabenHinzufuegen(self, text = ''):
        self.vorgabenText = text

    def pruefablaufHinzufuegen(self, text = ''):
        self.pruefablaufText = text

    def eigenschaftHinzufuegen(self, kategorie: str, beschreibung: str, bilder = []):
        self.eigenschaften.append(Eigenschaft(kategorie, beschreibung, bilder))

    def hinweisHinzufuegen(self, hinweis: str):
        self.hinweis = hinweis

    def __str__(self):
        eigenschaften_text = "\n".join([str(e) for e in self.eigenschaften])
        return (f"Prüfanweisung für: {self.namePruefobjekt}\n"
                f"Vorschau: {self.pfadVorschauBild}\n"
                f"Disclaimer: {self.vorgabenText}\n"
                f"Eigenschaften:\n{eigenschaften_text}")