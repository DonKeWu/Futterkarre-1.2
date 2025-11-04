"""
Main Window
Primary GUI window for Futterkarre-2 application
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from .horse_management_view import HorseManagementView
from .weighing_view import WeighingView
from .history_view import HistoryView
import config.settings as settings


class MainWindow(QMainWindow):
    """
    Main application window with navigation and view management
    Optimized for 1024x600 touchscreen display
    """
    
    def __init__(self, controller):
        """
        Initialize main window
        Args:
            controller: AppController instance
        """
        super().__init__()
        self.controller = controller
        self.init_ui()
        
        # Connect controller signals
        self.controller.weight_updated.connect(self.on_weight_updated)
        self.controller.scale_ready.connect(self.on_scale_ready)
        self.controller.error_occurred.connect(self.on_error)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        
        # Set window size for 7" touchscreen
        self.resize(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        
        if settings.FULLSCREEN:
            self.showFullScreen()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Add navigation bar
        nav_bar = self._create_navigation()
        main_layout.addWidget(nav_bar)
        
        # Add stacked widget for views
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create and add views
        self.weighing_view = WeighingView(self.controller)
        self.horse_view = HorseManagementView(self.controller)
        self.history_view = HistoryView(self.controller)
        
        self.stacked_widget.addWidget(self.weighing_view)
        self.stacked_widget.addWidget(self.horse_view)
        self.stacked_widget.addWidget(self.history_view)
        
        # Show weighing view by default
        self.stacked_widget.setCurrentWidget(self.weighing_view)
        
        # Status bar
        self.statusBar().showMessage("Bereit")
    
    def _create_header(self) -> QWidget:
        """Create application header"""
        header = QFrame()
        header.setStyleSheet(f"background-color: {settings.COLOR_PRIMARY}; color: white;")
        header.setFixedHeight(60)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Title
        title = QLabel(f"🚜 {settings.APP_NAME}")
        title.setFont(QFont("Arial", settings.FONT_SIZE_LARGE, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("●")
        self.status_label.setFont(QFont("Arial", 20))
        self.status_label.setStyleSheet("color: yellow;")
        layout.addWidget(self.status_label)
        
        return header
    
    def _create_navigation(self) -> QWidget:
        """Create navigation bar with view selection buttons"""
        nav_bar = QFrame()
        nav_bar.setStyleSheet(f"background-color: {settings.COLOR_SECONDARY};")
        nav_bar.setFixedHeight(70)
        
        layout = QHBoxLayout(nav_bar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Navigation buttons
        btn_weighing = self._create_nav_button("⚖️ Wiegen", 0)
        btn_horses = self._create_nav_button("🐴 Pferde", 1)
        btn_history = self._create_nav_button("📊 Historie", 2)
        
        layout.addWidget(btn_weighing)
        layout.addWidget(btn_horses)
        layout.addWidget(btn_history)
        
        return nav_bar
    
    def _create_nav_button(self, text: str, view_index: int) -> QPushButton:
        """
        Create a navigation button
        Args:
            text: Button text
            view_index: Index of view to show when clicked
        """
        button = QPushButton(text)
        button.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM, QFont.Bold))
        button.setMinimumHeight(50)
        button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #1976D2;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:pressed {
                background-color: #E3F2FD;
            }
        """)
        button.clicked.connect(lambda: self.switch_view(view_index))
        return button
    
    def switch_view(self, index: int):
        """
        Switch to a different view
        Args:
            index: Index of view in stacked widget
        """
        self.stacked_widget.setCurrentIndex(index)
        
        # Refresh view when switching
        current_widget = self.stacked_widget.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()
    
    def on_weight_updated(self, weight: float):
        """Handle weight update signal from controller"""
        # Could update a global weight display if needed
        pass
    
    def on_scale_ready(self, ready: bool):
        """Handle scale ready status change"""
        if ready:
            self.status_label.setStyleSheet("color: #4CAF50;")  # Green
            self.statusBar().showMessage("Waage bereit")
        else:
            self.status_label.setStyleSheet("color: #F44336;")  # Red
            self.statusBar().showMessage("Waage nicht bereit")
    
    def on_error(self, error_message: str):
        """Handle error signal from controller"""
        self.statusBar().showMessage(f"Fehler: {error_message}", 5000)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.controller.cleanup()
        event.accept()
