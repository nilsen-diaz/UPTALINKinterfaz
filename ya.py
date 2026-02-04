import sys
import math
# import numpy as np  <-- Eliminado (solo se usaba para 3D)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea, QSplitter,
    QToolBar, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QAction, QIcon, QPalette, QColor, QFont
# import pyvista as pv <-- Eliminado
# from pyvistaqt import QtInteractor <-- Eliminado

# =============================================================================
# 1. BACKEND: Lógica de Negocio y Matemáticas
# =============================================================================

class LinkBudgetCalculator:
    """
    Clase encargada exclusivamente de los cálculos matemáticos.
    No contiene nada de UI.
    """
    
    @staticmethod
    def calculate(freq, dist, p_tx, g_a, g_b, cable_loss, sens, cost_eq, hours):
        """
        Ejecuta las fórmulas basadas en el JS original.
        
        Args:
            freq: Frecuencia (GHz)
            dist: Distancia (Km)
            p_tx: Potencia Tx (dBm)
            g_a: Ganancia Antena A (dBi)
            g_b: Ganancia Antena B (dBi)
            cable_loss: Pérdidas Cables (dB)
            sens: Sensibilidad Rx (dBm)
            cost_eq: Costo Equipo ($)
            hours: Horas Instalación
            
        Returns:
            dict: Diccionario con todos los resultados calculados y estado.
        """
        
        # Validación básica
        if freq == 0 or dist == 0:
            raise ValueError("La Frecuencia y la Distancia deben ser mayores a 0.")

        # 1. FSPL (Free Space Path Loss)
        # Formula: 20*log10(d) + 20*log10(f) + 32.44
        fspl = 20 * math.log10(dist) + 20 * math.log10(freq) + 32.44
        
        # 2. Pérdida Total del Sistema
        total_loss = fspl + cable_loss
        
        # 3. Nivel Rx Recibido (RSSI)
        rssi = p_tx + g_a + g_b - total_loss
        
        # 4. Margen de Desvanecimiento (Fade Margin)
        margin = rssi - sens
        
        # 5. Determinación de viabilidad
        is_good = margin > 10
        
        # Cálculos secundarios (simulados según el JS original)
        availability = "99.999" if is_good else "98.5"
        snr = rssi + 100  # Aproximación simple del JS
        throughput = (freq * 10) if is_good else 0
        
        # Radio de Fresnel (Aproximación JS: 5.5 * sqrt(dist/freq))
        fresnel_radius = 5.5 * math.sqrt(dist / freq)
        
        # Costos
        total_cost = cost_eq + (hours * 50) # $50/hora ingeniero
        
        # Estado
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
# 2. FRONTEND: Interfaz Gráfica (PySide6)
# =============================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UPTALINK - Diseño de Radioenlaces")
        self.resize(1280, 800)
        
        # Configuración de la paleta de colores (Fallback por si falla QSS en algunos OS)
        self.apply_dark_theme_palette()
        
        # Setup Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QGridLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Definir áreas: Header, Sidebar, Main(Central Vacío), Right Panel
        self.setup_header()
        self.setup_sidebar()
        self.setup_central_area() # Renombrado de setup_3d_view
        self.setup_right_panel()
        
        # Estilos QSS (CSS para Qt)
        self.load_styles()

    def apply_dark_theme_palette(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#0f0f0f"))
        palette.setColor(QPalette.WindowText, QColor("#f1f1f1"))
        palette.setColor(QPalette.Base, QColor("#121212"))
        palette.setColor(QPalette.AlternateBase, QColor("#1e1e1e"))
        palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
        palette.setColor(QPalette.ToolTipText, QColor("#ffffff"))
        palette.setColor(QPalette.Text, QColor("#f1f1f1"))
        palette.setColor(QPalette.Button, QColor("#1e1e1e"))
        palette.setColor(QPalette.ButtonText, QColor("#f1f1f1"))
        palette.setColor(QPalette.BrightText, QColor("#ff0000"))
        palette.setColor(QPalette.Link, QColor("#3ea6ff"))
        palette.setColor(QPalette.Highlight, QColor("#3ea6ff"))
        palette.setColor(QPalette.HighlightedText, QColor("#000000"))
        QApplication.setPalette(palette)

    def setup_header(self):
        # Barra de herramientas simulando el header web
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(56)
        self.header_widget.setObjectName("header")
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(16, 0, 16, 0)

        # Logo
        logo_label = QLabel("UPTALINK")
        logo_label.setObjectName("logoLabel")
        logo_label.setStyleSheet("font-weight: bold; font-size: 1.2rem; color: #f1f1f1;")
        
        # Search Bar simulation
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar ID de enlace o coordenadas...")
        search_input.setObjectName("searchInput")
        
        # Botones header
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # Iconos simulados con texto unicode para no depender de archivos externos
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
        self.header_layout.addWidget(search_input, 1) # Stretch factor para que crezca
        self.header_layout.addStretch()
        self.header_layout.addLayout(btn_layout)

        self.main_layout.addWidget(self.header_widget, 0, 0, 1, 3)

    def setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(5, 10, 5, 10)
        
        # Items del Sidebar
        items = [
            ("Inicio", "🏠"),
            ("Suscripciones", "📈"),
            ("--", ""),
            ("DATASHEETS", ""),
            ("Antenas Históricas", "📡"),
            ("Registradas", "💾"),
            ("Guardadas", "🔖"),
            ("--", ""),
            ("SERVICIOS", ""),
            ("UPTALINK Premium", "👑"),
            ("UPTALINK Lite", "🌐"),
            ("--", ""),
            ("SOPORTE", ""),
            ("Configuración", "⚙️"),
            ("Ayuda", "❓"),
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

    def setup_central_area(self):
        # Contenedor central reemplazando el visor 3D
        self.main_content = QWidget()
        self.main_content.setObjectName("mainContent")
        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(0,0,0,0)
        
        # Label de reemplazo indicando que la visualización está inhabilitada
        placeholder_label = QLabel("Visualización 3D Inhabilitada")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("color: #333333; font-size: 24px; font-weight: bold;")
        
        main_layout.addWidget(placeholder_label)
        self.main_layout.addWidget(self.main_content, 1, 1, 1, 1)

    # def init_3d_scene(self): ... <-- ELIMINADO (Lógica de terreno y antenas)

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

        # --- Módulo 1: Inputs ---
        self.create_module("Parámetros de Entrada (INPUTS)", "inputs")
        
        # --- Módulo 2: Outputs ---
        self.create_module("Resultados de Cálculo (OUTPUTS)", "outputs")
        
        # --- Botones de Acción ---
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

        # Botón Reset
        self.btn_reset = QPushButton("🗑️ Limpiar / Reiniciar")
        self.btn_reset.setObjectName("btnReset")
        self.btn_reset.clicked.connect(self.reset_all)
        self.panel_layout.addWidget(self.btn_reset)
        
        self.panel_layout.addStretch() # Empujar todo hacia arriba
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
    # 3. LÓGICA DE CONTROL (Slots)
    # =============================================================================

    def get_input_value(self, index):
        try:
            val = self.input_widgets[index].text()
            return float(val) if val else 0.0
        except ValueError:
            return 0.0

    def perform_calculation(self):
        try:
            # Recolectar datos
            # Indices basados en la lista de labels JS: 0:Frec, 1:Dist, 2:Tx, 3:Ga, 4:Gb, 5:Loss, 6:Sens, 14:Cost, 15:Hours
            freq = self.get_input_value(0)
            dist = self.get_input_value(1)
            p_tx = self.get_input_value(2)
            g_a = self.get_input_value(3)
            g_b = self.get_input_value(4)
            cable_loss = self.get_input_value(5)
            sens = self.get_input_value(6)
            cost_eq = self.get_input_value(14)
            hours = self.get_input_value(15)
            
            # Calcular usando Backend
            results = LinkBudgetCalculator.calculate(freq, dist, p_tx, g_a, g_b, cable_loss, sens, cost_eq, hours)
            
            # Actualizar Outputs UI
            # Mapping resultados a los widgets de output
            # 0: FSPL, 1: TotalLoss, 2: RSSI, 3: Margin, 4: Avail, 5: SNR, 6: Throughput, 7: Fresnel
            # 12: Costo, 13: Status, 15: Presupuesto
            
            self.output_widgets[0].setText(f"{results['fspl']:.2f}")
            self.output_widgets[1].setText(f"{results['total_loss']:.2f}")
            self.output_widgets[2].setText(f"{results['rssi']:.2f}")
            self.output_widgets[3].setText(f"{results['margin']:.2f}")
            self.output_widgets[4].setText(results['availability'])
            self.output_widgets[5].setText(f"{results['snr']:.1f}")
            self.output_widgets[6].setText(f"{results['throughput']:.0f}")
            self.output_widgets[7].setText(f"{results['fresnel']:.2f}")
            
            # Costos (Output 11 y 15 en el código original JS, ajustando aquí al orden visual)
            # El JS usa indices 12 y 15 para costos en output
            self.output_widgets[11].setText(f"${results['total_cost']:.2f}") # Costo Total Instalación
            self.output_widgets[15].setText(f"${results['total_cost']:.2f}") # Presupuesto Final
            
            # Estado
            status_widget = self.output_widgets[13]
            status_widget.setText(results['status'])
            
            # Feedback visual de color
            color = "#00d09c" if results['is_good'] else "#ff4d4d"
            status_widget.setStyleSheet(f"color: {color}; font-weight: bold; background: #0a0a0a; border: 1px solid #222; padding: 4px; border-radius: 4px;")
            
            # Actualizar Visor 3D (ELIMINADO)
            # self.update_3d_link(results['is_good'])
            
            self.show_toast("Cálculo Exitoso: Enlace Viable" if results['is_good'] else "Alerta: Enlace Débil")
            
        except ValueError as e:
            QMessageBox.warning(self, "Error de Entrada", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado: {e}")

    # def update_3d_link(self, is_good): ... <-- ELIMINADO

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
                w.setStyleSheet("") # Reset estilo personalizado
            
            # Actualizar Visor 3D (ELIMINADO)
            # self.update_3d_link(False)
            
            self.show_toast("Sistema reiniciado.")

    def show_toast(self, message):
        # Implementación simple de Toast usando una Label flotante o status bar
        # Por simplicidad en PySide6 sin widgets externos, usamos el Status Bar temporalmente
        self.statusBar().showMessage(message, 3000)
        # O podríamos crear un QWidget personalizado que se anime, pero StatusBar es nativo y limpio.

    def load_styles(self):
        """Carga el QSS replicando el CSS proporcionado"""
        qss = """
        /* --- GENERAL --- */
        QWidget {
            background-color: #0f0f0f;
            color: #f1f1f1;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            font-size: 14px;
        }
        
        /* --- HEADER --- */
        #header {
            background-color: #0f0f0f;
            border-bottom: 1px solid #303030;
        }
        
        #logoLabel {
            color: #f1f1f1;
        }
        
        #searchInput {
            background-color: #121212;
            border: 1px solid #303030;
            border-right: none;
            padding: 6px 16px;
            color: #f1f1f1;
            border-radius: 40px 0 0 40px;
        }
        
        #headerIconBtn, #userAvatar {
            background-color: #181818;
            border: none;
            border-radius: 50%;
            color: #f1f1f1;
        }
        
        #userAvatar {
            background-color: #3ea6ff;
            color: #000;
            font-weight: bold;
        }
        
        #headerIconBtn:hover {
            background-color: #272727;
        }

        /* --- SIDEBAR --- */
        #sidebar {
            background-color: #0f0f0f;
            border-right: 1px solid #1e1e1e; /* Sutil borde */
        }
        
        #sidebarSectionTitle {
            color: #aaaaaa;
            font-size: 0.8rem;
            font-weight: bold;
            padding-left: 10px;
            margin-top: 10px;
        }
        
        #sidebarBtn {
            background: none;
            border: none;
            color: #f1f1f1;
            text-align: left;
            padding: 8px 12px;
            border-radius: 10px;
            font-size: 0.9rem;
        }
        
        #sidebarBtn:hover {
            background-color: #272727;
        }

        /* --- RIGHT PANEL --- */
        #rightPanel {
            background-color: #0f0f0f;
            border-left: 1px solid #303030;
        }
        
        #moduleBox {
            background-color: #1e1e1e;
            border-radius: 8px;
            border: 1px solid #303030;
        }
        
        #moduleTitle {
            color: #3ea6ff;
            font-weight: bold;
            font-size: 0.9rem;
            text-transform: uppercase;
            border-bottom: 1px solid #303030;
            padding-bottom: 8px;
            margin-bottom: 10px;
        }
        
        QLabel {
            color: #aaaaaa;
            font-size: 0.75rem;
            margin-bottom: 2px;
        }

        #inputField {
            background-color: #121212;
            border: 1px solid #333;
            color: #f1f1f1;
            padding: 6px 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
        
        #inputField:focus {
            border: 1px solid #3ea6ff;
        }
        
        #outputField {
            background-color: #0a0a0a;
            color: #00d09c;
            border: 1px solid #222;
            padding: 6px 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }

        /* --- BOTONES --- */
        QPushButton {
            border-radius: 6px;
            font-weight: bold;
            padding: 10px;
        }
        
        #btnCalc {
            background-color: #3ea6ff;
            color: #000;
        }
        #btnCalc:hover {
            background-color: #66b6ff;
        }
        
        #btnSave {
            background-color: #272727;
            color: #fff;
            border: 1px solid #444;
        }
        #btnSave:hover {
            background-color: #3a3a3a;
        }
        
        #btnReset {
            background: transparent;
            border: 1px solid #ff4d4d;
            color: #ff4d4d;
            padding: 12px;
        }
        #btnReset:hover {
            background-color: #ff4d4d;
            color: white;
        }
        
        /* Scrollbar */
        QScrollBar:vertical {
            background: #0f0f0f;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #333;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """
        self.setStyleSheet(qss)

# =============================================================================
# 4. MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Habilitar High DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())