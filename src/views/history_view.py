"""
History View
View for displaying feeding history and statistics
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QComboBox,
                             QHeaderView, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
import config.settings as settings


class HistoryView(QWidget):
    """
    View for displaying feed history and statistics
    """
    
    def __init__(self, controller):
        """
        Initialize history view
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
        
        # Header with filters
        filter_group = self._create_filter_section()
        layout.addWidget(filter_group)
        
        # Statistics section
        stats_group = self._create_statistics_section()
        layout.addWidget(stats_group)
        
        # History table
        table_label = QLabel("Fütterungsverlauf")
        table_label.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM, QFont.Bold))
        layout.addWidget(table_label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(
            ["Datum/Zeit", "Pferd", "Futterart", "Menge", "Notizen"]
        )
        self.history_table.setFont(QFont("Arial", settings.FONT_SIZE_SMALL))
        
        # Adjust column widths
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.history_table)
        
        # Load initial data
        self.refresh()
    
    def _create_filter_section(self) -> QGroupBox:
        """Create filter section"""
        group = QGroupBox("Filter")
        group.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        
        layout = QHBoxLayout()
        
        # Horse filter
        horse_label = QLabel("Pferd:")
        horse_label.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        
        self.horse_filter = QComboBox()
        self.horse_filter.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        self.horse_filter.setMinimumHeight(35)
        self.horse_filter.addItem("Alle Pferde", None)
        self.horse_filter.currentIndexChanged.connect(self.on_filter_changed)
        
        layout.addWidget(horse_label)
        layout.addWidget(self.horse_filter)
        
        # Time period filter
        period_label = QLabel("Zeitraum:")
        period_label.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        
        self.period_filter = QComboBox()
        self.period_filter.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        self.period_filter.setMinimumHeight(35)
        self.period_filter.addItems(["Heute", "Letzte 7 Tage", "Letzter Monat", "Alle"])
        self.period_filter.currentIndexChanged.connect(self.on_filter_changed)
        
        layout.addWidget(period_label)
        layout.addWidget(self.period_filter)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def _create_statistics_section(self) -> QGroupBox:
        """Create statistics display section"""
        group = QGroupBox("Statistiken")
        group.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        
        layout = QHBoxLayout()
        
        # Total feedings
        self.total_label = QLabel("Gesamt: 0")
        self.total_label.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        layout.addWidget(self.total_label)
        
        # Total weight
        self.weight_label = QLabel("Gesamtmenge: 0.00 kg")
        self.weight_label.setFont(QFont("Arial", settings.FONT_SIZE_MEDIUM))
        layout.addWidget(self.weight_label)
        
        layout.addStretch()
        
        group.setLayout(layout)
        return group
    
    def refresh(self):
        """Refresh the history view"""
        # Reload horse filter
        self.horse_filter.clear()
        self.horse_filter.addItem("Alle Pferde", None)
        horses = self.controller.get_all_horses()
        for horse in horses:
            self.horse_filter.addItem(f"{horse.name} (ID: {horse.horse_id})", horse.horse_id)
        
        # Reload history
        self.load_history()
    
    def on_filter_changed(self):
        """Handle filter change"""
        self.load_history()
    
    def load_history(self):
        """Load and display feed history based on filters"""
        # Get filter values
        horse_id = self.horse_filter.currentData()
        period = self.period_filter.currentText()
        
        # Calculate date range
        end_date = datetime.now()
        if period == "Heute":
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "Letzte 7 Tage":
            start_date = end_date - timedelta(days=7)
        elif period == "Letzter Monat":
            start_date = end_date - timedelta(days=30)
        else:  # Alle
            start_date = datetime(2000, 1, 1)
        
        # Get records
        records = self.controller.get_feed_records_by_date(start_date, end_date, horse_id)
        
        # Sort by timestamp (newest first)
        records.sort(key=lambda r: r.timestamp, reverse=True)
        
        # Update table
        self.history_table.setRowCount(len(records))
        
        total_weight = 0.0
        
        for row, record in enumerate(records):
            # Date/Time
            timestamp_str = record.timestamp.strftime("%d.%m.%Y %H:%M")
            self.history_table.setItem(row, 0, QTableWidgetItem(timestamp_str))
            
            # Horse name
            horse = self.controller.get_horse(record.horse_id)
            horse_name = horse.name if horse else f"ID: {record.horse_id}"
            self.history_table.setItem(row, 1, QTableWidgetItem(horse_name))
            
            # Feed type
            self.history_table.setItem(row, 2, QTableWidgetItem(record.feed_type))
            
            # Weight
            weight_str = f"{record.weight:.2f} kg"
            self.history_table.setItem(row, 3, QTableWidgetItem(weight_str))
            total_weight += record.weight
            
            # Notes
            notes = record.notes if record.notes else "-"
            self.history_table.setItem(row, 4, QTableWidgetItem(notes))
        
        # Update statistics
        self.total_label.setText(f"Gesamt: {len(records)}")
        self.weight_label.setText(f"Gesamtmenge: {total_weight:.2f} kg")
