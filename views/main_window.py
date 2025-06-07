# views/main_window.py

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QStackedWidget
from PyQt5.QtCore import QTimer
from views.start import StartSeite
from views.fuettern_seite import FuetternSeite
from utils.futter_loader import lade_heu_als_dataclasses, lade_heulage_als_dataclasses, lade_pferde_als_dataclasses
from utils.futter_loader import lade_heu_als_dataclasses
heuliste = lade_heu_als_dataclasses("heu_eigen_2025.csv")
if heuliste:
    heu = heuliste[0]  # Erstes Heu-Objekt
    print(heu.name, heu.trockenmasse)
class MainWindow(QMainWindow):
    def __init__(self, sensor, heu_namen=None):
        super().__init__()
        self.sensor = sensor
        self.status = "start"
        self.heu_namen = heu_namen if heu_namen is not None else []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Futterkarre 2.0")
        self.setFixedSize(1024, 600)

        self.stacked_widget = QStackedWidget()

        # Seiten anlegen
        self.start_screen = StartSeite()
        self.load_screen = self.create_load_screen()
        self.fuettern_seite = FuetternSeite()
        self.summary_screen = self.create_summary_screen()

        self.stacked_widget.addWidget(self.start_screen)      # Index 0
        self.stacked_widget.addWidget(self.load_screen)       # Index 1
        self.stacked_widget.addWidget(self.fuettern_seite)    # Index 2
        self.stacked_widget.addWidget(self.summary_screen)    # Index 3

        self.setCentralWidget(self.stacked_widget)
        self.show_status("start")

        # Navigation: Start -> Beladen
        self.start_screen.btn_start.clicked.connect(lambda: self.show_status("beladen"))
        # Navigation: Beladen abgeschlossen -> Füttern
        self.load_screen.findChild(QPushButton, "btn_beladung_abgeschlossen").clicked.connect(
            lambda: self.show_status("fuettern")
        )
        # Navigation: Füttern -> Abschluss (oder zurück)
        self.fuettern_seite.btn_naechstes_pferd.clicked.connect(lambda: self.show_status("abschluss"))
        self.fuettern_seite.btn_nachladen.clicked.connect(lambda: self.show_status("beladen"))

    def show_status(self, status):
        self.status = status
        if status == "start":
            self.stacked_widget.setCurrentWidget(self.start_screen)
        elif status == "beladen":
            self.stacked_widget.setCurrentWidget(self.load_screen)
        elif status == "fuettern":
            self.stacked_widget.setCurrentWidget(self.fuettern_seite)
        elif status == "abschluss":
            self.stacked_widget.setCurrentWidget(self.summary_screen)

    def create_load_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.weight_label = QLabel("Gewicht: -- kg")
        self.combo_heu = QComboBox()
        self.combo_heu.addItems(self.heu_namen)
        self.combo_heu.currentIndexChanged.connect(self.on_heu_changed)
        self.refresh_button = QPushButton("Aktualisieren")
        self.refresh_button.clicked.connect(self.update_weight)
        btn_beladung_abgeschlossen = QPushButton("Beladung abgeschlossen")
        btn_beladung_abgeschlossen.setObjectName("btn_beladung_abgeschlossen")
        layout.addWidget(QLabel("Bitte Futter wählen und Wagen beladen."))
        layout.addWidget(self.weight_label)
        layout.addWidget(self.combo_heu)
        layout.addWidget(self.refresh_button)
        layout.addWidget(btn_beladung_abgeschlossen)
        widget.setLayout(layout)
        # Gewicht automatisch aktualisieren
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_weight)
        self.timer.start(1000)
        return widget

    def create_summary_screen(self):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Fütterung abgeschlossen!\nHier kommt die Checkliste.")
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def update_weight(self):
        try:
            weight = self.sensor.read_weight()
            self.weight_label.setText(f"Gewicht: {weight:.2f} kg")
        except Exception as e:
            self.weight_label.setText("Fehler beim Wiegen!")

    def on_heu_changed(self, index):
        heu_name = self.combo_heu.currentText()
        try:
            heuliste = lade_heu_als_dataclasses(heu_name)
            if heuliste:
                heu = heuliste[0]
            print(f"Geladenes Heu: {heu}")
        except Exception as e:
            print(f"Fehler beim Laden von {heu_name}: {e}")







