import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PySide6.QtWidgets import QApplication
from src.gui.mainWindow import MainWindow # Hauptfenster importieren

if __name__ == "__main__":
    app = QApplication(sys.argv)  
    window = MainWindow()  # Hauptfenster erstellen
    window.show()  # Fenster anzeigen
    sys.exit(app.exec())  # Qt-Event-Loop starten