#!/usr/bin/env python3
"""
Futterkarre-2 Main Application
Intelligente Futterwaage für Pferde - PyQt5 + Raspberry Pi 5
"""
import sys
from PyQt5.QtWidgets import QApplication
from src.controllers import AppController
from src.views import MainWindow
import config.settings as settings


def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(settings.APP_NAME)
    app.setApplicationVersion(settings.APP_VERSION)
    
    # Set application-wide font
    from PyQt5.QtGui import QFont
    app.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
    
    # Create controller
    controller = AppController()
    
    # Create and show main window
    window = MainWindow(controller)
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
