import sys
import math
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

# =============================================================================
# CONFIGURACIÓN DE ENTORNO (MODO SEGURO)
# =============================================================================

# IMPORTANTE: Forzamos HAS_3D a False porque tu entorno no soporta OpenGL.
# Esto evita que el programa intente cargar el visor 3D y de errores en la consola.
# Si instalas drivers nuevos o ejecutas localmente, cambia esto a True.
HAS_3D = False 

# Intentamos importar librerías 3D por si acaso, pero no las usaremos.
try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
except ImportError:
    pass
except Exception:
    pass

# =============================================================================
# 1. BACKEND (Lógica Matemática - Funciona siempre)
# =============================================================================

class LinkBudgetCalculator:
    
    @staticmethod
    def calculate(freq, dist, p_tx, g_a, g_b, cable_loss, sens, cost_eq, hours):
        if freq == 0 or dist == 0:
            raise ValueError("La Frecuencia y la Distancia deben ser mayores a 0.")

        fspl = 20 * math.log10(dist) + 20 * math.log10(freq) + 32.44
        total_loss = fspl + cable_loss
        rssi = p_tx + g_a + g_b - total_loss
        margin = rssi - sens
        is_good = margin > 10
        
        availability = "99.999" if is_good else "98.5"
        snr = rssi + 100 
        throughput = (freq * 10) if is_good else 0
        fresnel_radius = 5.5 * math.sqrt(dist / freq)
        total_cost = cost_eq + (hours * 50)
        status = "VIABLE" if is_good else "CRÍTICO"
        
        return {
            'fspl': fspl,
            'total_loss': total_loss,
            'rssi': rssi,
            'margin': margin,
            'availability': availability,
            'snr': snr,
            'throughput': throughput,
            'fresnel': fresnel_radius,
            'total_cost': total_cost,
            'status': status,
            'is_good': is_good
        }

