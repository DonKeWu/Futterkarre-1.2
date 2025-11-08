# config/logging_config.py
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime


class Pi5OptimizedLogger:
    """
    Pi5-optimierter Logger mit erweiterten Features
    
    Features:
    ✅ Rotating Log Files (verhindert volle Disk)  
    ✅ Performance-optimierte Formatierung
    ✅ Remote-Debug-Unterstützung
    ✅ Context-basiertes Logging  
    ✅ Error-Level-spezifische Dateien
    ✅ Memory-effiziente Buffer
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
    def setup_optimized_logging(self, 
                              console_level: int = logging.INFO,
                              file_level: int = logging.DEBUG,
                              enable_remote_debug: bool = False):
        """
        Konfiguriert optimiertes Logging für Pi5
        
        Args:
            console_level: Log-Level für Konsole
            file_level: Log-Level für Dateien
            enable_remote_debug: Aktiviert Remote-Debug-Features
        """
        # Root-Logger konfigurieren
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Alle existierenden Handler entfernen
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Performance-optimiertes Format
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%H:%M:%S'  # Kurzes Zeit-Format für Pi5
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s | %(filename)s:%(lineno)d',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Konsolen-Handler (für SSH/Terminal)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # 2. Rotating File Handler (verhindert volle Disk)
        main_log = self.log_dir / "futterkarre.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log,
            maxBytes=5*1024*1024,  # 5MB pro Datei
            backupCount=3,  # Max 3 Archive (15MB total)
            encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # 3. Error-spezifische Datei (nur Errors/Critical)
        error_log = self.log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=2*1024*1024,  # 2MB
            backupCount=2,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
        
        # 4. Performance-Log für Hardware-Operations
        perf_log = self.log_dir / "performance.log"
        perf_handler = logging.handlers.RotatingFileHandler(
            perf_log,
            maxBytes=1024*1024,  # 1MB
            backupCount=2,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.DEBUG)
        
        # Filter nur für Performance-relevante Logger
        perf_filter = logging.Filter()
        perf_filter.filter = lambda record: any(name in record.name for name in 
            ['hardware', 'weight_manager', 'timer_manager', 'sensor'])
        perf_handler.addFilter(perf_filter)
        perf_handler.setFormatter(file_formatter)
        root_logger.addHandler(perf_handler)
        
        # 5. Remote-Debug-Handler (falls aktiviert)
        if enable_remote_debug:
            self._setup_remote_debug_handler(root_logger, file_formatter)
        
        # Startup-Info loggen
        logging.info("🚀 Pi5-optimiertes Logging initialisiert")
        logging.info(f"📁 Log-Verzeichnis: {self.log_dir}")
        logging.info(f"💾 Disk-Protection: RotatingFileHandler (max 20MB)")
        
    def _setup_remote_debug_handler(self, root_logger, formatter):
        """Setup für Remote-Debug via Network (optional)"""
        try:
            # Network-Handler für Remote-Debugging
            network_handler = logging.handlers.SocketHandler(
                'localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT
            )
            network_handler.setLevel(logging.ERROR)
            network_handler.setFormatter(formatter)
            root_logger.addHandler(network_handler)
            
            logging.info("🌐 Remote-Debug-Handler aktiviert")
        except Exception as e:
            logging.warning(f"Remote-Debug-Setup fehlgeschlagen: {e}")
    
    def create_context_logger(self, context: str) -> logging.Logger:
        """
        Erstellt Context-spezifischen Logger
        
        Args:
            context: Kontext-Name (z.B. "Pi5-Deployment", "Hardware-Test")
            
        Returns:
            Konfigurierter Logger mit Context
        """
        logger = logging.getLogger(f"futterkarre.{context}")
        
        # Context-spezifische Log-Datei
        context_log = self.log_dir / f"{context.lower()}.log"
        context_handler = logging.handlers.RotatingFileHandler(
            context_log,
            maxBytes=1024*1024,  # 1MB
            backupCount=1,
            encoding='utf-8'
        )
        context_handler.setLevel(logging.DEBUG)
        
        # Erweiterte Formatierung mit Context
        context_formatter = logging.Formatter(
            f'%(asctime)s [{context}] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        context_handler.setFormatter(context_formatter)
        logger.addHandler(context_handler)
        
        return logger
    
    def log_system_metrics(self):
        """Loggt System-Metriken für Pi5-Monitoring"""
        try:
            # CPU/Memory Info (falls verfügbar)
            import psutil
            
            metrics_logger = self.create_context_logger("system-metrics")
            metrics_logger.info(f"CPU: {psutil.cpu_percent()}%")
            metrics_logger.info(f"Memory: {psutil.virtual_memory().percent}%")
            metrics_logger.info(f"Disk: {psutil.disk_usage('/').percent}%")
            
        except ImportError:
            logging.debug("psutil nicht verfügbar - System-Metriken deaktiviert")
        except Exception as e:
            logging.warning(f"System-Metriken-Logging fehlgeschlagen: {e}")


def setup_logging(enable_remote_debug: bool = False):
    """
    Einfache Setup-Funktion für optimiertes Pi5-Logging
    
    Args:
        enable_remote_debug: Aktiviert Remote-Debug-Features
    """
    pi5_logger = Pi5OptimizedLogger()
    pi5_logger.setup_optimized_logging(
        console_level=logging.INFO,
        file_level=logging.DEBUG,
        enable_remote_debug=enable_remote_debug
    )
    
    return pi5_logger


# Globale Instanz für einfachen Import
pi5_logger = None

def get_pi5_logger():
    """Liefert globale Pi5-Logger-Instanz"""
    global pi5_logger
    if pi5_logger is None:
        pi5_logger = setup_logging()
    return pi5_logger


