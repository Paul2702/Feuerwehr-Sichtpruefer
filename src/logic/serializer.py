
import html
import os
import xml.etree.ElementTree as ET

from src.models.pruefanweisung import Pruefanweisung
from src.models.sichtpruefung import Sichtpruefung
from src.util import getUniqueFilename

pruefanweisungenDir = "data/pruefanweisungen"
pruefanweisungenXmlPfad="data/pruefanweisungen.xml"


def speicherePruefanweisungXml(pruefanweisung: Pruefanweisung):
    root = ET.Element("Pruefanweisung")
    ET.SubElement(root, "Name").text = pruefanweisung.namePruefobjekt
    ET.SubElement(root, "VorschauBildPfad").text = pruefanweisung.pfadVorschauBild
    ET.SubElement(root, "Pruefart").text = pruefanweisung.pruefart
    ET.SubElement(root, "Pruefvorgabe").text = pruefanweisung.pruefvorgabe
    ET.SubElement(root, "PruefvorgabeZusatz").text = pruefanweisung.pruefvorgabeZusatz
    ET.SubElement(root, "Prueffrist").text = pruefanweisung.prueffrist
    ET.SubElement(root, "Sachkundiger").text = pruefanweisung.sachkundiger
    ET.SubElement(root, "Zusatzausbildung").text = pruefanweisung.zusatzausbildung
    ET.SubElement(root, "Hersteller").text = pruefanweisung.hersteller
    ET.SubElement(root, "Aussonderungsfrist").text = pruefanweisung.aussonderungsfrist
    ET.SubElement(root, "VorgabenText").text = html.escape(pruefanweisung.vorgabenText)
    ET.SubElement(root, "PruefablaufText").text = html.escape(pruefanweisung.pruefablaufText)

    eigenschaftenElement = ET.SubElement(root, "Eigenschaften")
    for eigenschaft in pruefanweisung.eigenschaften:
        eigenschaftElement = ET.SubElement(eigenschaftenElement, "Eigenschaft")
        ET.SubElement(eigenschaftElement, "Kategorie").text = eigenschaft.kategorie
        ET.SubElement(eigenschaftElement, "Beschreibung").text = eigenschaft.beschreibung
        bilderElement = ET.SubElement(eigenschaftElement, "Bilder")
        for bildPfad, bildBeschreibung in eigenschaft.bilder:
            bildElement = ET.SubElement(bilderElement, "Bild")
            ET.SubElement(bildElement, "BildPfad").text = bildPfad
            ET.SubElement(bildElement, "BildBeschreibung").text = bildBeschreibung
            
    ET.SubElement(root, "Hinweis").text = pruefanweisung.hinweis

    tree = ET.ElementTree(root)
    namePruefobjekt = pruefanweisung.namePruefobjekt
    fileName = f"{namePruefobjekt}.xml"
    fileName = getUniqueFilename(pruefanweisungenDir, fileName)
    filePath = os.path.join(pruefanweisungenDir, fileName)
    tree.write(filePath, encoding="utf-8", xml_declaration=True)
    return filePath

