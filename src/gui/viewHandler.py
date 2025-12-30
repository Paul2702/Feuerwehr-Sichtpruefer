import datetime
import logging
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QLineEdit, QTextEdit, QCheckBox, QRadioButton, QComboBox, QMessageBox, QFileDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QSizePolicy, QPlainTextEdit, QSpacerItem, QMainWindow
from PySide6.QtGui import QIcon, QCursor, QPixmap
from PySide6.QtCore import Qt, QObject, QSize, QCoreApplication

from src.gui.navigation import NavigationController
from src.gui.pages import Page
from src.logic.serializer import eigenschaftenNachKategorienGruppieren, eigenschaftspruefungenNachKategorienGruppieren, ladePruefanweisungXml, ladePruefanweisungenXml
from src.logic.state import AppState
from src.models.eigenschaft import Eigenschaft
from ui.ui_main import Ui_MainWindow

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

class ViewHandler(QObject):
    def __init__(self, mainWindow: QMainWindow, navigator: NavigationController, ui: Ui_MainWindow, state: AppState) -> None:
        self.navigator: NavigationController = navigator
        self.ui: Ui_MainWindow = ui
        self.state: AppState = state

        super().__init__(mainWindow)
        self.imageNotFoundPath: str = "assets/icons/Image not found"
        self.placeholderPath: str = "assets/icons/Add Image.png"
        self.placeholderIconSize: QSize = QSize(96, 96)

        self.zusammenfassungEigenschaftenIndex: int = 7
        self.zusammenfassungAnzahlZeilen: int = 11

        self.ladbareSeitenInhalte: dict[Page, callable] = {
            Page.SICHTPRUEFUNG_AUSWAHL: self.ladeSichtpruefungAuswahl,
            Page.SICHTPRUEFUNG_VORGABEN: self.ladeSichtpruefungVorgaben,
            Page.SICHTPRUEFUNG_PRUEFABLAUF: self.ladeSichtpruefungPruefablauf,
            Page.SICHTPRUEFUNG_EIGENSCHAFT: self.ladeSichtpruefungEigenschaft,
            Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG: self.ladeSichtpruefungZusammenfassung,
            Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG: self.ladePruefanweisungZusammenfassung
        }

    def ladeSeiteninhalte(self, page: Page) -> None:
        logger.debug(f"Lade Seiteninhalte für Seite: {page}")
        if page in self.ladbareSeitenInhalte:
            self.ladbareSeitenInhalte[page]()
            logger.debug(f"Seiteninhalte für {page} erfolgreich geladen")
        else:
            logger.debug(f"Keine Ladefunktion für Seite {page} definiert")

    def ladeSichtpruefungAuswahl(self) -> None:
        logger.info("Lade Sichtprüfung-Auswahl")
        auswahl = ladePruefanweisungenXml()
        logger.debug(f"Gefundene Prüfanweisungen: {len(auswahl)}")
        self.ladePruefanweisungenInAuswahl(auswahl)

    def ladePruefanweisungenInAuswahl(self, auswahl) -> None:
        # Erst alle alten Widgets aus dem Layout entfernen
        while self.ui.gridLayout.count():
            item = self.ui.gridLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        columns = 3  # Anzahl der Spalten
        for index, pruefanweisung in enumerate(auswahl):
            row = index // columns
            col = index % columns

            # Vertikales Layout für Name und Bild erstellen
            verticalLayout = QVBoxLayout()
            verticalLayout.setSpacing(0)
            verticalLayout.setObjectName(f"pruefobjektAuswahl{index}")

            # Anklickbares Bild erstellen
            verticalLayoutImage = QPushButton(self.ui.sichtpruefungAuswahlRaster)
            verticalLayoutImage.setObjectName(f"pruefobjektAuswahlImage{index}")
            verticalLayoutImage.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            verticalLayoutImage.setStyleSheet(u"height: 371;")
            icon = QIcon()
            icon.addFile(pruefanweisung["VorschauBildPfad"], QSize(), QIcon.Mode.Normal, QIcon.State.Off)
            verticalLayoutImage.setIcon(icon)
            verticalLayoutImage.setIconSize(QSize(371, 371))
            verticalLayoutImage.setProperty("xmlPfad", pruefanweisung["PruefanweisungXmlPfad"])
            verticalLayoutImage.clicked.connect(self.ladePruefanweisung)
            verticalLayout.addWidget(verticalLayoutImage)

            # Anklickbaren Namen erstellen
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            verticalLayoutName = QPushButton(self.ui.sichtpruefungAuswahlRaster)
            verticalLayoutName.setMaximumSize(QSize(371, 16777215))
            verticalLayoutName.setObjectName(f"pruefobjektAuswahlName{index}")
            verticalLayoutName.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            verticalLayoutName.setStyleSheet(u"QPushButton {\n"
                "	border: none;\n"
                "	color: rgb(208, 83, 82);\n"
                "	font: 600 16pt \"Segoe UI\";\n"
                "	padding-left:35;\n"
                "	padding-right:35;\n"
                "	padding-top:12;\n"
                "	padding-bottom:12;\n"
                "}\n"
                "QPushButton:hover {\n"
                "	color: rgb(255, 255, 255);\n"
                "}\n"
                "QPushButton:pressed {\n"
                "	color: rgb(208, 83, 82);\n"
                "}")

            woerterImNamen = pruefanweisung["Name"].split()
            name = ''
            zeilenLaenge = 0
            for wort in woerterImNamen:
                if zeilenLaenge + len(wort) > 30:
                    name += '\n'
                    zeilenLaenge = 0
                name += wort + ' '
                zeilenLaenge += len(wort) + 1
                
            verticalLayoutName.setText(QCoreApplication.translate("MainWindow", name.strip(), None))
            verticalLayoutName.setProperty("xmlPfad", pruefanweisung["PruefanweisungXmlPfad"])
            sizePolicy.setHeightForWidth(verticalLayoutName.sizePolicy().hasHeightForWidth())
            verticalLayoutName.clicked.connect(self.ladePruefanweisung)

            verticalLayout.addWidget(verticalLayoutName)

            verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            verticalLayout.addItem(verticalSpacer)
            
            self.ui.gridLayout.addLayout(verticalLayout, row, col, 1, 1)
            # Notlösung, wenn sich die Buttons vertikal überlappen...
            # Merke: Bei ScrollAreas ganz vorsichtig mit Größenangaben umgehen. Selbst eine minimum Size verhindert die Expandierung von Widgets...
            # self.ui.sichtpruefungAuswahlRaster.setMinimumHeight(self.ui.gridLayout.sizeHint().height())

    def ladePruefanweisung(self) -> None:
        button = self.sender()
        if button:
            xmlPfad = button.property("xmlPfad")
            if xmlPfad:
                logger.info(f"Lade Prüfanweisung aus: {xmlPfad}")
                try:
                    self.state.sichtpruefungManager.sichtpruefung = ladePruefanweisungXml(xmlPfad)
                    logger.debug("Prüfanweisung erfolgreich geladen, fülle UI-Felder")
                    if self.state.sichtpruefungManager.sichtpruefung is None:
                        raise ValueError("Sichtpruefung wurde nicht korrekt geladen")
                    self.ui.sichtpruefungInfosPruefart.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.pruefart)
                    self.ui.sichtpruefungInfosPruefvorgabe.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.pruefvorgabe)
                    self.ui.sichtpruefungInfosPruefvorgabeZusatz.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.pruefvorgabeZusatz)
                    self.ui.sichtpruefungInfosPrueffrist.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.prueffrist)
                    self.ui.sichtpruefungInfosSachkundiger.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.sachkundiger)
                    self.ui.sichtpruefungInfosZusatzausbildung.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.zusatzausbildung)
                    self.ui.sichtpruefungInfosHersteller.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.hersteller)
                    self.ui.sichtpruefungInfosAussonderungsfrist.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.aussonderungsfrist)
                    self.ui.fertig.setEnabled(True)
                    nextPage = self.navigator.get_next_page()
                    self.navigator.goto(nextPage)
                    logger.info(f"Prüfanweisung geladen: {self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.namePruefobjekt}")
                except Exception as e:
                    logger.error(f"Fehler beim Laden der Prüfanweisung: {e}", exc_info=True)

            else:
                logger.error("Fehler: Kein XML-Pfad gefunden!")
        else:
            logger.warning("LadePruefanweisung aufgerufen, aber kein Sender-Button gefunden")

    def ladeSichtpruefungVorgaben(self) -> None:
        if self.state.sichtpruefungManager.sichtpruefung is None:
            logger.error("Sichtpruefung wurde nicht initialisiert")
            return
        vorgabenText = self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.vorgabenText
        if vorgabenText:
            self.ui.vorgabenText.setText(vorgabenText)

    def ladeSichtpruefungPruefablauf(self) -> None:
        if self.state.sichtpruefungManager.sichtpruefung is None:
            logger.error("Sichtpruefung wurde nicht initialisiert")
            return
        pruefablaufText = self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.pruefablaufText
        if pruefablaufText:
            self.ui.pruefablaufText.setText(pruefablaufText)

    def ladeSichtpruefungEigenschaft(self) -> None:
        logger.debug(f"Lade Sichtprüfung-Eigenschaft (Index: {self.state.aktuelleEigenschaftIndex})")
        self.resetAlleFelderAufSeite(Page.SICHTPRUEFUNG_EIGENSCHAFT)
        if self.state.sichtpruefungManager.sichtpruefung is None:
            logger.error("Sichtpruefung wurde nicht initialisiert")
            return
        eigenschaft = self.state.sichtpruefungManager.sichtpruefung.eigenschaftspruefungen[self.state.aktuelleEigenschaftIndex].eigenschaft
        logger.debug(f"Eigenschaft geladen: {eigenschaft.kategorie} - {eigenschaft.beschreibung[:50]}...")
        self.eigenschaftBilderEinfuegen(eigenschaft)
        self.ui.eigenschaftKategorie.setText(eigenschaft.kategorie)
        self.ui.eigenschaftText.setText(eigenschaft.beschreibung)

    def ladeSichtpruefungZusammenfassung(self) -> None:
        if self.state.sichtpruefungManager.sichtpruefung is None:
            logger.error("Sichtpruefung wurde nicht initialisiert")
            return
        self.ui.zusammenfassungPruefobjektName.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.namePruefobjekt)
        self.eigenschaftenEinfuegenSeite6()
        self.ui.zusammenfassungHinweisText.setText(self.state.sichtpruefungManager.sichtpruefung.pruefanweisung.hinweis)
        self.ui.zusammenfassungSignaturDatumEingeben.setText(datetime.datetime.now().strftime("%d.%m.%Y"))

    def ladePruefanweisungZusammenfassung(self) -> None:
        if self.state.pruefanweisungManager.pruefanweisung is None:
            logger.error("Pruefanweisung wurde nicht initialisiert")
            return
        self.ui.zusammenfassungPruefobjektName_2.setText(self.state.pruefanweisungManager.pruefanweisung.namePruefobjekt)
        self.eigenschaftenEinfuegenSeite12()

    def eigenschaftBilderEinfuegen(self, eigenschaft: Eigenschaft) -> None:
        bilder = eigenschaft.bilder
        if bilder:
            # Platzhalter löschen
            item = self.ui.verticalLayout_14.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            for bildPfad, beschreibung in bilder:
                sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                eigenschaftBild = QLabel(self.ui.eigenschaftBilder)
                sizePolicy.setHeightForWidth(eigenschaftBild.sizePolicy().hasHeightForWidth())
                eigenschaftBild.setSizePolicy(sizePolicy)
                eigenschaftBild.setMinimumSize(QSize(540, 0))
                eigenschaftBild.setStyleSheet(u"height: 371;")
                pixmap = QPixmap(bildPfad)
                scaledPixmap = pixmap.scaled(540, pixmap.height() * (540 / pixmap.width()), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                eigenschaftBild.setPixmap(scaledPixmap)
                eigenschaftBild.setAlignment(Qt.AlignmentFlag.AlignCenter)
                eigenschaftBild.setText("")

                self.ui.verticalLayout_14.addWidget(eigenschaftBild)

                if beschreibung:
                    eigenschaftBildBeschreibung = QLabel(self.ui.eigenschaftBilder)
                    eigenschaftBildBeschreibung.setMaximumSize(QSize(540, 16777215))
                    eigenschaftBildBeschreibung.setStyleSheet(u"font: 16pt \"Segoe UI\";")
                    eigenschaftBildBeschreibung.setText(beschreibung)
                    eigenschaftBildBeschreibung.setWordWrap(True)

                    self.ui.verticalLayout_14.addWidget(eigenschaftBildBeschreibung)
            
            eigenschaftBildSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.ui.verticalLayout_14.addItem(eigenschaftBildSpacer)

    def eigenschaftenEinfuegenSeite6(self) -> None:
        if self.state.sichtpruefungManager.sichtpruefung is None:
            logger.error("Sichtpruefung wurde nicht initialisiert")
            return
        layoutRowIndex = self.zusammenfassungEigenschaftenIndex
        eigenschaftenLayout = self.ui.verticalLayout_10
        kategorien = eigenschaftspruefungenNachKategorienGruppieren(self.state.sichtpruefungManager.sichtpruefung.eigenschaftspruefungen)
        for kategorie, eigenschaftspruefungen in kategorien.items():
            # Falls eine neue Kategorie beginnt, erst die Kategoriezeile hinzufügen
            labelKategorie = QLabel(self.ui.scrollAreaWidgetContents)
            labelKategorie.setStyleSheet(  u"background-color: rgb(161, 192, 228);\n"
                                            "font: 700 14pt \"Segoe UI\";\n"
                                            "color: rgb(0, 0, 0);\n"
                                            "border: 1px solid rgb(81, 106, 196);")
            labelKategorie.setText(QCoreApplication.translate("MainWindow", kategorie, None))
            labelKategorie.setWordWrap(True)

            eigenschaftenLayout.insertWidget(layoutRowIndex, labelKategorie)
            layoutRowIndex += 1

            for eigenschaftspruefung in eigenschaftspruefungen:
                sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                sizePolicy5.setHorizontalStretch(0)
                sizePolicy5.setVerticalStretch(0)

                eigenschaftLayout = QHBoxLayout()
                eigenschaftLayout.setSpacing(0)
                labelEigenschaft = QLabel(self.ui.scrollAreaWidgetContents)
                sizePolicy5.setHeightForWidth(labelEigenschaft.sizePolicy().hasHeightForWidth())
                labelEigenschaft.setSizePolicy(sizePolicy5)
                labelEigenschaft.setStyleSheet(u"border: 1px solid rgb(81, 106, 196);\n"
                                                "background-color: rgb(255, 255, 255);\n"
                                                "color: rgb(0, 0, 0);")
                labelEigenschaft.setText(QCoreApplication.translate("MainWindow", eigenschaftspruefung.eigenschaft.beschreibung, None))
                labelEigenschaft.setWordWrap(True)

                eigenschaftLayout.addWidget(labelEigenschaft)

                checkboxHandlungsbedarf = QCheckBox(self.ui.scrollAreaWidgetContents)
                sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                sizePolicy6.setHorizontalStretch(0)
                sizePolicy6.setVerticalStretch(0)
                sizePolicy6.setHeightForWidth(checkboxHandlungsbedarf.sizePolicy().hasHeightForWidth())
                checkboxHandlungsbedarf.setSizePolicy(sizePolicy6)
                checkboxHandlungsbedarf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                checkboxHandlungsbedarf.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
                checkboxHandlungsbedarf.setStyleSheet( u"QCheckBox {\n"
                                                        "    border: 1px solid rgb(81, 106, 196);\n"
                                                        "	background-color: rgb(255, 255, 255);\n"
                                                        "	color: rgb(0, 0, 0);\n"
                                                        "	padding-left: 6px;\n"
                                                        "}\n"
                                                        "QCheckBox::indicator {\n"
                                                        "    width: 14px;\n"
                                                        "    height: 14px;\n"
                                                        "    border:2px solid black;\n"
                                                        "}\n"
                                                        "QCheckBox::indicator:unchecked {\n"
                                                        "}\n"
                                                        "QCheckBox::indicator:checked {\n"
                                                        "	image: url(\":/icons/assets/icons/Checkmark.png\");\n"
                                                        "}\n"
                                                        "QCheckBox::indicator:hover {\n"
                                                        "	background-color: rgb(230, 230, 230);\n"
                                                        "}")
                checkboxHandlungsbedarf.setCheckable(True)
                checkboxHandlungsbedarf.setChecked(eigenschaftspruefung.keinHandlungsbedarf)
                checkboxHandlungsbedarf.setText("")

                eigenschaftLayout.addWidget(checkboxHandlungsbedarf, 0, Qt.AlignmentFlag.AlignHCenter)

                inputMassnahmen = QLineEdit(self.ui.scrollAreaWidgetContents)
                sizePolicy5.setHeightForWidth(inputMassnahmen.sizePolicy().hasHeightForWidth())
                inputMassnahmen.setSizePolicy(sizePolicy5)
                inputMassnahmen.setStyleSheet( u"border: 1px solid rgb(81, 106, 196);\n"
                                                "background-color: rgb(255, 255, 255);\n"
                                                "color: rgb(0, 0, 0);")
                inputMassnahmen.setText(eigenschaftspruefung.massnahmen)

                eigenschaftLayout.addWidget(inputMassnahmen)
                eigenschaftLayout.setStretch(0, 1)
                eigenschaftLayout.setStretch(1, 0)
                eigenschaftLayout.setStretch(2, 1)

                eigenschaftenLayout.insertLayout(layoutRowIndex, eigenschaftLayout)
                layoutRowIndex += 1
        
    def eigenschaftenEinfuegenSeite12(self) -> None:
        if self.state.pruefanweisungManager.pruefanweisung is None:
            logger.error("Pruefanweisung wurde nicht initialisiert")
            return
        layoutRowIndex = self.zusammenfassungEigenschaftenIndex
        eigenschaftenLayout = self.ui.verticalLayout_17
        kategorien = eigenschaftenNachKategorienGruppieren(self.state.pruefanweisungManager.pruefanweisung.eigenschaften)
        for kategorie, eigenschaften in kategorien.items():
            # Falls eine neue Kategorie beginnt, erst die Kategoriezeile hinzufügen
            labelKategorie = QLabel(self.ui.scrollAreaWidgetContents_2)
            labelKategorie.setStyleSheet(  u"background-color: rgb(161, 192, 228);\n"
                                            "font: 700 14pt \"Segoe UI\";\n"
                                            "color: rgb(0, 0, 0);\n"
                                            "border: 1px solid rgb(81, 106, 196);")
            labelKategorie.setText(QCoreApplication.translate("MainWindow", kategorie, None))
            labelKategorie.setWordWrap(True)

            eigenschaftenLayout.insertWidget(layoutRowIndex, labelKategorie)
            layoutRowIndex += 1

            for eigenschaft in eigenschaften:
                sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                sizePolicy5.setHorizontalStretch(0)
                sizePolicy5.setVerticalStretch(0)

                eigenschaftLayout = QHBoxLayout()
                eigenschaftLayout.setSpacing(0)
                labelEigenschaft = QLabel(self.ui.scrollAreaWidgetContents_2)
                sizePolicy5.setHeightForWidth(labelEigenschaft.sizePolicy().hasHeightForWidth())
                labelEigenschaft.setSizePolicy(sizePolicy5)
                labelEigenschaft.setStyleSheet(u"border: 1px solid rgb(81, 106, 196);\n"
                                                "background-color: rgb(255, 255, 255);\n"
                                                "color: rgb(0, 0, 0);")
                labelEigenschaft.setText(QCoreApplication.translate("MainWindow", eigenschaft.beschreibung, None))
                labelEigenschaft.setWordWrap(True)

                eigenschaftLayout.addWidget(labelEigenschaft)

                checkboxHandlungsbedarf = QCheckBox(self.ui.scrollAreaWidgetContents_2)
                sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                sizePolicy6.setHorizontalStretch(0)
                sizePolicy6.setVerticalStretch(0)
                sizePolicy6.setHeightForWidth(checkboxHandlungsbedarf.sizePolicy().hasHeightForWidth())
                checkboxHandlungsbedarf.setSizePolicy(sizePolicy6)
                checkboxHandlungsbedarf.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                checkboxHandlungsbedarf.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
                checkboxHandlungsbedarf.setStyleSheet( u"QCheckBox {\n"
                                                        "    border: 1px solid rgb(81, 106, 196);\n"
                                                        "	background-color: rgb(255, 255, 255);\n"
                                                        "	color: rgb(0, 0, 0);\n"
                                                        "	padding-left: 6px;\n"
                                                        "}\n"
                                                        "QCheckBox::indicator {\n"
                                                        "    width: 14px;\n"
                                                        "    height: 14px;\n"
                                                        "    border:2px solid black;\n"
                                                        "}\n"
                                                        "QCheckBox::indicator:unchecked {\n"
                                                        "}\n"
                                                        "QCheckBox::indicator:checked {\n"
                                                        "	image: url(\":/icons/assets/icons/Checkmark.png\");\n"
                                                        "}\n"
                                                        "QCheckBox::indicator:hover {\n"
                                                        "	background-color: rgb(230, 230, 230);\n"
                                                        "}")
                checkboxHandlungsbedarf.setCheckable(False)
                checkboxHandlungsbedarf.setChecked(False)
                checkboxHandlungsbedarf.setText("")

                eigenschaftLayout.addWidget(checkboxHandlungsbedarf, 0, Qt.AlignmentFlag.AlignHCenter)

                inputMassnahmen = QLabel(self.ui.scrollAreaWidgetContents_2)
                sizePolicy5.setHeightForWidth(inputMassnahmen.sizePolicy().hasHeightForWidth())
                inputMassnahmen.setSizePolicy(sizePolicy5)
                inputMassnahmen.setStyleSheet( u"border: 1px solid rgb(81, 106, 196);\n"
                                                "background-color: rgb(255, 255, 255);\n"
                                                "color: rgb(0, 0, 0);")
                inputMassnahmen.setText('')

                eigenschaftLayout.addWidget(inputMassnahmen)
                eigenschaftLayout.setStretch(0, 1)
                eigenschaftLayout.setStretch(1, 0)
                eigenschaftLayout.setStretch(2, 1)

                eigenschaftenLayout.insertLayout(layoutRowIndex, eigenschaftLayout)
                layoutRowIndex += 1

    def resetAlleFelder(self) -> None:
        logger.info("Setze alle Felder zurück")
        for page in Page:
            self.resetAlleFelderAufSeite(page)
        
        self.ui.zurueck.setEnabled(False)
        self.ui.weiter.setEnabled(False)
        self.ui.hinzufuegen.setEnabled(False)
        self.ui.fertig.setEnabled(False)
        self.ui.loeschen.setEnabled(False)
        self.ui.abbrechen.setEnabled(False)
        logger.debug("Alle Buttons deaktiviert")

    def resetAlleFelderAufSeite(self, page: Page) -> None:
        widget_types = (QLineEdit, QTextEdit, QPlainTextEdit, QCheckBox, QRadioButton, QComboBox)
        all_widgets = []

        for widget_type in widget_types:
            all_widgets.extend(self.ui.content.widget(page.value).findChildren(widget_type))

        for widget in all_widgets:
            if isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit)):
                widget.clear()  # Textfelder leeren
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)  # Checkboxen deaktivieren
            elif isinstance(widget, QRadioButton):
                widget.setAutoExclusive(False) # Um die Logik zu umgehen, dass ein Radiobutton immer aktiviert sein muss
                widget.setChecked(False) # Radiobuttons deaktivieren
                widget.setAutoExclusive(True)
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)  # ComboBox auf Standard setzen

        if page == Page.SICHTPRUEFUNG_EIGENSCHAFT:
            while self.ui.verticalLayout_14.count():
                item = self.ui.verticalLayout_14.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            eigenschaftBild = QLabel(self.ui.eigenschaftBilder)
            sizePolicy.setHeightForWidth(eigenschaftBild.sizePolicy().hasHeightForWidth())
            eigenschaftBild.setSizePolicy(sizePolicy)
            eigenschaftBild.setMinimumSize(QSize(540, 0))
            eigenschaftBild.setStyleSheet(u"height: 371;")
            eigenschaftBild.setPixmap(QPixmap(self.imageNotFoundPath))
            eigenschaftBild.setAlignment(Qt.AlignmentFlag.AlignCenter)
            eigenschaftBild.setText("")
            self.ui.verticalLayout_14.addWidget(eigenschaftBild)

        if page == Page.SICHTPRUEFUNG_ZUSAMMENFASSUNG:
            self.resetEigenschaftenDerZusammenfassung(self.ui.verticalLayout_10)

        if page == Page.PRUEFANWEISUNG_AUSWAHL:
            self.ui.auswahlBildEinfuegen.setIcon(QIcon(self.placeholderPath))
            self.ui.auswahlBildEinfuegen.setIconSize(self.placeholderIconSize)
            self.ui.auswahlBildEinfuegen.setProperty("isPlaceholder", True)
            self.ui.auswahlBildEinfuegen.setProperty("imagePath", '')
            self.ui.auswahlBildEinfuegen.setStyleSheet(u"QPushButton {\n"
                "border:5px solid black;\n"
                "border-radius:20;\n"
                "width: 371;\n"
                "height: 371;\n"
                "}\n"
                "\n"
                "QPushButton:hover {\n"
                "	background-color: rgb(50, 50, 50);\n"
                "}")
            
        if page == Page.PRUEFANWEISUNG_EIGENSCHAFT:
            while self.ui.verticalLayout_11.count() > 2:
                item = self.ui.verticalLayout_11.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            if self.ui.verticalLayout_11.count() > 1:
                item = self.ui.verticalLayout_11.takeAt(1)
                if item.widget():
                    item.widget().deleteLater()
                    

        if page == Page.PRUEFANWEISUNG_ZUSAMMENFASSUNG:
            self.resetEigenschaftenDerZusammenfassung(self.ui.verticalLayout_17)
            
    def resetEigenschaftenDerZusammenfassung(self, layout: QVBoxLayout) -> None:
        anzahlZuLoeschendeZeilen = layout.count() - self.zusammenfassungAnzahlZeilen
        letzterIndex = self.zusammenfassungEigenschaftenIndex + anzahlZuLoeschendeZeilen - 1

        # Rückwärts durch das Layout iterieren, um Index-Verschiebungen zu vermeiden
        for i in reversed(range(self.zusammenfassungEigenschaftenIndex, letzterIndex)):
            item = layout.itemAt(i)

            if item.widget():  # Falls es ein Widget ist (QLabel, QCheckBox, QLineEdit etc.)
                item.widget().deleteLater()
            elif item.layout():  # Falls es ein verschachteltes Layout (z. B. QHBoxLayout) ist
                sub_layout = item.layout()
                while sub_layout.count():  # Alle enthaltenen Widgets löschen
                    sub_item = sub_layout.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                layout.removeItem(sub_layout)  # Das leere Layout entfernen

            layout.removeItem(item)  # Schließlich das Haupt-Item aus dem Layout entfernen