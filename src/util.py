import os
import bleach
from bs4 import BeautifulSoup



def getUniqueFilename(directory, filename):
    base, ext = os.path.splitext(filename)  # Trennt Name und Endung (z.B. "bild", ".jpg")
    counter = 1
    newFilename = filename

    while os.path.exists(os.path.join(directory, newFilename)):
        newFilename = f"{base}_{counter}{ext}"  # Fügt Nummerierung hinzu
        counter += 1
    
    return newFilename

def cleanHtml(htmlText: str):
    # Erlaubte HTML-Tags und Attribute für ReportLab
    allowed_tags = ["b", "i", "u", "br", "font"]
    allowed_attrs = {"font": ["color"]}
    # 🔥 1. Mit BeautifulSoup den <body>-Inhalt extrahieren
    soup = BeautifulSoup(htmlText, "html.parser")
    body_content = str(soup.body) if soup.body else htmlText  # Falls kein <body>, dann originaler Text
    # Bereinigter HTML-Text für ReportLab
    clean_text = bleach.clean(body_content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    clean_text = clean_text.replace("<br>", "\n").replace("<br/>", "\n")
    return clean_text