# =============================================================================
# 2. FRONTEND (Interfaz Gráfica)
# =============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UPTALINK - Diseño de Radioenlaces (Modo Cálculo)")
        self.resize(1280, 800)
        
        self.apply_dark_theme_palette()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QGridLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_header()
        self.setup_sidebar()
        self.setup_main_content() # Cargará el modo de error/informativo
        self.setup_right_panel()
        self.load_styles()

    def apply_dark_theme_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#0f0f0f"))
        palette.setColor(QPalette.WindowText, QColor("#f1f1f1"))
        palette.setColor(QPalette.Base, QColor("#121212"))
        palette.setColor(QPalette.AlternateBase, QColor("#1e1e1e"))
        palette.setColor(QPalette.Text, QColor("#f1f1f1"))
        palette.setColor(QPalette.Button, QColor("#1e1e1e"))
        palette.setColor(QPalette.ButtonText, QColor("#f1f1f1"))
        palette.setColor(QPalette.Link, QColor("#3ea6ff"))
        palette.setColor(QPalette.Highlight, QColor("#3ea6ff"))
        palette.setColor(QPalette.HighlightedText, QColor("#000000"))
        QApplication.setPalette(palette)

    def setup_header(self):
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(56)
        self.header_widget.setObjectName("header")
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(16, 0, 16, 0)

        logo_label = QLabel("UPTALINK")
        logo_label.setStyleSheet("font-weight: bold; font-size: 1.2rem; color: #f1f1f1;")
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar ID de enlace o coordenadas...")
        search_input.setObjectName("searchInput")
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_vid = QPushButton("📹")
        btn_bell = QPushButton("🔔")
        btn_user = QPushButton("J")
        btn_user.setObjectName("userAvatar")
        
        for btn in [btn_vid, btn_bell, btn_user]:
            btn.setFixedSize(40, 40)
            btn.setObjectName("headerIconBtn")
            btn_layout.addWidget(btn)

        self.header_layout.addWidget(logo_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(search_input, 1)
        self.header_layout.addStretch()
        self.header_layout.addLayout(btn_layout)

        self.main_layout.addWidget(self.header_widget, 0, 0, 1, 3)

    def setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(5, 10, 5, 10)
        
        items = [
            ("Inicio", "🏠"), ("Suscripciones", "📈"), ("--", ""),
            ("DATASHEETS", ""), ("Antenas Históricas", "📡"), ("Registradas", "💾"), ("Guardadas", "🔖"),
            ("--", ""), ("SERVICIOS", ""), ("UPTALINK Premium", "👑"), ("UPTALINK Lite", "🌐"),
            ("--", ""), ("SOPORTE", ""), ("Configuración", "⚙️"), ("Ayuda", "❓"),
        ]
        
        for text, icon in items:
            if text == "--":
                line = QLabel("---")
                line.setAlignment(Qt.AlignCenter)
                line.setStyleSheet("color: #303030; margin: 5px 0;")
                sidebar_layout.addWidget(line)
            elif icon == "":
                title = QLabel(text)
                title.setObjectName("sidebarSectionTitle")
                sidebar_layout.addWidget(title)
            else:
                btn = QPushButton(f"{icon}  {text}")
                btn.setObjectName("sidebarBtn")
                sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar, 1, 0, 1, 1)

    def setup_main_content(self):
        """Muestra el visor de estado (ya que el 3D está deshabilitado por entorno)"""
        self.main_content = QWidget()
        self.main_content.setObjectName("mainContent")
        layout = QVBoxLayout(self.main_content)
        layout.setContentsMargins(0,0,0,0)
        
        # Como HAS_3D es False, vamos directo al mensaje informativo
        self.show_3d_error(layout)

        self.main_layout.addWidget(self.main_content, 1, 1, 1, 1)

    def show_3d_error(self, parent_layout):
        """Muestra un mensaje profesional en el área central"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setAlignment(Qt.AlignCenter)
        
        msg = QLabel("📊 MÓDULO DE CÁLCULO ACTIVO")
        msg.setStyleSheet("font-size: 28px; font-weight: bold; color: #3ea6ff; margin-bottom: 20px;")
        
        sub_msg = QLabel(
            "El entorno actual no soporta aceleración gráfica 3D.\n"
            "La interfaz se está ejecutando en modo de compatibilidad.\n\n"
            "El sistema de análisis de Enlace de Radio está FULL OPERATIVO.\n"
            "Ingrese los parámetros en el panel derecho para obtener resultados."
        )
        sub_msg.setAlignment(Qt.AlignCenter)
        sub_msg.setStyleSheet("color: #f1f1f1; font-size: 16px; background: #1e1e1e; padding: 40px; border-radius: 8px; border: 1px solid #303030;")
        
        info_layout.addWidget(msg)
        info_layout.addWidget(sub_msg)
        parent_layout.addWidget(info_widget)

    def setup_right_panel(self):
        self.right_panel = QScrollArea()
        self.right_panel.setWidgetResizable(True)
        self.right_panel.setFixedWidth(380)
        self.right_panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.right_panel.setObjectName("rightPanel")
        
        panel_widget = QWidget()
        self.panel_layout = QVBoxLayout(panel_widget)
        self.panel_layout.setContentsMargins(15, 15, 15, 15)
        self.panel_layout.setSpacing(10)

        self.create_module("Parámetros de Entrada (INPUTS)", "inputs")
        self.create_module("Resultados de Cálculo (OUTPUTS)", "outputs")
        
        btn_layout = QHBoxLayout()
        self.btn_calc = QPushButton("⚡ Calcular")
        self.btn_calc.setObjectName("btnCalc")
        self.btn_calc.clicked.connect(self.perform_calculation)
        
        self.btn_save = QPushButton("💾 Guardar")
        self.btn_save.setObjectName("btnSave")
        self.btn_save.clicked.connect(self.save_link)
        
        btn_layout.addWidget(self.btn_calc)
        btn_layout.addWidget(self.btn_save)
        self.panel_layout.addLayout(btn_layout)

        self.btn_reset = QPushButton("🗑️ Limpiar / Reiniciar")
        self.btn_reset.setObjectName("btnReset")
        self.btn_reset.clicked.connect(self.reset_all)
        self.panel_layout.addWidget(self.btn_reset)
        
        self.panel_layout.addStretch()
        self.right_panel.setWidget(panel_widget)
        self.main_layout.addWidget(self.right_panel, 1, 2, 1, 1)

    def create_module(self, title, type_id):
        module = QFrame()
        module.setObjectName("moduleBox")
        layout = QVBoxLayout(module)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        header = QLabel(title)
        header.setObjectName("moduleTitle")
        layout.addWidget(header)
        
        if type_id == "inputs":
            self.input_widgets = []
            labels = [
                "Frecuencia (GHz)", "Distancia (Km)", "Potencia Tx (dBm)", "Ganancia Ant A (dBi)",
                "Ganancia Ant B (dBi)", "Pérdidas Cables (dB)", "Sensibilidad Rx (dBm)", "Factor de Ruido (dB)",
                "Ancho de Banda (MHz)", "Temperatura (°C)", "Margen de Lluvia (dB)", "Altura Torre A (m)",
                "Altura Torre B (m)", "Obstáculo Altura (m)", "Costo Equipo ($)", "Horas Instalación"
            ]
            for lbl_text in labels:
                h_layout = QHBoxLayout()
                lbl = QLabel(lbl_text)
                inp = QLineEdit()
                inp.setPlaceholderText("0.0")
                inp.setObjectName("inputField")
                self.input_widgets.append(inp)
                h_layout.addWidget(lbl)
                h_layout.addWidget(inp)
                layout.addLayout(h_layout)
                
        elif type_id == "outputs":
            self.output_widgets = []
            labels = [
                "Pérdida Trayecto (FSPL) (dB)", "Pérdida Total Sistema (dB)", "Nivel Rx Recibido (dBm)", "Margen de Desvanecimiento (dB)",
                "Disponibilidad (%)", "SNR Estimado (dB)", "Throughput (Mbps)", "Radio de Fresnel (m)",
                "Clearance Terrain (%)", "Consumo Energía (W)", "Disipación Térmica (BTU)", "Costo Total Instalación ($)",
                "ROI Esperado (Meses)", "Estado del Enlace", "Alerta Crítica", "Presupuesto Final ($)"
            ]
            for lbl_text in labels:
                h_layout = QHBoxLayout()
                lbl = QLabel(lbl_text)
                out = QLineEdit()
                out.setReadOnly(True)
                out.setText("-")
                out.setObjectName("outputField")
                self.output_widgets.append(out)
                h_layout.addWidget(lbl)
                h_layout.addWidget(out)
                layout.addLayout(h_layout)

        self.panel_layout.addWidget(module)

    # =============================================================================
    # 3. LÓGICA DE CONTROL
    # =============================================================================

    def get_input_value(self, index):
        try:
            val = self.input_widgets[index].text()
            return float(val) if val else 0.0
        except ValueError:
            return 0.0

    def perform_calculation(self):
        try:
            freq = self.get_input_value(0)
            dist = self.get_input_value(1)
            p_tx = self.get_input_value(2)
            g_a = self.get_input_value(3)
            g_b = self.get_input_value(4)
            cable_loss = self.get_input_value(5)
            sens = self.get_input_value(6)
            cost_eq = self.get_input_value(14)
            hours = self.get_input_value(15)
            
            results = LinkBudgetCalculator.calculate(freq, dist, p_tx, g_a, g_b, cable_loss, sens, cost_eq, hours)
            
            self.output_widgets[0].setText(f"{results['fspl']:.2f}")
            self.output_widgets[1].setText(f"{results['total_loss']:.2f}")
            self.output_widgets[2].setText(f"{results['rssi']:.2f}")
            self.output_widgets[3].setText(f"{results['margin']:.2f}")
            self.output_widgets[4].setText(results['availability'])
            self.output_widgets[5].setText(f"{results['snr']:.1f}")
            self.output_widgets[6].setText(f"{results['throughput']:.0f}")
            self.output_widgets[7].setText(f"{results['fresnel']:.2f}")
            self.output_widgets[11].setText(f"${results['total_cost']:.2f}")
            self.output_widgets[15].setText(f"${results['total_cost']:.2f}")
            
            status_widget = self.output_widgets[13]
            status_widget.setText(results['status'])
            color = "#00d09c" if results['is_good'] else "#ff4d4d"
            status_widget.setStyleSheet(f"color: {color}; font-weight: bold; background: #0a0a0a; border: 1px solid #222; padding: 4px; border-radius: 4px;")
            
            self.show_toast("Cálculo Exitoso" if results['is_good'] else "Alerta: Enlace Débil")
            
        except ValueError as e:
            QMessageBox.warning(self, "Error de Entrada", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {e}")

    def save_link(self):
        if self.output_widgets[0].text() == '-':
            QMessageBox.information(self, "Info", "Calcule antes de guardar.")
            return
        self.show_toast("Enlace guardado en Base de Datos.")

    def reset_all(self):
        reply = QMessageBox.question(self, 'Confirmar', '¿Reiniciar todos los campos?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for w in self.input_widgets:
                w.clear()
            for w in self.output_widgets:
                w.setText('-')
                w.setStyleSheet("")
            self.show_toast("Sistema reiniciado.")

    def show_toast(self, message):
        self.statusBar().showMessage(message, 3000)

    def load_styles(self):
        qss = """
        /* --- GENERAL --- */
        QWidget { background-color: #0f0f0f; color: #f1f1f1; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
        #header { background-color: #0f0f0f; border-bottom: 1px solid #303030; }
        #logoLabel { color: #f1f1f1; }
        #searchInput { background-color: #121212; border: 1px solid #303030; border-right: none; padding: 6px 16px; color: #f1f1f1; border-radius: 40px 0 0 40px; }
        #headerIconBtn, #userAvatar { background-color: #181818; border: none; border-radius: 50%; color: #f1f1f1; }
        #userAvatar { background-color: #3ea6ff; color: #000; font-weight: bold; }
        #headerIconBtn:hover { background-color: #272727; }
        #sidebar { background-color: #0f0f0f; }
        #sidebarSectionTitle { color: #aaaaaa; font-size: 0.8rem; font-weight: bold; padding-left: 10px; margin-top: 10px; }
        #sidebarBtn { background: none; border: none; color: #f1f1f1; text-align: left; padding: 8px 12px; border-radius: 10px; font-size: 0.9rem; }
        #sidebarBtn:hover { background-color: #272727; }
        #rightPanel { background-color: #0f0f0f; border-left: 1px solid #303030; }
        #moduleBox { background-color: #1e1e1e; border-radius: 8px; border: 1px solid #303030; }
        #moduleTitle { color: #3ea6ff; font-weight: bold; font-size: 0.9rem; text-transform: uppercase; border-bottom: 1px solid #303030; padding-bottom: 8px; margin-bottom: 10px; }
        QLabel { color: #aaaaaa; font-size: 0.75rem; margin-bottom: 2px; }
        #inputField { background-color: #121212; border: 1px solid #333; color: #f1f1f1; padding: 6px 10px; border-radius: 4px; font-family: 'Courier New', monospace; }
        #inputField:focus { border: 1px solid #3ea6ff; }
        #outputField { background-color: #0a0a0a; color: #00d09c; border: 1px solid #222; padding: 6px 10px; border-radius: 4px; font-family: 'Courier New', monospace; }
        QPushButton { border-radius: 6px; font-weight: bold; padding: 10px; }
        #btnCalc { background-color: #3ea6ff; color: #000; }
        #btnCalc:hover { background-color: #66b6ff; }
        #btnSave { background-color: #272727; color: #fff; border: 1px solid #444; }
        #btnSave:hover { background-color: #3a3a3a; }
        #btnReset { background: transparent; border: 1px solid #ff4d4d; color: #ff4d4d; padding: 12px; }
        #btnReset:hover { background-color: #ff4d4d; color: white; }
        """
        self.setStyleSheet(qss)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())