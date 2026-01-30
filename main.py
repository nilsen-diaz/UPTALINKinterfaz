# Prototipo de intefaz estilo Youtube y UISP Desing Center
import sys
import math
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QScrollArea, 
    QFrame, QSplitter, QToolButton, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor

# --- 1. DEFINICIÓN DE ESTILOS (YOUTUBE DARK MODE) ---
STYLESHEET = """
/* Fondo General */
QMainWindow, QWidget {
    background-color: #0f0f0f;
    color: #ffffff;
    font-family: 'Roboto', 'Segoe UI', sans-serif;
    font-size: 14px;
}

/* Header */
QFrame#header_frame {
    background-color: #0f0f0f;
    border: none;
}
QPushButton#icon_btn {
    background-color: transparent;
    border: none;
    border-radius: 50%;
    padding: 8px;
}
QPushButton#icon_btn:hover {
    background-color: #272727;
}
QLabel#logo_text {
    font-size: 18px;
    font-weight: bold;
    color: white;
    letter-spacing: -0.5px;
}
QLabel#logo_icon {
    color: #ff0000;
    font-size: 24px;
}

/* Barra de Búsqueda (Pill Shape) */
QWidget#search_container {
    background-color: #121212;
    border: 1px solid #303030;
    border-radius: 40px;
    padding: 0;
}
QLineEdit#search_input {
    background-color: transparent;
    border: none;
    color: white;
    padding: 8px 16px;
    font-size: 16px;
}
QLineEdit#search_input:focus {
    outline: none;
}
QPushButton#search_btn {
    background-color: #222222;
    border: none;
    border-top-right-radius: 40px;
    border-bottom-right-radius: 40px;
    padding: 0 20px;
}
QPushButton#search_btn:hover {
    background-color: #303030;
}
QPushButton#mic_btn {
    background-color: #181818;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
}
QPushButton#mic_btn:hover {
    background-color: #303030;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #0f0f0f;
}
QPushButton#nav_item {
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 0 12px; 
    text-align: left;
    color: white;
    height: 40px;
    font-size: 14px;
}
QPushButton#nav_item:hover {
    background-color: #272727;
}
QPushButton#nav_item QLabel {
    background-color: transparent;
    padding-left: 24px; 
}
QLabel#section_title {
    padding: 8px 24px;
    font-weight: bold;
    font-size: 16px;
    color: white;
}

/* Main Content Area */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background: #0f0f0f; width: 8px; margin: 0px;
}
QScrollBar::handle:vertical {
    background: #717171; min-height: 20px; border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #aaaaaa;
}

/* Visor / Player */
QFrame#player_container {
    background-color: black;
    border-radius: 0px; 
}
QLabel#placeholder_text {
    color: #555;
    font-size: 16px;
}

/* Sección Info y Comentarios (Calculadora) */
QFrame#info_panel {
    background-color: #0f0f0f;
    border-bottom: 1px solid #303030;
    padding: 12px 24px;
}
QPushButton#subscribe_btn {
    background-color: white;
    color: black;
    border: none;
    border-radius: 18px;
    padding: 8px 16px;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 12px;
}
QPushButton#subscribe_btn:hover {
    background-color: #d9d9d9;
}

/* Inputs de Calculadora estilo YouTube */
QLabel#param_label {
    font-size: 12px;
    color: #aaaaaa;
    margin-bottom: 4px;
}
QLineEdit#calc_input {
    background-color: #121212;
    border: 1px solid #303030;
    border-radius: 4px;
    color: white;
    padding: 8px;
}
QLineEdit#calc_input:focus {
    border: 1px solid #3ea6ff;
}
QLabel#output_label {
    font-size: 12px;
    color: #aaaaaa;
}
QLabel#output_value {
    font-size: 14px;
    color: white;
    font-weight: bold;
}
QPushButton#calculate_btn {
    background-color: #3ea6ff;
    color: black; 
    border: none;
    border-radius: 18px;
    padding: 10px 24px;
    font-weight: bold;
    text-transform: uppercase;
}
QPushButton#calculate_btn:hover {
    background-color: #65b8ff;
}

/* History (Comentarios) */
QWidget#history_item {
    border-bottom: 1px solid #2f2f2f;
    padding: 12px 0;
}
"""

class UptaLinkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UptaLink - Radio Link Calculator")
        self.resize(1280, 800)
        self.setStyleSheet(STYLESHEET)

        # Mapas de datos
        self.inputs_map = {}
        self.outputs_map = {}
        self.sidebar_buttons = [] 

        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Estructura Principal
        self.setup_ui()
        
    def setup_ui(self):
        # --- 1. HEADER ---
        self.header_frame = QFrame()
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setFixedHeight(56)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(0, 0, 16, 0)
        
        # Left: Menu & Logo
        self.menu_btn = QToolButton()
        self.menu_btn.setText("☰")
        self.menu_btn.setStyleSheet("font-size: 18px; color: white; background: transparent; border: none; padding: 10px;")
        self.menu_btn.clicked.connect(self.toggle_sidebar)
        
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0,0,0,0)
        logo_layout.setSpacing(0)
        logo_icon = QLabel("▶")
        logo_icon.setObjectName("logo_icon")
        logo_text = QLabel("UptaLink")
        logo_text.setObjectName("logo_text")
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        
        header_layout.addWidget(self.menu_btn)
        header_layout.addWidget(logo_widget)
        header_layout.addSpacing(16) 
        
        # Center: Search
        search_widget = QWidget()
        search_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0,0,0,0)
        search_layout.setSpacing(0)
        
        search_container = QWidget()
        search_container.setObjectName("search_container")
        search_container.setFixedHeight(40)
        sc_layout = QHBoxLayout(search_container)
        sc_layout.setContentsMargins(0,0,0,0)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Buscar")
        
        search_btn = QPushButton("🔍")
        search_btn.setObjectName("search_btn")
        
        sc_layout.addWidget(self.search_input)
        sc_layout.addWidget(search_btn)
        
        mic_btn = QPushButton("🎤")
        mic_btn.setObjectName("mic_btn")
        mic_btn.setFixedSize(40, 40)
        
        search_layout.addWidget(search_container)
        search_layout.addWidget(mic_btn)
        header_layout.addWidget(search_widget, 1)
        
        # Right: Actions
        create_btn = QPushButton("📥")
        create_btn.setObjectName("icon_btn")
        notif_btn = QPushButton("🔔")
        notif_btn.setObjectName("icon_btn")
        
        avatar = QLabel()
        avatar.setFixedSize(32, 32)
        avatar.setStyleSheet("background-color:#555; border-radius:50%;")
        
        header_layout.addWidget(create_btn)
        header_layout.addWidget(notif_btn)
        header_layout.addWidget(avatar)

        self.main_layout.addWidget(self.header_frame)

        # --- SPLITTER PRINCIPAL (Sidebar + Content) ---
        self.content_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.content_splitter)
        
        # 2. SIDEBAR
        self.create_sidebar()
        self.content_splitter.addWidget(self.sidebar_frame)
        
        # 3. MAIN CONTENT
        self.create_main_content()
        self.content_splitter.addWidget(self.main_content_widget)
        
        # Ajustes iniciales
        self.content_splitter.setSizes([240, 1040])
        self.content_splitter.setHandleWidth(0) 

    def create_sidebar(self):
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("sidebar")
        self.sidebar_frame.setFixedWidth(240)
        
        sidebar_content = QWidget()
        layout = QVBoxLayout(sidebar_content)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(0)
        
        self.add_nav_item(layout, "🏠", "Inicio", True) 
        self.add_nav_item(layout, "🚀", "Shorts")
        self.add_nav_item(layout, "📺", "Suscripciones")
        
        layout.addSpacing(8)
        line = QFrame(); line.setFrameShape(QFrame.HLine); line.setStyleSheet("background-color: #303030; margin: 0 12px;")
        layout.addWidget(line)
        layout.addSpacing(8)
        
        layout.addWidget(QLabel("Tú"))
        title_layout = layout.itemAt(layout.count()-1).widget().layout()
        if title_layout: title_layout.setContentsMargins(24, 8, 0, 8) 
        
        self.add_nav_item(layout, "🕒", "Historial")
        self.add_nav_item(layout, "▶️", "Tus videos")
        self.add_nav_item(layout, "⏱️", "Ver más tarde")
        self.add_nav_item(layout, "👍", "Videos que me gustan")

        layout.addStretch()
        
        sb_layout = QVBoxLayout(self.sidebar_frame)
        sb_layout.setContentsMargins(0,0,0,0)
        sb_layout.addWidget(sidebar_content)

    def add_nav_item(self, layout, icon, text, active=False):
        btn = QPushButton()
        btn.setObjectName("nav_item")
        btn.setCursor(Qt.PointingHandCursor)
        
        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(12, 0, 12, 0)
        btn_layout.setSpacing(12)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 18px; background: transparent; min-width: 24px;")
        
        lbl_text = QLabel(text)
        lbl_text.setStyleSheet("background: transparent;")
        
        btn_layout.addWidget(lbl_icon)
        btn_layout.addWidget(lbl_text)
        btn_layout.addStretch()
        
        if active:
            btn.setStyleSheet("background-color: #272727; font-weight: bold;")
        
        layout.addWidget(btn)
        self.sidebar_buttons.append(lbl_text)

    def toggle_sidebar(self):
        current_width = self.sidebar_frame.width()
        
        if current_width > 100: 
            self.sidebar_frame.setFixedWidth(72)
            for lbl in self.sidebar_buttons:
                lbl.hide()
            for btn in self.sidebar_frame.findChild(QFrame).findChildren(QPushButton):
                if btn.objectName() == "nav_item":
                    btn.layout().setContentsMargins(0, 0, 0, 0)
        else: 
            self.sidebar_frame.setFixedWidth(240)
            for lbl in self.sidebar_buttons:
                lbl.show()
            for btn in self.sidebar_frame.findChild(QFrame).findChildren(QPushButton):
                if btn.objectName() == "nav_item":
                    btn.layout().setContentsMargins(12, 0, 12, 0)

    def create_main_content(self):
        self.main_content_widget = QWidget()
        main_layout = QVBoxLayout(self.main_content_widget)
        
        # --- VISOR (TOP) ---
        self.player_container = QFrame()
        self.player_container.setObjectName("player_container")
        self.player_container.setFixedHeight(400) 
        
        player_layout = QVBoxLayout(self.player_container)
        placeholder = QLabel(
            "⚠️ VISOR 3D TOPOGRÁFICO\n\n"
            "El motor gráfico se ha deshabilitado para mantener la compatibilidad.\n"
            "Aquí se visualizaría el perfil del terreno y la zona Fresnel."
        )
        placeholder.setObjectName("placeholder_text")
        placeholder.setAlignment(Qt.AlignCenter)
        player_layout.addWidget(placeholder)
        
        main_layout.addWidget(self.player_container)
        
        # --- INFO PANEL (Titulo y Controles) ---
        info_frame = QFrame()
        info_frame.setObjectName("info_panel")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)
        
        title = QLabel("Cálculo de Radioenlace Punto a Punto: Torre A ↔ Torre B (5 GHz)")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        actions_layout = QHBoxLayout()
        ch_info = QLabel("UptaLink Engineering  •  12.5K suscriptores")
        sub_btn = QPushButton("Suscribirse")
        sub_btn.setObjectName("subscribe_btn")
        
        actions_left = QHBoxLayout()
        actions_left.addWidget(ch_info)
        actions_left.addWidget(sub_btn)
        
        actions_right = QHBoxLayout()
        actions_right.addStretch()
        for icon, txt in [("👍", "245"), ("👎", ""), ("🔗", "Compartir"), ("💾", "Guardar")]:
            btn = QPushButton(f"{icon} {txt}" if txt else icon)
            btn.setStyleSheet("background:transparent; color:#aaa; border:none; padding: 8px; font-weight:bold; border-radius:18px;")
            btn.setObjectName("icon_btn")
            actions_right.addWidget(btn)
            
        info_layout.addWidget(title)
        info_layout.addLayout(actions_left)
        info_layout.addLayout(actions_right)
        
        desc = QLabel("Calculadora de enlaces microondas basada en FSPL y curvatura terrestre. \nParámetros de ingeniería para despliegos WISP.")
        desc.setStyleSheet("color: #fff; font-size: 14px; margin-top:8px;")
        info_layout.addWidget(desc)
        
        main_layout.addWidget(info_frame)
        
        # --- BOTTOM SECTION (Comentarios/Calculadora) ---
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(24)
        
        # Columna Izquierda: Calculadora (Principal)
        calc_container = QFrame()
        calc_layout = QVBoxLayout(calc_container)
        calc_layout.setSpacing(20)
        
        # Inputs
        inputs_group = QWidget()
        ig_layout = QVBoxLayout(inputs_group)
        ig_layout.addWidget(QLabel("PARÁMETROS DE INGENIERÍA"))
        inputs_grid = QGridLayout()
        inputs_grid.setSpacing(12)
        self.create_input_grid(inputs_grid)
        ig_layout.addLayout(inputs_grid)
        
        calc_btn = QPushButton("CALCULAR ENLACE")
        calc_btn.setObjectName("calculate_btn")
        calc_btn.clicked.connect(self.perform_calculation)
        calc_btn.setMaximumWidth(200)
        # --- AQUÍ ESTABA EL ERROR Y YA HA SIDO ELIMINADO ---
        
        # Outputs
        outputs_group = QWidget()
        og_layout = QVBoxLayout(outputs_group)
        og_layout.addWidget(QLabel("RESULTADOS DEL SISTEMA"))
        outputs_grid = QGridLayout()
        outputs_grid.setSpacing(12)
        self.create_output_grid(outputs_grid)
        og_layout.addLayout(outputs_grid)
        
        calc_layout.addWidget(inputs_group)
        calc_layout.addWidget(calc_btn, 0, Qt.AlignCenter) # Centrado correcto en el layout
        calc_layout.addWidget(outputs_group)
        
        # Columna Derecha: Historial (Recomendaciones)
        history_container = QFrame()
        history_container.setFixedWidth(350) 
        hc_layout = QVBoxLayout(history_container)
        hc_layout.addWidget(QLabel("BITÁCORA DE OPERACIONES"))
        
        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setFrameShape(QFrame.NoFrame)
        
        h_content = QWidget()
        self.history_layout = QVBoxLayout(h_content)
        self.history_layout.setAlignment(Qt.AlignTop)
        self.history_layout.setSpacing(0)
        self.add_history_log("Sistema", "Interfaz inicializada. Esperando datos...")
        
        history_scroll.setWidget(h_content)
        hc_layout.addWidget(history_scroll)

        bottom_layout.addWidget(calc_container, 1) 
        bottom_layout.addWidget(history_container)
        
        main_layout.addLayout(bottom_layout)
        main_layout.addStretch()

    def create_input_grid(self, layout):
        inputs = [
            ("Frecuencia (GHz)", "5.0"), ("Distancia (km)", "15"), 
            ("Potencia TX (dBm)", "30"), ("Ganancia TX (dBi)", "24"),
            ("Ganancia RX (dBi)", "24"), ("Pérdidas (dB)", "3"),
            ("Sensibilidad RX", "-80"), ("Altura Torre A (m)", "30"), 
            ("Altura Torre B (m)", "30"), ("Margen (dB)", "10")
        ]
        for i, (label, default) in enumerate(inputs):
            row = i // 2
            col = (i % 2) * 3
            
            lbl = QLabel(label)
            lbl.setObjectName("param_label")
            
            inp = QLineEdit(default)
            inp.setObjectName("calc_input")
            self.inputs_map[f"in_{i}"] = inp
            
            layout.addWidget(lbl, row, col)
            layout.addWidget(inp, row, col + 1, 1, 2)

    def create_output_grid(self, layout):
        outputs = ["Pérdidas FSPL (dB)", "Presupuesto Pot. (dBm)", "RSSI Recibido (dBm)", 
                   "Margen Real (dB)", "Radio Fresnel (m)", "Estado Enlace", 
                   "Throughput Est.", "Distancia Obj.", "Altura Obj.", "Jitter"]
        for i, label in enumerate(outputs):
            row = i // 2
            col = (i % 2) * 3
            
            lbl = QLabel(label)
            lbl.setObjectName("output_label")
            
            val = QLabel("---")
            val.setObjectName("output_value")
            self.outputs_map[f"out_{i}"] = val
            
            layout.addWidget(lbl, row, col)
            layout.addWidget(val, row, col + 1, 1, 2)

    def add_history_log(self, user, text):
        item = QWidget()
        item.setObjectName("history_item")
        h_layout = QHBoxLayout(item)
        h_layout.setContentsMargins(0,0,0,0)
        
        avatar = QLabel("U")
        avatar.setFixedSize(24, 24)
        avatar.setStyleSheet(f"background-color: {'#555' if user == 'Sistema' else '#3ea6ff'}; color:white; border-radius:50%; font-size:10px; font-weight:bold;")
        avatar.setAlignment(Qt.AlignCenter)
        
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        meta = QLabel(f"@{user.lower().replace(' ', '_')}  •  hace un momento")
        meta.setStyleSheet("font-size: 11px; color: #606060;")
        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setStyleSheet("color: #fff;")
        
        content_layout.addWidget(meta)
        content_layout.addWidget(msg)
        
        h_layout.addWidget(avatar)
        h_layout.addLayout(content_layout)
        
        self.history_layout.insertWidget(0, item)

    def perform_calculation(self):
        try:
            freq = float(self.inputs_map["in_0"].text())
            dist = float(self.inputs_map["in_1"].text())
            p_tx = float(self.inputs_map["in_2"].text())
            g_tx = float(self.inputs_map["in_3"].text())
            g_rx = float(self.inputs_map["in_4"].text())
            losses = float(self.inputs_map["in_5"].text())
            sens = float(self.inputs_map["in_6"].text())
            
            fspl = (20 * math.log10(dist) + 20 * math.log10(freq) + 92.45)
            budget = p_tx + g_tx + g_rx - losses
            rssi = budget - fspl
            margin = rssi - sens
            r_fresnel = 8.66 * math.sqrt(dist / freq)
            
            self.outputs_map["out_0"].setText(f"{fspl:.2f}")
            self.outputs_map["out_1"].setText(f"{budget:.2f}")
            self.outputs_map["out_2"].setText(f"{rssi:.2f}")
            self.outputs_map["out_3"].setText(f"{margin:.2f}")
            self.outputs_map["out_4"].setText(f"{r_fresnel:.2f}")
            
            estado = "ESTABLE" if margin > 10 else "CRÍTICO"
            color = "#3ea6ff" if margin > 10 else "#ff0000"
            self.outputs_map["out_5"].setText(estado)
            self.outputs_map["out_5"].setStyleSheet(f"color:{color}; font-size:14px;")
            
            self.outputs_map["out_6"].setText(f"~{max(0, 150 - (dist*2))} Mbps")
            self.outputs_map["out_7"].setText(f"{dist} km")
            self.outputs_map["out_8"].setText("N/A")
            self.outputs_map["out_9"].setText(f"< {max(1, dist/10)} ms")

            self.add_history_log("Calculadora", f"Cálculo completado: RSSI {rssi:.1f} dBm ({estado})")
            
        except ValueError:
            self.add_history_log("Error", "Entrada inválida detectada. Verifique números.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UptaLinkApp()
    window.show()
    sys.exit(app.exec())