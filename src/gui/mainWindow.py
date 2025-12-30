import os
import shutil
import webbrowser
import yaml
import logging
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QLabel, QSizePolicy, QPlainTextEdit, QSpacerItem
from PySide6.QtGui import QIcon, QCursor, QPixmap
from PySide6.QtCore import Qt, QSize, QCoreApplication
from src.gui.navigation import NavigationController
from src.gui.pages import Page
from src.gui.viewHandler import ViewHandler
from src.logic.state import AppState
from src.logic.vorgang import Vorgang
from src.logic.validators import ValidationController
from src.models.pruefanweisung import Pruefanweisung
from util import getUniqueFilename
from ui.ui_main import Ui_MainWindow

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.debug("MainWindow.__init__() aufgerufen")
        
        self.ui = Ui_MainWindow()  
        self.ui.setupUi(self)
        logger.debug("UI-Setup abgeschlossen")

        try:
            with open("config.yaml", "r", encoding="utf-8") as config:
                self.config = yaml.safe_load(config)
            logger.info("Konfigurationsdatei erfolgreich geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfigurationsdatei: {e}", exc_info=True)
            raise
        
        self.state = AppState(self.ui)
        logger.debug("AppState initialisiert")
        
        self.navigator = NavigationController(self.ui, self.state)
        logger.debug("NavigationController initialisiert")
        
        self.validator = ValidationController(self, self.ui, self.state)
        logger.debug("ValidationController initialisiert")
        
        self.view_handler = ViewHandler(self, self.navigator, self.ui, self.state)
        logger.debug("ViewHandler initialisiert")

        self.assetsDir = "assets/images"
        logger.debug(f"Assets-Verzeichnis: {self.assetsDir}")

        # Buttons verbinden
        # Navigationsleiste
        self.ui.feuerwehrLogo.clicked.connect(self.feuerwehrLogoGeklickt)
        self.ui.zurueck.clicked.connect(self.zurueckGeklickt)
        self.ui.weiter.clicked.connect(self.weiterGeklickt)
        self.ui.hinzufuegen.clicked.connect(self.hinzufuegenGeklickt)
        self.ui.fertig.clicked.connect(self.fertigGeklickt)
        self.ui.loeschen.clicked.connect(self.loeschenGeklickt)
        self.ui.abbrechen.clicked.connect(self.abbrechenGeklickt)

        # Hauptmenü
        self.ui.sichtpruefungStarten.clicked.connect(self.startSichtpruefung)
        self.ui.neuePruefanweisung.clicked.connect(self.createPruefanweisung)
        self.ui.pruefanweisungBearbeiten.clicked.connect(self.editPruefanweisung)
        self.ui.pruefanweisungLoeschen.clicked.connect(self.deletePruefanweisung)

        # Prüfanweisung Auswahl
        self.ui.auswahlBildEinfuegen.setProperty("isPlaceholder", True)
        self.ui.auswahlBildEinfuegen.clicked.connect(self.bildEinfuegenPruefanweisungAuswahl)

        # Prüfanweisung Eigenschaft
        self.ui.eigenschaftBildEinfuegen.setProperty("isPlaceholder", True)
        self.ui.eigenschaftBildEinfuegen.clicked.connect(self.bildEinfuegenPruefanweisungEigenschaft)
        
        # Erfolgreich Abgeschlossen
        self.ui.zumHauptmenue.clicked.connect(self.zurueckZumHauptmenueGeklickt)


    # UI Steuerung
    # Navigationsleiste
    def feuerwehrLogoGeklickt(self):
        url = self.config["feuerwehrHompageURL"]
        logger.info(f"Feuerwehr-Logo geklickt, öffne URL: {url}")
        webbrowser.open(url)

    def zurueckGeklickt(self):
        logger.warning("Zurück-Button geklickt, aber noch nicht implementiert")

    def weiterGeklickt(self):
        logger.warning("Weiter-Button geklickt, aber noch nicht implementiert")

    def hinzufuegenGeklickt(self):
        logger.info("Hinzufügen-Button geklickt")
        istSeiteValide, statusNachricht = self.validator.validiereHinzufuegenPruefanweisungEigenschaft()
        if istSeiteValide:
            logger.debug("Validierung erfolgreich, speichere Seiteninhalte")
            self.state.speichereSeiteninhalte(Page.PRUEFANWEISUNG_EIGENSCHAFT)
            self.view_handler.resetAlleFelderAufSeite(Page.PRUEFANWEISUNG_EIGENSCHAFT)
            logger.info("Eigenschaft hinzugefügt und Felder zurückgesetzt")
        elif statusNachricht:
            logger.warning(f"Validierung fehlgeschlagen: {statusNachricht}")
            self.statusBarMeldung(statusNachricht)

    def fertigGeklickt(self):
        currentPage = self.state.get_current_page()
        logger.info(f"Fertig-Button geklickt auf Seite: {currentPage}")
        istSeiteValide, statusNachricht = self.validator.istSeiteValide(currentPage)
        if istSeiteValide:
            logger.debug("Seite ist valide, speichere Inhalte")
            self.state.speichereSeiteninhalte(currentPage)
            nextPage = self.navigator.get_next_page()
            logger.debug(f"Nächste Seite: {nextPage}")
            self.view_handler.ladeSeiteninhalte(nextPage)
            self.navigator.goto(nextPage)
            logger.info(f"Navigation zu Seite: {nextPage}")
        elif statusNachricht:
            logger.warning(f"Validierung fehlgeschlagen: {statusNachricht}")
            self.statusBarMeldung(statusNachricht)


    def loeschenGeklickt(self):
        logger.info("Löschen-Button geklickt")
        self.loeschenPruefanweisungEigenschaft()
        
    def abbrechenGeklickt(self):
        logger.info("Abbrechen-Button geklickt, zeige Bestätigungsdialog")
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Bestätigung")
        msg_box.setWindowIcon(QIcon(":/icons/assets/icons/Stauferlöwe.png"))
        msg_box.setText("Bist du sicher, dass du abbrechen und ins Hauptmenü zurückkehren möchtest?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        antwort = msg_box.exec()

        if antwort == QMessageBox.Yes:
            logger.info("Benutzer hat Abbrechen bestätigt, kehre zum Hauptmenü zurück")
            self.state.aktuellerVorgang = Vorgang.HAUPTMENUE
            self.view_handler.resetAlleFelder()
            self.navigator.goto(Page.HAUPTMENUE)
        else:
            logger.debug("Abbrechen abgebrochen")


    # Seiten Funktionen 
    # Hauptmenü
    def startSichtpruefung(self):
        logger.info("Sichtprüfung wird gestartet")
        if self.auswahlVorbereiten():
            self.state.aktuellerVorgang = Vorgang.SICHTPRUEFUNG
            self.ui.abbrechen.setEnabled(True)
            self.navigator.goto(Page.SICHTPRUEFUNG_AUSWAHL)
            logger.info("Sichtprüfung gestartet, navigiere zur Auswahlseite")
        else:
            logger.warning("Sichtprüfung konnte nicht gestartet werden (keine Prüfanweisungen gefunden)")

    def createPruefanweisung(self):
        logger.info("Neue Prüfanweisung wird erstellt")
        self.state.aktuellerVorgang = Vorgang.PRUEFANWEISUNG_ERSTELLEN
        self.state.pruefanweisungManager.pruefanweisung = Pruefanweisung()
        self.ui.fertig.setEnabled(True)
        self.ui.abbrechen.setEnabled(True)
        self.navigator.goto(Page.PRUEFANWEISUNG_AUSWAHL)
        logger.info("Prüfanweisung-Erstellung gestartet, navigiere zur Auswahlseite")

    def editPruefanweisung(self):
        logger.warning("Prüfanweisung bearbeiten aufgerufen, aber noch nicht implementiert")
        # TODO

    def deletePruefanweisung(self):
        logger.warning("Prüfanweisung löschen aufgerufen, aber noch nicht implementiert")
        # TODO

    # Sichtprüfung Auswahl
    def auswahlVorbereiten(self):
        logger.debug("Bereite Sichtprüfung-Auswahl vor")
        if not os.path.exists("data/pruefanweisungen.xml"):
            logger.warning("Prüfanweisungen-XML-Datei nicht gefunden")
            self.statusBar().showMessage("Keine vorhandenen Prüfanweisungen gefunden, die zur Auswahl stehen.", 3000)
            return False
        logger.debug("Lade Seiteninhalte für Sichtprüfung-Auswahl")
        self.view_handler.ladeSeiteninhalte(Page.SICHTPRUEFUNG_AUSWAHL)
        return True

    # Prüfanweisung Auswahl    
    def bildEinfuegenPruefanweisungAuswahl(self):
        logger.info("Bild für Prüfanweisung-Auswahl wird eingefügt")
        filePath = self.bildInProjektEinfuegen()
        if filePath:
            logger.debug(f"Bild erfolgreich eingefügt: {filePath}")
            self.ui.auswahlBildEinfuegen.setIcon(QIcon(filePath))
            self.ui.auswahlBildEinfuegen.setIconSize(self.ui.auswahlBildEinfuegen.size())
            self.ui.auswahlBildEinfuegen.setProperty("isPlaceholder", False)
            self.ui.auswahlBildEinfuegen.setProperty("imagePath", filePath)
            self.ui.auswahlBildEinfuegen.setStyleSheet(u"QPushButton {\n"
"border:none;\n"
"border-radius:20;\n"
"width: 371;\n"
"height: 371;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	background-color: rgb(50, 50, 50);\n"
"}")
        else:
            logger.debug("Bild-Einfügen abgebrochen")

    # Prüfanweisung Schadensbilder
    #TODO

    # Prüfanweisung Eigenschaft
        
    def loeschenPruefanweisungEigenschaft(self):
        logger.info(f"Lösche Prüfanweisung-Eigenschaft (Index: {self.state.aktuelleEigenschaftIndex})")
        self.view_handler.resetAlleFelderAufSeite(Page.PRUEFANWEISUNG_EIGENSCHAFT)
        if self.state.aktuelleEigenschaftIndex > 0:
            self.state.aktuelleEigenschaftIndex -= 1
            logger.debug(f"Eigenschaftsindex reduziert auf: {self.state.aktuelleEigenschaftIndex}")
    
    def bildEinfuegenPruefanweisungEigenschaft(self):
        logger.info("Bild für Prüfanweisung-Eigenschaft wird eingefügt")
        bildPfad = self.bildInProjektEinfuegen()
        if bildPfad:
            logger.debug(f"Bild erfolgreich eingefügt: {bildPfad}")
            # Bild und Textfeld über Button einfügen
            anzahlWidgets = self.ui.verticalLayout_11.count()
            if isinstance(self.ui.verticalLayout_11.itemAt(anzahlWidgets-1), QSpacerItem):
                item = self.ui.verticalLayout_11.takeAt(anzahlWidgets-1)
                if item.widget():
                    item.widget().deleteLater()
                anzahlWidgets -= 1
            eigenschaftBildEinfuegen = QLabel(self.ui.bildEditor)
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(eigenschaftBildEinfuegen.sizePolicy().hasHeightForWidth())
            eigenschaftBildEinfuegen.setSizePolicy(sizePolicy)
            eigenschaftBildEinfuegen.setMaximumSize(QSize(540, 16777215))
            eigenschaftBildEinfuegen.setText("")
            eigenschaftBildEinfuegen.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            pixmap = QPixmap(bildPfad)
            scaledPixmap = pixmap.scaled(540, pixmap.height() * (540 / pixmap.width()), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            eigenschaftBildEinfuegen.setPixmap(scaledPixmap)
            eigenschaftBildEinfuegen.setProperty("isPlaceholder", False)
            eigenschaftBildEinfuegen.setProperty("imagePath", bildPfad)
            eigenschaftBildEinfuegen.setStyleSheet(u"QPushButton {\n"
                "border:none;\n"
                "height: 304;\n"
                "}")
            self.ui.verticalLayout_11.insertWidget(anzahlWidgets-1 ,eigenschaftBildEinfuegen)

            eigenschaftBildBeschreibungEingeben = QPlainTextEdit(self.ui.bildEditor)
            sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            sizePolicy8.setHorizontalStretch(0)
            sizePolicy8.setVerticalStretch(0)
            sizePolicy8.setHeightForWidth(eigenschaftBildBeschreibungEingeben.sizePolicy().hasHeightForWidth())
            eigenschaftBildBeschreibungEingeben.setSizePolicy(sizePolicy8)
            eigenschaftBildBeschreibungEingeben.setMinimumSize(QSize(0, 0))
            eigenschaftBildBeschreibungEingeben.setMaximumSize(QSize(540, 78))
            eigenschaftBildBeschreibungEingeben.setStyleSheet(u"font: 16pt \"Segoe UI\";")
            eigenschaftBildBeschreibungEingeben.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Bildbeschreibung eingeben...", None))
            self.ui.verticalLayout_11.insertWidget(anzahlWidgets ,eigenschaftBildBeschreibungEingeben)

            bildEditorSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.ui.verticalLayout_11.addItem(bildEditorSpacer)

    # Erfolgreich abgeschlossen
    def zurueckZumHauptmenueGeklickt(self):
        logger.info("Zurück zum Hauptmenü geklickt")
        self.state.aktuellerVorgang = Vorgang.HAUPTMENUE
        self.view_handler.resetAlleFelder()
        self.navigator.goto(Page.HAUPTMENUE)

    # Allgemeine UI Funktionen
    def bildInProjektEinfuegen(self):
        logger.debug("Öffne Dateidialog für Bildauswahl")
        filePath, _ = QFileDialog.getOpenFileName(self, "Bild auswählen", "", "Bilder (*.png *.jpg *.jpeg)")
        if filePath:
            logger.info(f"Bild ausgewählt: {filePath}")
            os.makedirs(self.assetsDir, exist_ok=True)  # Falls assets-Ordner nicht existiert, erstellen
            logger.debug(f"Assets-Verzeichnis sichergestellt: {self.assetsDir}")

            # Neuen Pfad im assets-Ordner erstellen (selber Dateiname wie Original)
            fileName = os.path.basename(filePath)
            fileName = getUniqueFilename(self.assetsDir, fileName)
            newPath = os.path.join(self.assetsDir, fileName)
            logger.debug(f"Kopiere Bild nach: {newPath}")

            # Datei kopieren
            try:
                shutil.copy(filePath, newPath)
                logger.info(f"Bild erfolgreich kopiert: {newPath}")
                return newPath
            except Exception as e:
                logger.error(f"Fehler beim Kopieren des Bildes: {e}", exc_info=True)
                return None
        else:
            logger.debug("Bildauswahl abgebrochen")
            return None
        
    def statusBarMeldung(self, nachricht):
        self.statusBar().showMessage(nachricht, 3000)

# TODO: evtl. ungenutzte Bilder löschen