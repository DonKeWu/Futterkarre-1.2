"""
Weighing View
Main view for weighing feed portions
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QTextEdit, QGroupBox,
                             QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import config.settings as settings


class WeighingView(QWidget):
    """
    View for weighing feed and recording measurements
    """
    
    def __init__(self, controller):
        """
        Initialize weighing view
        Args:
            controller: AppController instance
        """
        super().__init__()
        self.controller = controller
        self.current_weight = 0.0
        self.init_ui()
        
        # Timer for continuous weight updates
        self.weight_timer = QTimer()
        self.weight_timer.timeout.connect(self.update_weight_display)
        self.weight_timer.start(500)  # Update every 500ms
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Weight display section
        weight_group = self._create_weight_display()
        layout.addWidget(weight_group)
        
        # Selection section
        selection_group = self._create_selection_section()
        layout.addWidget(selection_group)
        
        # Control buttons
        control_layout = self._create_control_buttons()
        layout.addLayout(control_layout)
        
        # Notes section
        notes_group = self._create_notes_section()
        layout.addWidget(notes_group)
        
        layout.addStretch()
    
    def _create_weight_display(self) -> QGroupBox:
        """Create the weight display section"""
        group = QGroupBox("Aktuelle Messung")
        group.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM, QFont.Bold))
        
        layout = QVBoxLayout()
        
        # Large weight display
        self.weight_label = QLabel("0.00 kg")
        self.weight_label.setAlignment(Qt.AlignCenter)
        self.weight_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.weight_label.setStyleSheet(f"color: {settings.COLOR_PRIMARY}; padding: 20px;")
        layout.addWidget(self.weight_label)
        
        # Tare button
        tare_btn = QPushButton("⚖️ Tarieren")
        tare_btn.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        tare_btn.setMinimumHeight(50)
        tare_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.COLOR_SECONDARY};
                color: white;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:pressed {{
                background-color: {settings.COLOR_PRIMARY};
            }}
        """)
        tare_btn.clicked.connect(self.on_tare_clicked)
        layout.addWidget(tare_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_selection_section(self) -> QGroupBox:
        """Create selection section for horse and feed type"""
        group = QGroupBox("Auswahl")
        group.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM, QFont.Bold))
        
        layout = QVBoxLayout()
        
        # Horse selection
        horse_layout = QHBoxLayout()
        horse_label = QLabel("Pferd:")
        horse_label.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        horse_label.setMinimumWidth(100)
        
        self.horse_combo = QComboBox()
        self.horse_combo.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        self.horse_combo.setMinimumHeight(40)
        
        horse_layout.addWidget(horse_label)
        horse_layout.addWidget(self.horse_combo)
        layout.addLayout(horse_layout)
        
        # Feed type selection
        feed_layout = QHBoxLayout()
        feed_label = QLabel("Futterart:")
        feed_label.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        feed_label.setMinimumWidth(100)
        
        self.feed_combo = QComboBox()
        self.feed_combo.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        self.feed_combo.setMinimumHeight(40)
        self.feed_combo.addItems(settings.FEED_TYPES)
        
        feed_layout.addWidget(feed_label)
        feed_layout.addWidget(self.feed_combo)
        layout.addLayout(feed_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_control_buttons(self) -> QHBoxLayout:
        """Create control buttons"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Record button
        self.record_btn = QPushButton("✓ Speichern")
        self.record_btn.setFont(QFont("Arial", settings.FONT_SIZE_LARGE, QFont.Bold))
        self.record_btn.setMinimumHeight(60)
        self.record_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.COLOR_SUCCESS};
                color: white;
                border-radius: 5px;
            }}
            QPushButton:pressed {{
                background-color: {settings.COLOR_PRIMARY};
            }}
        """)
        self.record_btn.clicked.connect(self.on_record_clicked)
        
        layout.addWidget(self.record_btn)
        
        return layout
    
    def _create_notes_section(self) -> QGroupBox:
        """Create notes section"""
        group = QGroupBox("Notizen (optional)")
        group.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        
        layout = QVBoxLayout()
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Optionale Notizen zur Fütterung...")
        
        layout.addWidget(self.notes_edit)
        group.setLayout(layout)
        
        return group
    
    def update_weight_display(self):
        """Update the weight display with current reading"""
        weight = self.controller.get_current_weight()
        if weight is not None:
            self.current_weight = weight
            self.weight_label.setText(f"{weight:.2f} kg")
    
    def refresh(self):
        """Refresh the view (reload horse list)"""
        self.horse_combo.clear()
        horses = self.controller.get_all_horses()
        for horse in horses:
            self.horse_combo.addItem(f"{horse.name} (ID: {horse.horse_id})", horse.horse_id)
    
    def on_tare_clicked(self):
        """Handle tare button click"""
        if self.controller.tare_scale():
            QMessageBox.information(self, "Tarieren", "Waage wurde tariert")
        else:
            QMessageBox.warning(self, "Fehler", "Tarieren fehlgeschlagen")
    
    def on_record_clicked(self):
        """Handle record button click"""
        # Validate selections
        if self.horse_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie ein Pferd aus")
            return
        
        # Get selected values
        horse_id = self.horse_combo.currentData()
        feed_type = self.feed_combo.currentText()
        weight = self.current_weight
        notes = self.notes_edit.toPlainText().strip() or None
        
        # Validate weight
        if weight < settings.MIN_WEIGHT:
            QMessageBox.warning(self, "Fehler", 
                              f"Gewicht zu gering (min. {settings.MIN_WEIGHT}kg)")
            return
        
        # Record feeding
        if self.controller.record_feeding(horse_id, feed_type, weight, notes):
            QMessageBox.information(self, "Erfolg", 
                                   f"Fütterung gespeichert:\n{weight:.2f}kg {feed_type}")
            # Clear notes
            self.notes_edit.clear()
        else:
            QMessageBox.critical(self, "Fehler", "Speichern fehlgeschlagen")
