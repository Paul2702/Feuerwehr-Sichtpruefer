import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Logging-Konfiguration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

from PySide6.QtWidgets import QApplication
from src.gui.mainWindow import MainWindow # Hauptfenster importieren

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Feuerwehr-Sichtpruefer wird gestartet")
    logger.info("=" * 60)
    
    try:
        app = QApplication(sys.argv)
        logger.debug(f"QApplication erstellt mit Argumenten: {sys.argv}")
        
        window = MainWindow()  # Hauptfenster erstellen
        logger.info("Hauptfenster erstellt")
        
        window.show()  # Fenster anzeigen
        logger.info("Hauptfenster angezeigt")
        
        logger.info("Event-Loop wird gestartet")
        exit_code = app.exec()
        logger.info(f"Anwendung wird beendet mit Exit-Code: {exit_code}")
        sys.exit(exit_code)  # Qt-Event-Loop starten
    except Exception as e:
        logger.critical(f"Kritischer Fehler beim Starten der Anwendung: {e}", exc_info=True)
        sys.exit(1)