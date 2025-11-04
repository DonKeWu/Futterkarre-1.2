"""
Horse Management View
View for managing horses in the system
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QLineEdit, QFormLayout, QMessageBox,
                             QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import config.settings as settings


class HorseManagementView(QWidget):
    """
    View for managing horses (add, edit, delete)
    """
    
    def __init__(self, controller):
        """
        Initialize horse management view
        Args:
            controller: AppController instance
        """
        super().__init__()
        self.controller = controller
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Pferdeverwaltung")
        title.setFont(QFont("Arial", settings.FONT_SIZE_LARGE, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Add button
        add_btn = QPushButton("+ Neues Pferd")
        add_btn.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        add_btn.setMinimumHeight(40)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.COLOR_SUCCESS};
                color: white;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:pressed {{
                background-color: {settings.COLOR_PRIMARY};
            }}
        """)
        add_btn.clicked.connect(self.on_add_horse)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Horse table
        self.horse_table = QTableWidget()
        self.horse_table.setColumnCount(6)
        self.horse_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Rasse", "Alter", "Gewicht", "Aktionen"]
        )
        self.horse_table.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        
        # Adjust column widths
        header = self.horse_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # Make table read-only except for action buttons
        self.horse_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.horse_table)
        
        # Load horses
        self.refresh()
    
    def refresh(self):
        """Refresh the horse list"""
        horses = self.controller.get_all_horses()
        self.horse_table.setRowCount(len(horses))
        
        for row, horse in enumerate(horses):
            # ID
            self.horse_table.setItem(row, 0, QTableWidgetItem(str(horse.horse_id)))
            
            # Name
            self.horse_table.setItem(row, 1, QTableWidgetItem(horse.name))
            
            # Breed
            breed = horse.breed if horse.breed else "-"
            self.horse_table.setItem(row, 2, QTableWidgetItem(breed))
            
            # Age
            age = str(horse.age) if horse.age else "-"
            self.horse_table.setItem(row, 3, QTableWidgetItem(age))
            
            # Weight
            weight = f"{horse.weight:.1f}kg" if horse.weight else "-"
            self.horse_table.setItem(row, 4, QTableWidgetItem(weight))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(40)
            edit_btn.clicked.connect(lambda checked, h=horse: self.on_edit_horse(h))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(40)
            delete_btn.clicked.connect(lambda checked, h=horse: self.on_delete_horse(h))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.horse_table.setCellWidget(row, 5, actions_widget)
    
    def on_add_horse(self):
        """Handle add horse button click"""
        dialog = HorseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if self.controller.add_horse(**data):
                QMessageBox.information(self, "Erfolg", "Pferd hinzugefügt")
                self.refresh()
            else:
                QMessageBox.critical(self, "Fehler", "Pferd konnte nicht hinzugefügt werden")
    
    def on_edit_horse(self, horse):
        """Handle edit horse button click"""
        dialog = HorseDialog(self, horse)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if self.controller.update_horse(horse.horse_id, **data):
                QMessageBox.information(self, "Erfolg", "Pferd aktualisiert")
                self.refresh()
            else:
                QMessageBox.critical(self, "Fehler", "Pferd konnte nicht aktualisiert werden")
    
    def on_delete_horse(self, horse):
        """Handle delete horse button click"""
        reply = QMessageBox.question(
            self, "Löschen bestätigen",
            f"Möchten Sie {horse.name} wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.controller.delete_horse(horse.horse_id):
                QMessageBox.information(self, "Erfolg", "Pferd gelöscht")
                self.refresh()
            else:
                QMessageBox.critical(self, "Fehler", "Pferd konnte nicht gelöscht werden")


class HorseDialog(QDialog):
    """Dialog for adding/editing a horse"""
    
    def __init__(self, parent, horse=None):
        """
        Initialize horse dialog
        Args:
            parent: Parent widget
            horse: Horse object for editing (None for adding new)
        """
        super().__init__(parent)
        self.horse = horse
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        self.setWindowTitle("Pferd hinzufügen" if self.horse is None else "Pferd bearbeiten")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # Name field (required)
        self.name_edit = QLineEdit()
        self.name_edit.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        if self.horse:
            self.name_edit.setText(self.horse.name)
        layout.addRow("Name*:", self.name_edit)
        
        # Breed field
        self.breed_edit = QLineEdit()
        self.breed_edit.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        if self.horse and self.horse.breed:
            self.breed_edit.setText(self.horse.breed)
        layout.addRow("Rasse:", self.breed_edit)
        
        # Age field
        self.age_edit = QLineEdit()
        self.age_edit.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        if self.horse and self.horse.age:
            self.age_edit.setText(str(self.horse.age))
        layout.addRow("Alter:", self.age_edit)
        
        # Weight field
        self.weight_edit = QLineEdit()
        self.weight_edit.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        if self.horse and self.horse.weight:
            self.weight_edit.setText(str(self.horse.weight))
        layout.addRow("Gewicht (kg):", self.weight_edit)
        
        # Notes field
        self.notes_edit = QLineEdit()
        self.notes_edit.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        if self.horse and self.horse.notes:
            self.notes_edit.setText(self.horse.notes)
        layout.addRow("Notizen:", self.notes_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Speichern")
        save_btn.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
    
    def get_data(self):
        """Get form data as dictionary"""
        data = {
            'name': self.name_edit.text().strip(),
            'breed': self.breed_edit.text().strip() or None,
            'notes': self.notes_edit.text().strip() or None
        }
        
        # Parse age
        try:
            age_text = self.age_edit.text().strip()
            data['age'] = int(age_text) if age_text else None
        except ValueError:
            data['age'] = None
        
        # Parse weight
        try:
            weight_text = self.weight_edit.text().strip()
            data['weight'] = float(weight_text) if weight_text else None
        except ValueError:
            data['weight'] = None
        
        return data
