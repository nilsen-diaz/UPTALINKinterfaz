# Versión PySide6 + PyVista
import sys
import math
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QScrollArea, 
    QFrame, QSizePolicy, QSpacerItem, QToolButton, QMessageBox,
    QSplitter
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QIcon, QColor, QFont, QPalette
import pyvista as pv
from pyvistaqt import QtInteractor

# --- 1. DEFINICIÓN DE ESTILOS (QSS - Qt Style Sheets) ---
# Aquí traducimos el CSS de HTML a la sintaxis de Qt Stylesheet
STYLESHEET = """
QMainWindow, QWidget {
    background-color: #0f0f0f;
    color: #ffffff;
    font-family: 'Roboto', sans-serif;
    font-size: 14px;
}

/* --- Scrollbars --- */
QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical { background: #0f0f0f; width: 10px; margin: 0px; }
QScrollBar::handle:vertical { background: #303030; min-height: 20px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

/* --- Header --- */
#header {
    background-color: #0f0f0f;
    border-bottom: 1px solid #303030;
    padding: 0 16px;
}
#logo_label { font-weight: 700; font-size: 18px; color: white; }
#logo_span { color: #ff0000; font-size: 24px; }

/* --- Search Bar --- */
#search_input {
    background-color: #121212;
    border: 1px solid #303030;
    border-right: none;
    color: white;
    padding: 8px 16px;
    border-top-left-radius: 20px;
    border-bottom-left-radius: 20px;
}
#search_input:focus { border-color: #1c62b9; }
#search_btn {
    background-color: #212121;
    border: 1px solid #303030;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
    padding: 0 20px;
}
#search_btn:hover { background-color: #272727; }
#mic_btn {
    background-color: #121212;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
}
#mic_btn:hover { background-color: #272727; }

/* --- Sidebar --- */
#sidebar { background-color: #0f0f0f; }
QPushButton#nav_btn {
    background-color: transparent;
    border: none;
    text-align: left;
    padding: 10px 24px;
    border-radius: 10px;
    color: white;
}
QPushButton#nav_btn:hover { background-color: #272727; }
QPushButton#nav_btn:checked { background-color: #272727; font-weight: bold; }
QLabel#section_title { padding: 8px 24px; font-weight: bold; font-size: 15px; }

/* --- Main Content --- */
#player_container {
    background-color: black;
    border-radius: 12px;
    min-height: 300px;
}
#info_panel QLabel { color: white; }
#subscribe_btn {
    background-color: white;
    color: black;
    border: none;
    border-radius: 18px;
    padding: 8px 16px;
    font-weight: bold;
}
#subscribe_btn:hover { opacity: 0.9; }
.pill_btn {
    background-color: #212121;
    color: white;
    border: none;
    border-radius: 18px;
    padding: 6px 14px;
}
.pill_btn:hover { background-color: #272727; }

/* --- History & Calc --- */
#history_item { border-bottom: 1px solid #303030; padding: 10px 0; }
.log_meta { font-size: 12px; color: #aaaaaa; }

/* --- Calc Modules --- */
#module_header {
    background-color: #212121;
    padding: 8px 12px;
    border-radius: 8px;
    font-weight: 500;
}
.calc_input {
    background: transparent;
    border: none;
    border-bottom: 1px solid #303030;
    color: white;
    padding: 4px;
}
.calc_input:focus { outline: none; border-bottom: 1px solid #3ea6ff; }
.unit_label { font-size: 11px; color: #aaaaaa; }
.output_value { font-family: monospace; font-weight: bold; color: #3ea6ff; text-align: right; }
.output_label { font-size: 12px; color: #aaaaaa; }

#calculate_btn {
    background-color: #065fd4;
    color: white;
    border: none;
    border-radius: 18px;
    padding: 10px;
    font-weight: bold;
}
#calculate_btn:hover { background-color: #054a9e; }

/* --- Toast (Message Box simple simulación) --- */
"""
# Nota: Para un "Toast" nativo complejo en Qt se requieren animaciones custom, 
# aquí usaremos un QMessageBox o status bar por simplicidad en la transferencia.

# --- 2. CLASE PRINCIPAL DE LA APLICACIÓN ---

class UptaLinkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UptaLink - Calculadora de Radioenlace")
        self.resize(1280, 800)
        self.setStyleSheet(STYLESHEET)

        # Widget Central y Layout Principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Header
        self.create_header()
        self.main_layout.addWidget(self.header_frame)

        # Contenedor Splitter (Sidebar | Content)
        self.content_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.content_splitter)

        # 2. Sidebar
        self.create_sidebar()
        self.content_splitter.addWidget(self.sidebar_frame)

        # 3. Main Content
        self.create_main_content()
        self.content_splitter.addWidget(self.main_content_widget)
        
        # Ajustar anchos iniciales
        self.content_splitter.setSizes([240, 1040]) 

        # Referencias a inputs para el cálculo
        self.inputs_map = {}
        self.outputs_map = {}

    def create_header(self):
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(56)
        self.header_frame.setObjectName("header")
        
        layout = QHBoxLayout(self.header_frame)
        
        # Left: Menu + Logo
        self.menu_btn = QToolButton()
        self.menu_btn.setText("☰") # Icono unicode simple
        self.menu_btn.setStyleSheet("border:none; font-size: 20px; padding: 8px; background:transparent; color:white;")
        self.menu_btn.clicked.connect(self.toggle_sidebar)
        
        logo = QLabel()
        logo.setObjectName("logo_label")
        logo.setText('<span id="logo_span">▶</span> UptaLink')
        
        layout.addWidget(self.menu_btn)
        layout.addWidget(logo)
        
        # Center: Search
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0,0,0,0)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Buscar radioenlaces...")
        
        search_btn = QPushButton()
        search_btn.setObjectName("search_btn")
        search_btn.setText("🔍") # Icono unicode
        
        mic_btn = QPushButton()
        mic_btn.setObjectName("mic_btn")
        mic_btn.setText("🎤")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        layout.addWidget(search_container, 1) # Stretch factor 1
        layout.addWidget(mic_btn)
        
        # Right: Actions
        create_btn = QPushButton("📥 Crear") # Icono unicode
        create_btn.setStyleSheet("background-color:#212121; color:white; border:none; border-radius:18px; padding:6px 12px;")
        
        notif_btn = QPushButton("🔔")
        notif_btn.setStyleSheet("background:transparent; border:none; color:white; font-size:18px;")
        
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("background-color:#555; border-radius:16px;")
        
        layout.addWidget(create_btn)
        layout.addWidget(notif_btn)
        layout.addWidget(avatar)

    def create_sidebar(self):
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebar")
        self.sidebar_frame.setFixedWidth(240)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        sidebar_content = QWidget()
        layout = QVBoxLayout(sidebar_content)
        
        # Sección Principal
        layout.addWidget(QLabel("Principal"))
        self.add_nav_item(layout, "🏠", "Inicio", checked=True)
        self.add_nav_item(layout, "🚀", "Shorts")
        self.add_nav_item(layout, "❤️", "Suscripciones")
        
        # Sección Tú
        layout.addSpacing(10)
        layout.addWidget(QLabel("Tú"))
        self.add_nav_item(layout, "🕒", "Historial")
        self.add_nav_item(layout, "📝", "Tus listas")
        
        # Sección Herramientas
        layout.addSpacing(10)
        layout.addWidget(QLabel("Herramientas"))
        self.add_nav_item(layout, "🎨", "Temas")
        self.add_nav_item(layout, "❓", "Ayuda")
        self.add_nav_item(layout, "💲", "Acerca de Pro")
        
        layout.addStretch()
        scroll.setWidget(sidebar_content)
        
        sb_layout = QVBoxLayout(self.sidebar_frame)
        sb_layout.setContentsMargins(0,0,0,0)
        sb_layout.addWidget(scroll)

    def add_nav_item(self, layout, icon, text, checked=False):
        btn = QPushButton(f"{icon}  {text}")
        btn.setObjectName("nav_btn")
        btn.setCheckable(True)
        if checked: btn.setChecked(True)
        layout.addWidget(btn)

    def toggle_sidebar(self):
        # Lógica simple de colapsar/expandir
        if self.sidebar_frame.width() > 100:
            self.sidebar_frame.setFixedWidth(60)
        else:
            self.sidebar_frame.setFixedWidth(240)

    def create_main_content(self):
        self.main_content_widget = QWidget()
        # Usamos un QVBoxLayout para apilar Top Section y Bottom Section
        main_layout = QVBoxLayout(self.main_content_widget)
        
        # --- TOP SECTION (Player + Info) ---
        top_layout = QVBoxLayout()
        
        # PyVista Placeholder
        self.pyvista_container = QFrame()
        self.pyvista_container.setObjectName("player_container")
        self.pyvista_layout = QVBoxLayout(self.pyvista_container)
        self.pyvista_layout.setContentsMargins(0,0,0,0)
        
        # AQUÍ SE INTEGRARÁ PYVISTA
        self.setup_pyvista_widget()
        
        top_layout.addWidget(self.pyvista_container)
        
        # Info Panel
        info_panel = QFrame()
        info_panel.setObjectName("info_panel")
        info_layout = QVBoxLayout(info_panel)
        
        title = QLabel("Cálculo de Radioenlace Punto a Punto - Torre A a Torre B (5GHz)")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top:10px;")
        
        # Action Bar
        action_layout = QHBoxLayout()
        
        channel_info = QLabel("UptaLink Engineering\n12.5K suscriptores")
        sub_btn = QPushButton("Suscribirse")
        sub_btn.setObjectName("subscribe_btn")
        
        left_action_layout = QHBoxLayout()
        left_action_layout.addWidget(channel_info)
        left_action_layout.addSpacing(10)
        left_action_layout.addWidget(sub_btn)
        
        # Botones Pill
        like_btn = QPushButton("👍 245")
        like_btn.setObjectName("pill_btn")
        share_btn = QPushButton("🔗 Compartir")
        share_btn.setObjectName("pill_btn")
        save_btn = QPushButton("📌 Guardar")
        save_btn.setObjectName("pill_btn")
        
        right_action_layout = QHBoxLayout()
        right_action_layout.addWidget(like_btn)
        right_action_layout.addWidget(share_btn)
        right_action_layout.addWidget(save_btn)
        
        action_layout.addLayout(left_action_layout)
        action_layout.addStretch()
        action_layout.addLayout(right_action_layout)
        
        desc = QLabel("Parámetros del enlace: 48km distancia, zona rural.\nEste cálculo estima la zona de Fresnel.")
        desc.setStyleSheet("background-color: #222; padding: 10px; border-radius: 8px; margin-top: 10px;")
        
        info_layout.addWidget(title)
        info_layout.addLayout(action_layout)
        info_layout.addWidget(desc)
        
        top_layout.addWidget(info_panel)
        main_layout.addLayout(top_layout)
        
        # --- BOTTOM SECTION (Grid: History | Calc) ---
        bottom_splitter = QSplitter(Qt.Horizontal)
        
        # Left: History
        history_scroll = QScrollArea()
        history_content = QWidget()
        self.history_layout = QVBoxLayout(history_content)
        self.history_layout.setAlignment(Qt.AlignTop)
        
        # Log inicial
        self.add_history_log("UptaLink Engine", "Inicialización del módulo FSPL completada.")
        
        history_scroll.setWidget(history_content)
        history_scroll.setWidgetResizable(True)
        
        # Right: Inputs & Outputs
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        
        # Module 1: Inputs
        inputs_module = QFrame()
        inputs_layout = QVBoxLayout(inputs_module)
        inputs_layout.addWidget(QLabel("Parámetros de Entrada"))
        
        inputs_grid = QGridLayout()
        self.create_input_grid(inputs_grid)
        inputs_layout.addLayout(inputs_grid)
        
        calc_btn = QPushButton("CALCULAR")
        calc_btn.setObjectName("calculate_btn")
        calc_btn.clicked.connect(self.perform_calculation)
        inputs_layout.addWidget(calc_btn)
        
        # Module 2: Outputs
        outputs_module = QFrame()
        outputs_layout = QVBoxLayout(outputs_module)
        outputs_layout.addWidget(QLabel("Resultados"))
        
        outputs_grid = QGridLayout()
        self.create_output_grid(outputs_grid)
        outputs_layout.addLayout(outputs_grid)
        
        right_layout.addWidget(inputs_module)
        right_layout.addWidget(outputs_module)
        
        bottom_splitter.addWidget(history_scroll)
        bottom_splitter.addWidget(right_col)
        bottom_splitter.setSizes([600, 400]) # Proporción inicial
        
        main_layout.addWidget(bottom_splitter)

    # --- LOGICA PYVISTA ---
    def setup_pyvista_widget(self):
        # Creamos el QtInteractor de PyVista
        self.plotter = QtInteractor(self.pyvista_container)
        self.pyvista_layout.addWidget(self.plotter.interactor)
        
        # Ejemplo visual inicial (Un terreno o simple plano)
        # En un caso real, cargarías tu archivo DEM o datos aquí
        mesh = pv.Plane(center=(0,0,0), direction=(0,1,0), i_size=20, j_size=10)
        self.plotter.add_mesh(mesh, color='green', opacity=0.5)
        self.plotter.add_text("Visualizador Topográfico", position='upper_left', font_size=10, color='white')
        self.plotter.set_background("black")
        self.plotter.show_grid()
        
    # --- LOGICA DE INPUTS/OUTPUTS (Generación Dinámica) ---
    def create_input_grid(self, layout):
        # Datos idénticos al HTML/JS
        inputs = [
            ("Frecuencia", "GHz"), ("Distancia", "km"), ("Potencia TX", "dBm"),
            ("Ganancia Tx", "dBi"), ("Ganancia Rx", "dBi"), ("Pérdidas Cables", "dB"),
            ("Sensibilidad Rx", "dBm"), ("Altura Torre A", "m"), ("Altura Torre B", "m"),
            ("Margen Deseado", "dB")
        ]
        
        for i, (label, unit) in enumerate(inputs):
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size:12px; color:#aaa;")
            
            line_edit = QLineEdit()
            line_edit.setObjectName(f"in_{i}")
            line_edit.setPlaceholderText("0")
            self.inputs_map[f"in_{i}"] = line_edit # Guardamos referencia
            
            unit_lbl = QLabel(unit)
            unit_lbl.setObjectName("unit_label")
            
            layout.addWidget(lbl, i, 0)
            layout.addWidget(line_edit, i, 1)
            layout.addWidget(unit_lbl, i, 2)

    def create_output_grid(self, layout):
        outputs = [
            "Pérdidas FSPL", "Presupuesto Potencia", "Señal Recibida", "Margen de Enlace",
            "Radio Zona Fresnel", "Estado del Enlace", "Throughput Est.", "Distancia Objetivo",
            "Altura Objetivo", "Jitter Estimado"
        ]
        
        for i, label in enumerate(outputs):
            lbl = QLabel(label)
            lbl.setObjectName("output_label")
            
            val = QLabel("---")
            val.setObjectName("output_value")
            self.outputs_map[f"out_{i}"] = val
            
            layout.addWidget(lbl, i, 0)
            layout.addWidget(val, i, 1)

    def add_history_log(self, user, text):
        item = QWidget()
        item.setObjectName("history_item")
        h_layout = QHBoxLayout(item)
        
        avatar = QLabel("🤖") # Icono sistema
        avatar.setStyleSheet("background-color:#333; border-radius:10px; padding:4px;")
        
        content_layout = QVBoxLayout()
        meta = QLabel(f"{user}  |  Hace un momento")
        meta.setObjectName("log_meta")
        msg = QLabel(text)
        
        content_layout.addWidget(meta)
        content_layout.addWidget(msg)
        
        h_layout.addWidget(avatar)
        h_layout.addLayout(content_layout)
        
        self.history_layout.insertWidget(0, item) # Insertar al inicio

    # --- LOGICA DE CALCULO (Python) ---
    def perform_calculation(self):
        try:
            # Obtener valores
            freq = float(self.inputs_map["in_0"].text())
            dist = float(self.inputs_map["in_1"].text())
            p_tx = float(self.inputs_map["in_2"].text())
            g_tx = float(self.inputs_map["in_3"].text())
            g_rx = float(self.inputs_map["in_4"].text())
            losses = float(self.inputs_map["in_5"].text())
            
            if freq == 0 or dist == 0:
                QMessageBox.warning(self, "Error", "Por favor ingresa Frecuencia y Distancia")
                return

            # Cálculos
            # FSPL = 20log10(d) + 20log10(f) + 92.45
            fspl = (20 * math.log10(dist) + 20 * math.log10(freq) + 92.45)
            
            budget = p_tx + g_tx + g_rx - losses
            rssi = budget - fspl
            
            # Fresnel Radio aprox
            r_fresnel = 8.66 * math.sqrt(dist / freq)
            
            # Actualizar Outputs
            self.outputs_map["out_0"].setText(f"{fspl:.2f} dB")
            self.outputs_map["out_1"].setText(f"{budget:.2f} dBm")
            self.outputs_map["out_2"].setText(f"{rssi:.2f} dBm")
            
            margin = rssi - (-80) # Asumiendo -80dBm referencia
            self.outputs_map["out_3"].setText(f"{margin:.2f} dB")
            self.outputs_map["out_4"].setText(f"{r_fresnel:.2f} m")
            
            estado = "Excelente" if rssi > -70 else "Crítico"
            color = "#00ff00" if rssi > -70 else "#ff5555"
            self.outputs_map["out_5"].setText(estado)
            self.outputs_map["out_5"].setStyleSheet(f"color:{color}")
            
            self.outputs_map["out_6"].setText("150 Mbps") # Dummy
            self.outputs_map["out_7"].setText(f"{dist} km")
            self.outputs_map["out_8"].setText("45 m") # Dummy
            self.outputs_map["out_9"].setText("2 ms") # Dummy
            
            # Agregar al Historial
            self.add_history_log("Calculadora Manual", f"Enlace {freq}GHz a {dist}km. RSSI: {rssi:.2f} dBm.")
            
            # Feedback Visual (Toast simulado con QMessageBox por simplicidad, o Status Bar)
            self.statusBar().showMessage("Cálculo completado con éxito", 3000)
            
        except ValueError:
            QMessageBox.critical(self, "Error", "Por favor ingresa solo números válidos.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UptaLinkApp()
    window.show()
    sys.exit(app.exec())