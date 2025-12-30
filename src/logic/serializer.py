
import html
import os
import logging
import xml.etree.ElementTree as ET

from src.models.pruefanweisung import Pruefanweisung
from src.models.sichtpruefung import Sichtpruefung
from src.util import getUniqueFilename

logger = logging.getLogger(__name__)

pruefanweisungenDir = "data/pruefanweisungen"
pruefanweisungenXmlPfad="data/pruefanweisungen.xml"


def speicherePruefanweisungXml(pruefanweisung: Pruefanweisung):
    logger.info(f"Speichere Prüfanweisung: {pruefanweisung.namePruefobjekt}")
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
    logger.debug(f"Speichere {len(pruefanweisung.eigenschaften)} Eigenschaften")
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
    
    try:
        os.makedirs(pruefanweisungenDir, exist_ok=True)
        tree.write(filePath, encoding="utf-8", xml_declaration=True)
        logger.info(f"Prüfanweisung erfolgreich gespeichert: {filePath}")
        return filePath
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Prüfanweisung: {e}", exc_info=True)
        raise

def ladePruefanweisungXml(xmlPfad):
    logger.info(f"Lade Prüfanweisung aus XML: {xmlPfad}")
    try:
        with open(xmlPfad, "r", encoding="utf-8") as file:
            xmlInhalt = file.read()
        
        root = ET.fromstring(xmlInhalt)  # XML parsen
        logger.debug(f"XML erfolgreich geparst: {xmlPfad}")

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
        eigenschafts_count = 0
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
            eigenschafts_count += 1
            logger.debug(f"Eigenschaft geladen: {kategorie} ({len(eigenschaftBilder)} Bilder)")
            
        hinweis = root.find("Hinweis").text
        pruefanweisung.hinweisHinzufuegen(hinweis)
        sichtpruefung.labelsBefuellen(pruefanweisung)

        logger.info(f"Prüfanweisung erfolgreich geladen: {pruefanweisung.namePruefobjekt} ({eigenschafts_count} Eigenschaften)")
        return sichtpruefung
    except Exception as e:
        logger.error(f"Fehler beim Laden der XML-Datei: {e}", exc_info=True)
        raise

def addToPruefanweisungenXml(pruefanweisung: Pruefanweisung, pruefanweisungXmlPfad: str):
    logger.info(f"Füge Prüfanweisung zur Übersichts-XML hinzu: {pruefanweisung.namePruefobjekt}")
    try:
        tree = ET.parse(pruefanweisungenXmlPfad)
        root = tree.getroot()
        logger.debug(f"Bestehende Prüfanweisungen-XML geladen: {pruefanweisungenXmlPfad}")
    except FileNotFoundError:
        logger.info(f"Prüfanweisungen-XML nicht gefunden, erstelle neue Datei: {pruefanweisungenXmlPfad}")
        root = ET.Element("Pruefanweisungen")
        tree = ET.ElementTree(root)

    # Neue Prüfanweisung erstellen
    pruefanweisungElement = ET.SubElement(root, "Pruefanweisung")
    ET.SubElement(pruefanweisungElement, "Name").text = pruefanweisung.namePruefobjekt
    ET.SubElement(pruefanweisungElement, "VorschauBildPfad").text = pruefanweisung.pfadVorschauBild
    ET.SubElement(pruefanweisungElement, "PruefanweisungXmlPfad").text = pruefanweisungXmlPfad

    try:
        tree.write(pruefanweisungenXmlPfad, encoding="utf-8", xml_declaration=True)
        logger.info(f"Prüfanweisung erfolgreich zur Übersichts-XML hinzugefügt")
    except Exception as e:
        logger.error(f"Fehler beim Schreiben der Prüfanweisungen-XML: {e}", exc_info=True)
        raise

def ladePruefanweisungenXml():
    logger.info(f"Lade Prüfanweisungen-Übersicht aus: {pruefanweisungenXmlPfad}")
    try:
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

        logger.info(f"{len(pruefanweisungen)} Prüfanweisungen geladen")
        return pruefanweisungen
    except FileNotFoundError:
        logger.warning(f"Prüfanweisungen-XML nicht gefunden: {pruefanweisungenXmlPfad}")
        return []
    except Exception as e:
        logger.error(f"Fehler beim Laden der Prüfanweisungen-XML: {e}", exc_info=True)
        return []

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