def ladePruefanweisungXml(xmlPfad):
    try:
        with open(xmlPfad, "r", encoding="utf-8") as file:
            xmlInhalt = file.read()
        
        root = ET.fromstring(xmlInhalt)  # XML parsen
        print(f"XML erfolgreich geladen: {xmlPfad}")

        sichtpruefung = Sichtpruefung()

        # Tags richtig auslesen
        namePruefobjekt = root.find("Name").text
        pfadVorschauBild = root.find("VorschauBildPfad").text
        pruefart = root.find("Pruefart").text
        pruefvorgabe = root.find("Pruefvorgabe").text
        pruefvorgabeZusatz = root.find("PruefvorgabeZusatz").text
        prueffrist = root.find("Prueffrist").text
        sachkundiger = root.find("Sachkundiger").text
        zusatzausbildung = root.find("Zusatzausbildung").text
        hersteller = root.find("Hersteller").text
        aussonderungsfrist = root.find("Aussonderungsfrist").text
        vorgabenText = html.unescape(root.find("VorgabenText").text)
        pruefablaufText = html.unescape(root.find("PruefablaufText").text)

        pruefanweisung = Pruefanweisung()
        pruefanweisung.auswahlHinzufuegen(pfadVorschauBild, namePruefobjekt)
        pruefanweisung.infosHinzufuegen(pruefart, pruefvorgabe, pruefvorgabeZusatz, prueffrist, sachkundiger, zusatzausbildung, hersteller, aussonderungsfrist)
        pruefanweisung.vorgabenHinzufuegen(vorgabenText)
        pruefanweisung.pruefablaufHinzufuegen(pruefablaufText)

        eigenschaften = root.find("Eigenschaften")
        for eigenschaft in eigenschaften.findall("Eigenschaft"):
            kategorie = eigenschaft.find("Kategorie").text
            beschreibung = eigenschaft.find("Beschreibung").text

            eigenschaftBilder = []
            bilder = eigenschaft.find("Bilder")
            for bild in bilder.findall("Bild"):
                bildPfad = bild.find("BildPfad").text
                bildBeschreibung = bild.find("BildBeschreibung").text
                eigenschaftBilder.append((bildPfad, bildBeschreibung))

            sichtpruefung.eigenschaftspruefungHinzufuegen(kategorie, beschreibung, eigenschaftBilder)
            
        hinweis = root.find("Hinweis").text
        pruefanweisung.hinweisHinzufuegen(hinweis)
        sichtpruefung.labelsBefuellen(pruefanweisung)


        return sichtpruefung
    except Exception as e:
        print(f"Fehler beim Laden der XML-Datei: {e}")

def addToPruefanweisungenXml(pruefanweisung: Pruefanweisung, pruefanweisungXmlPfad: str):
    try:
        tree = ET.parse(pruefanweisungenXmlPfad)
        root = tree.getroot()
    except FileNotFoundError:
        root = ET.Element("Pruefanweisungen")
        tree = ET.ElementTree(root)

    # Neue Prüfanweisung erstellen
    pruefanweisungElement = ET.SubElement(root, "Pruefanweisung")
    ET.SubElement(pruefanweisungElement, "Name").text = pruefanweisung.namePruefobjekt
    ET.SubElement(pruefanweisungElement, "VorschauBildPfad").text = pruefanweisung.pfadVorschauBild
    ET.SubElement(pruefanweisungElement, "PruefanweisungXmlPfad").text = pruefanweisungXmlPfad

    tree.write(pruefanweisungenXmlPfad, encoding="utf-8", xml_declaration=True)

def ladePruefanweisungenXml():
    tree = ET.parse(pruefanweisungenXmlPfad)
    root = tree.getroot()

    pruefanweisungen = []
    for pruefanweisung in root.findall("Pruefanweisung"):
        name = pruefanweisung.find("Name").text
        vorschau_bild = pruefanweisung.find("VorschauBildPfad").text
        pfad = pruefanweisung.find("PruefanweisungXmlPfad").text
        pruefanweisungen.append({
            "Name": name,
            "VorschauBildPfad": vorschau_bild,
            "PruefanweisungXmlPfad": pfad
        })

    return pruefanweisungen

def eigenschaftenNachKategorienGruppieren(eigenschaften):
    kategorien = {}
    for eigenschaft in eigenschaften:
        kategorie = eigenschaft.kategorie
        if kategorie not in kategorien:
            kategorien[kategorie] = []
        kategorien[kategorie].append(eigenschaft)
    return kategorien

def eigenschaftspruefungenNachKategorienGruppieren(eigenschaftspruefungen):
    kategorien = {}
    for eigenschaftspruefung in eigenschaftspruefungen:
        kategorie = eigenschaftspruefung.eigenschaft.kategorie
        if kategorie not in kategorien:
            kategorien[kategorie] = []
        kategorien[kategorie].append(eigenschaftspruefung)
    return kategorien
