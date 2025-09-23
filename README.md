# Sichtpruefer (Work in Progress)
Ein Programm, dass Nutzer Schritt für Schritt durch die Sichtprüfung von Einsatzkleidung führt.

Zum Konvertieren der UI-Dateien folgende Befehle ausführen:
pyside6-uic ui\ui_main.ui -o ui\ui_main.py
pyside6-rcc resources\uiResources.qrc -o resources\uiResources_rc.py

Und in ui_main.py "import uiResources_rc" zu "import resources.uiResources_rc" ändern.

Konfigurationsdateien (Feuerwehr Logos und config) mittels 
git update-index --skip-worktree config.yaml
ignorieren und mittels
git update-index --no-skip-worktree config.yaml
nach Platzhalteränderungen wieder für commits berücksichtigen.

Zum Starten in Sichtpruefer "python -m src.main" ausführen.

Infos zur Projektstruktur:
- .venv: Virtuelle Python Umgebung mit zusätzlich installierten Paketen
- assets: Bilder und Icons die in der UI genutzt werden
- data: Ablageort der Prüfanweisungen
- resources: resource-Dateien mit Infos über den speicherorte der assets
- src: Hauptcode
- ui: ui-Dateien, die mittels Qt-Designer erstellt wurden
- __init__ Dateien dienen dazu, ordnerübergreifend auf Code zugreifen zu können

Haftungsausschluss:

Dieses Programm wird ohne jegliche Garantie bereitgestellt. Die Nutzung erfolgt auf eigene Verantwortung. 
Der Autor übernimmt keine Haftung für Schäden oder Datenverlust, die durch die Nutzung dieses Programms entstehen.

Hinweis zur Verwendung von Symbolen:

In dieser Anwendung werden das Stauferlöwen-Signet und das Logo der Feuerwehr Bischweier verwendet. 
Diese Symbole sind geschützt und dürfen nur gemäß den Vorgaben des Landesfeuerwehrverbands Baden-Württemberg (LFV BW) genutzt werden. 
Für weitere Informationen zur zulässigen Verwendung siehe: 
https://www.lfs-bw.de/fileadmin/LFS-BW/themen/gesetze_vorschriften/verwaltungsvorschriften/feuerwehrbekleidung/signet_emblem/dokumente/_Hinweise_Feuerwehrsignet.pdf
