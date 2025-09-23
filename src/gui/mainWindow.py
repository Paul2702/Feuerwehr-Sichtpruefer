import os
import shutil
import webbrowser
import yaml
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QLabel, QSizePolicy, QPlainTextEdit, QSpacerItem
from PySide6.QtGui import QIcon, QCursor, QPixmap
from PySide6.QtCore import Qt, QSize, QCoreApplication
from src.gui.navigation import NavigationController
from src.gui.pages import Page
from src.gui.viewHandler import ViewHandler
from src.logic.serializer import eigenschaftenNachKategorienGruppieren, eigenschaftspruefungenNachKategorienGruppieren, ladePruefanweisungXml, ladePruefanweisungenXml
from src.logic.state import AppState
from src.logic.validators import ValidationController
from src.models.pruefanweisung import Pruefanweisung
from util import getUniqueFilename
from ui.ui_main import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  
        self.ui.setupUi(self)

        with open("config.yaml", "r", encoding="utf-8") as config:
            self.config = yaml.safe_load(config)
        
        self.state = AppState(self.ui)
        self.navigator = NavigationController(self.ui, self.state)
        self.validator = ValidationController(self, self.ui, self.state)
        self.view_handler = ViewHandler(self, self.navigator, self.ui, self.state)

        self.assetsDir = "assets/images"

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
        self.ui.auswahlBildEinfuegen.clicked.connect(self.bildEinfuegenSeite7)

        # Prüfanweisung Eigenschaft
        self.ui.eigenschaftBildEinfuegen.setProperty("isPlaceholder", True)
        self.ui.eigenschaftBildEinfuegen.clicked.connect(self.bildEinfuegenSeite12)
        
        # Erfolgreich Abgeschlossen
        self.ui.zumHauptmenue.clicked.connect(self.zurueckZumHauptmenueGeklickt)


    # UI Steuerung
    # Navigationsleiste
    def feuerwehrLogoGeklickt(self):
        url = self.config["feuerwehrHompageURL"]
        webbrowser.open(url)

    def zurueckGeklickt(self):
        print("nicht implementiert")

    def weiterGeklickt(self):
        print("nicht implementiert")

    def hinzufuegenGeklickt(self):
        print("Hinzufügen geklickt")
        istSeiteValide, statusNachricht = self.validator.validiereHinzufuegenPruefanweisungEigenschaft()
        if istSeiteValide:
            self.state.speichereSeiteninhalte(Page.PRUEFANWEISUNG_EIGENSCHAFT)
            self.view_handler.resetAlleFelderAufSeite(Page.PRUEFANWEISUNG_EIGENSCHAFT)
        elif statusNachricht:
            self.statusBarMeldung(statusNachricht)

    def fertigGeklickt(self):
        print("Fertig geklickt")
        currentPage = self.state.get_current_page()
        istSeiteValide, statusNachricht = self.validator.istSeiteValide(currentPage)
        if istSeiteValide:
            self.state.speichereSeiteninhalte(currentPage)
            nextPage = self.navigator.get_next_page()
            self.view_handler.ladeSeiteninhalte(nextPage)
            self.navigator.goto(nextPage)
        elif statusNachricht:
            self.statusBarMeldung(statusNachricht)


    def loeschenGeklickt(self):
        print("Löschen geklickt")
        self.loeschenSeite12()
        
    def abbrechenGeklickt(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Bestätigung")
        msg_box.setWindowIcon(QIcon(":/icons/assets/icons/Stauferlöwe.png"))
        msg_box.setText("Bist du sicher, dass du abbrechen und ins Hauptmenü zurückkehren möchtest?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        antwort = msg_box.exec()

        if antwort == QMessageBox.Yes:
            print("Abgebrochen")
            self.view_handler.resetAlleFelder()
            self.navigator.goto(Page.HAUPTMENUE)


    # Seiten Funktionen 
    # Hauptmenü
    def startSichtpruefung(self):
        print("Sichtprüfung gestartet")
        if self.auswahlVorbereiten():
            self.ui.abbrechen.setEnabled(True)
            self.navigator.goto(Page.SICHTPRUEFUNG_AUSWAHL)

    def createPruefanweisung(self):
        print("createPruefanweisung")
        self.state.pruefanweisung = Pruefanweisung()
        self.ui.fertig.setEnabled(True)
        self.ui.abbrechen.setEnabled(True)
        self.navigator.goto(Page.PRUEFANWEISUNG_AUSWAHL)

    def editPruefanweisung(self):
        print("editPruefanweisung")
        # TODO

    def deletePruefanweisung(self):
        print("deletePruefanweisung")
        # TODO

    # Sichtprüfung Auswahl
    def auswahlVorbereiten(self):
        if not os.path.exists("data/pruefanweisungen.xml"):
            self.statusBar().showMessage("Keine vorhandenen Prüfanweisungen gefunden, die zur Auswahl stehen.", 3000)
            return False
        self.view_handler.ladeSeiteninhalte(Page.SICHTPRUEFUNG_AUSWAHL)
        return True

    # Prüfanweisung Auswahl    
    def bildEinfuegenSeite7(self):
        filePath = self.bildInProjektEinfuegen()
        if filePath:
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

    # Prüfanweisung Schadensbilder
    #TODO

    # Prüfanweisung Eigenschaft
        
    def loeschenSeite12(self):
        self.resetAlleFelderAufSeite(11)
        self.state.aktuelleEigenschaftIndex -= 1
    
    def bildEinfuegenSeite12(self):
        bildPfad = self.bildInProjektEinfuegen()
        if bildPfad:
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
        self.view_handler.resetAlleFelder()
        self.navigator.goto(Page.HAUPTMENUE)

    # Allgemeine UI Funktionen
    def bildInProjektEinfuegen(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Bild auswählen", "", "Bilder (*.png *.jpg *.jpeg)")
        if filePath:
            os.makedirs(self.assetsDir, exist_ok=True)  # Falls assets-Ordner nicht existiert, erstellen

            # Neuen Pfad im assets-Ordner erstellen (selber Dateiname wie Original)
            fileName = os.path.basename(filePath)
            fileName = getUniqueFilename(self.assetsDir, fileName)
            newPath = os.path.join(self.assetsDir, fileName)

            # Datei kopieren
            shutil.copy(filePath, newPath)

            return newPath
        
    def statusBarMeldung(self, nachricht):
        self.statusBar().showMessage(nachricht, 3000)

# TODO: evtl. ungenutzte Bilder löschen