import sys
import os

# --- FIX DE COMPATIBILIDAD WINDOWS (OPENGL / DIRECTX) ---
# Esto fuerza a Qt a usar DirectX (ANGLE) en lugar de OpenGL nativo,
# solucionando el error "failed to get wglChoosePixelFormatARB"
os.environ["QT_OPENGL"] = "angle" 
# -------------------------------------------------------

import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QPushButton, QLabel, QLineEdit, QScrollArea, 
    QFrame, QSizePolicy, QStackedWidget, QGroupBox, QSplitter,
    QToolButton, QStyle, QTextEdit, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, Signal, Slot
from PySide6.QtGui import QIcon, QFont, QColor, QPalette
import pyvista as pv
from pyvistaqt import QtInteractor

# --- ESTILOS (QSS) - DISEÑO YOUTUBE + UISP (MODO OSCURO) ---
STYLESHEET = """
QMainWindow {
    background-color: #0f0f0f;
}

/* Barra Superior */
QWidget#HeaderContainer {
    background-color: #0f0f0f;
    border-bottom: 1px solid #303030;
}

QPushButton#HeaderBtn {
    background-color: transparent;
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    font-size: 16px;
}
QPushButton#HeaderBtn:hover {
    background-color: #272727;
}

QLineEdit#SearchBar {
    background-color: #121212;
    border: 1px solid #303030;
    border-radius: 20px;
    padding: 5px 15px;
    color: white;
    font-size: 14px;
}
QLineEdit#SearchBar:focus {
    border: 1px solid #1c62b9;
}

QPushButton#SearchBtn {
    background-color: #222222;
    border: 1px solid #303030;
    border-left: none;
    border-top-right-radius: 20px;
    border-bottom-right-radius: 20px;
    padding: 0 15px;
    color: white;
}

/* Barra Lateral */
QWidget#SideBar {
    background-color: #0f0f0f;
}

QPushButton#SideNavBtn {
    background-color: transparent;
    color: white;
    text-align: left;
    padding: 10px 24px;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#SideNavBtn:hover {
    background-color: #272727;
}

QPushButton#SideNavBtn:checked {
    background-color: #272727;
    font-weight: bold;
}

QLabel#SectionLabel {
    color: #aaaaaa;
    font-size: 16px;
    font-weight: bold;
    padding: 8px 24px;
}

QFrame#SideSeparator {
    background-color: #303030;
    max-height: 1px;
    margin: 5px 12px;
}

/* Cuerpo Principal */
QWidget#MainContent {
    background-color: #0f0f0f;
}

/* Visor 3D */
QWidget#PlayerContainer {
    background-color: black;
    border-radius: 12px;
    border: 1px solid #303030;
}
QLabel#OverlayText {
    color: white;
    background-color: rgba(0,0,0,150);
    padding: 5px;
    border-radius: 4px;
}

/* Panel de Información */
QLabel#VideoTitle {
    color: white;
    font-size: 20px;
    font-weight: bold;
}
QPushButton#ActionBtn {
    background-color: #272727;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 18px;
    font-weight: 500;
    text-transform: uppercase;
}
QPushButton#ActionBtn:hover {
    background-color: #3f3f3f;
}
QPushButton#SubscribeBtn {
    background-color: white;
    color: black;
    font-weight: bold;
    border-radius: 18px;
}
QPushButton#SubscribeBtn:hover {
    background-color: #d9d9d9;
}

/* Módulos I/O */
QGroupBox {
    color: white;
    border: 1px solid #303030;
    border-radius: 10px;
    margin-top: 20px;
    padding-top: 10px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QLineEdit#InputField {
    background-color: #121212;
    border: 1px solid #303030;
    color: white;
    padding: 5px;
    border-radius: 4px;
}
QLineEdit#OutputField {
    background-color: #1a1a1a;
    border: none;
    color: #aaaaaa;
    padding: 5px;
    border-radius: 4px;
}
QPushButton#CalcBtn, QPushButton#SaveBtn, QPushButton#ResetBtn {
    background-color: #3ea6ff;
    color: black;
    font-weight: bold;
    border: none;
    border-radius: 4px;
    padding: 8px;
}
QPushButton#ResetBtn {
    background-color: #ff0000;
    color: white;
}
"""

class SideBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SideBar")
        # Corrección visual: Permitir que el sidebar se encoja hasta 0
        self.setMinimumWidth(0) 
        self.setFixedWidth(240) # Ancho inicial expandido
        self.is_expanded = True
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Scroll para el sidebar
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background-color: transparent;")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        self.scroll.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll)
        
        self.items = [] # Para guardar referencias a los botones y animar texto

    def add_section_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("SectionLabel")
        self.content_layout.addWidget(lbl)
        self.items.append({'type': 'label', 'widget': lbl})

    def add_nav_item(self, text, icon_char, callback):
        btn = QPushButton(icon_char + "  " + text)
        btn.setObjectName("SideNavBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        self.content_layout.addWidget(btn)
        self.items.append({'type': 'btn', 'widget': btn, 'icon': icon_char, 'text': text})

    def add_separator(self):
        sep = QFrame()
        sep.setObjectName("SideSeparator")
        self.content_layout.addWidget(sep)

    def toggle(self):
        self.is_expanded = not self.is_expanded
        
        # Animación de ancho
        self.anim = QPropertyAnimation(self, b"maximumWidth")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.InOutQuart)
        
        target_width = 240 if self.is_expanded else 72
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(target_width)
        self.anim.start()
        
        # Ajustar contenido visible
        for item in self.items:
            if item['type'] == 'btn':
                if self.is_expanded:
                    item['widget'].setText(item['icon'] + "  " + item['text'])
                else:
                    item['widget'].setText(item['icon'])
            elif item['type'] == 'label':
                item['widget'].setVisible(self.is_expanded)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("UPTALINK Design Center")
        self.resize(1280, 800)
        self.setStyleSheet(STYLESHEET)

        # Widget Central y Layout Principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # --- 1. BARRA LATERAL ---
        self.sidebar = SideBar()
        self.setup_sidebar_content()
        main_layout.addWidget(self.sidebar)

        # Contenedor Derecho (Header + Body)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0,0,0,0)
        right_layout.setSpacing(0)

        # --- 2. ENCABEZADO ---
        header = self.create_header()
        right_layout.addWidget(header)

        # --- 3. CUERPO PRINCIPAL (SCROLL) ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { background-color: #0f0f0f; border: none; }")
        
        body_widget = QWidget()
        body_widget.setObjectName("MainContent")
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(24, 24, 24, 24)
        body_layout.setSpacing(20)

        # --- A. REPRODUCTOR 3D (Simulación PyVista) ---
        player_container = self.create_3d_player()
        body_layout.addWidget(player_container, stretch=2)

        # --- B. PANEL DE INFORMACIÓN Y MÓDULOS ---
        bottom_splitter = QWidget()
        bottom_layout = QHBoxLayout(bottom_splitter)
        bottom_layout.setContentsMargins(0,0,0,0)

        # Panel Izquierdo (Info + Historial)
        left_panel = self.create_info_panel()
        bottom_layout.addWidget(left_panel, stretch=2)

        # Panel Derecho (Inputs/Outputs)
        right_panel = self.create_io_modules()
        bottom_layout.addWidget(right_panel, stretch=1)

        body_layout.addWidget(bottom_splitter)
        
        scroll_area.setWidget(body_widget)
        right_layout.addWidget(scroll_area)

        main_layout.addWidget(right_container)

    def setup_sidebar_content(self):
        self.sidebar.add_nav_item("Inicio", "🏠", lambda: print("Ir a Inicio"))
        self.sidebar.add_nav_item("Suscripciones", "💰", lambda: print("Ver Gastos"))
        self.sidebar.add_separator()
        self.sidebar.add_section_label("DATASHEETS")
        self.sidebar.add_nav_item("Antenas Históricas", "📡", lambda: print("Antenas"))
        self.sidebar.add_nav_item("Registradas", "📂", lambda: print("Guardadas"))
        self.sidebar.add_separator()
        self.sidebar.add_section_label("Más de UPTALINK")
        self.sidebar.add_nav_item("UPTALINK Premium", "💎", lambda: print("Premium"))
        self.sidebar.add_nav_item("UPTALINK Lite", "🌐", lambda: print("Lite"))
        self.sidebar.add_nav_item("UPTALINK Básico", "📉", lambda: print("Básico (Sin 3D)"))
        self.sidebar.add_separator()
        self.sidebar.add_section_label("Configuración")
        self.sidebar.add_nav_item("Temas", "🎨", lambda: print("Temas"))
        self.sidebar.add_nav_item("Configuración", "⚙️", lambda: print("Config"))
        self.sidebar.add_nav_item("Ayuda", "❓", lambda: print("Ayuda"))

    def create_header(self):
        header = QWidget()
        header.setObjectName("HeaderContainer")
        header.setFixedHeight(56)
        layout = QHBoxLayout(header)
        
        # Menu Hamburguesa
        menu_btn = QPushButton("☰")
        menu_btn.setObjectName("HeaderBtn")
        menu_btn.clicked.connect(self.sidebar.toggle)
        layout.addWidget(menu_btn)

        # Logo
        logo_lbl = QLabel("UPTALINK")
        logo_lbl.setStyleSheet("font-weight: bold; font-size: 18px; color: white; padding: 0 10px;")
        logo_lbl.setCursor(Qt.PointingHandCursor)
        layout.addWidget(logo_lbl)

        # Buscador
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0,0,0,0)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBar")
        self.search_input.setPlaceholderText("Buscar enlaces, clientes, GPS...")
        
        search_btn = QPushButton("🔍")
        search_btn.setObjectName("SearchBtn")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        
        layout.addWidget(search_container)
        
        # Micrófono (Simulado)
        mic_btn = QPushButton("🎙️")
        mic_btn.setObjectName("HeaderBtn")
        layout.addWidget(mic_btn)

        layout.addStretch()

        # Botones Header Derecho
        create_btn = QPushButton("📹")
        create_btn.setObjectName("HeaderBtn")
        layout.addWidget(create_btn)

        notify_btn = QPushButton("🔔")
        notify_btn.setObjectName("HeaderBtn")
        layout.addWidget(notify_btn)

        user_btn = QPushButton("👤")
        user_btn.setObjectName("HeaderBtn")
        layout.addWidget(user_btn)

        return header

    def create_3d_player(self):
        container = QWidget()
        container.setObjectName("PlayerContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)

        # Toolbar del Reproductor
        toolbar = QWidget()
        toolbar.setStyleSheet("background-color: rgba(0,0,0,0.5); padding: 5px;")
        tb_layout = QHBoxLayout(toolbar)
        
        btn_3d = QPushButton("Topo 3D")
        btn_3d.setStyleSheet("color: white; border: none; background: transparent;")
        btn_3d.clicked.connect(self.update_plot_3d)
        
        btn_2d = QPushButton("Patrón 2D")
        btn_2d.setStyleSheet("color: #aaa; border: none; background: transparent;")
        btn_2d.clicked.connect(self.update_plot_2d)
        
        btn_cine = QPushButton("Cine 🎬")
        btn_cine.setStyleSheet("color: #aaa; border: none; background: transparent;")
        
        tb_layout.addWidget(btn_3d)
        tb_layout.addWidget(btn_2d)
        tb_layout.addStretch()
        tb_layout.addWidget(QLabel("Calidad: 4K"))
        tb_layout.addWidget(btn_cine)

        # Widget PyVista con manejo de errores (Fallback)
        try:
            self.plotter = QtInteractor(container)
            # Crear topografía dummy
            x = np.arange(-10, 10, 0.5)
            y = np.arange(-10, 10, 0.5)
            x, y = np.meshgrid(x, y)
            z = np.sin(np.sqrt(x**2 + y**2))
            
            grid = pv.StructuredGrid(x, y, z)
            self.plotter.add_mesh(grid, color="green", show_edges=True)
            self.plotter.add_text("Enlace: Pt_A -> Pt_B", position='upper_left', color='white', font_size=10)
            self.plotter.set_background("black")
            self.plotter.show_grid()
            layout.addWidget(self.plotter)
        except Exception as e:
            # Fallback si OpenGL falla completamente
            error_label = QLabel("ERROR 3D: Controladores de video incompatibles.\nActualice sus drivers o use ANGLE.")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-weight: bold; padding: 20px;")
            layout.addWidget(error_label)
            print(f"Error al inicializar PyVista: {e}")

        layout.addWidget(toolbar)
        return container

    def update_plot_3d(self):
        try:
            if hasattr(self, 'plotter'):
                self.plotter.clear()
                # Volver a cargar terreno
                x = np.arange(-10, 10, 0.5)
                y = np.arange(-10, 10, 0.5)
                x, y = np.meshgrid(x, y)
                z = np.sin(np.sqrt(x**2 + y**2))
                grid = pv.StructuredGrid(x, y, z)
                self.plotter.add_mesh(grid, color="green", show_edges=True)
                self.plotter.add_text("Modo: Topografía 3D", position='upper_left', color='white')
        except Exception:
            pass

    def update_plot_2d(self):
        try:
            if hasattr(self, 'plotter'):
                self.plotter.clear()
                # Simular patrón de radiación 2D (plot simple)
                theta = np.linspace(0, 2*np.pi, 50)
                r = np.abs(np.sin(4*theta))
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                z = np.zeros_like(x)
                
                # Crear líneas simples para 2D
                points = np.column_stack((x, y, z))
                self.plotter.add_points(points, color='red', point_size=10)
                self.plotter.add_text("Modo: Patrón de Radiación 2D", position='upper_left', color='white')
        except Exception:
            pass

    def create_info_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Título
        title = QLabel("Diseño Radioenlace: Torre Centro - Sector Norte")
        title.setObjectName("VideoTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        # Acciones
        actions_layout = QHBoxLayout()
        sub_btn = QPushButton("Suscribirse")
        sub_btn.setObjectName("SubscribeBtn")
        like_btn = QPushButton("👍 1.2K")
        like_btn.setObjectName("ActionBtn")
        share_btn = QPushButton("↗ Compartir")
        share_btn.setObjectName("ActionBtn")
        save_btn = QPushButton("📥 Guardar")
        save_btn.setObjectName("ActionBtn")
        
        actions_layout.addWidget(sub_btn)
        actions_layout.addWidget(like_btn)
        actions_layout.addWidget(share_btn)
        actions_layout.addWidget(save_btn)
        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Descripción Expandible
        desc_group = QGroupBox("Descripción y Presupuesto")
        desc_layout = QVBoxLayout(desc_group)
        
        self.desc_text = QTextEdit()
        self.desc_text.setReadOnly(True)
        self.desc_text.setMaximumHeight(100)
        self.desc_text.setStyleSheet("background-color: transparent; border: none; color: #aaaaaa;")
        self.desc_text.setText("Datos del enlace: Distancia 15km, Altura Torre A 40m, Torre B 25m.\nPresione 'Calcular' para ver el presupuesto completo.")
        
        desc_layout.addWidget(self.desc_text)
        layout.addWidget(desc_group)

        # Sección Comentarios (Reemplazo: Historial)
        history_group = QGroupBox("Historial del Enlace")
        hist_layout = QVBoxLayout(history_group)
        
        hist_label = QLabel("• 12/10/2023: Cambio de antena 5GHz a 2ft\n• 01/09/2023: Instalación inicial")
        hist_label.setStyleSheet("color: #aaaaaa; padding: 5px;")
        hist_layout.addWidget(hist_label)
        
        layout.addWidget(history_group)
        
        return panel

    def create_io_modules(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Botón de reinicio estratégico
        reset_btn = QPushButton("🗑️ Limpiar / Reiniciar Casillas")
        reset_btn.setObjectName("ResetBtn")
        reset_btn.clicked.connect(self.reset_io)
        layout.addWidget(reset_btn)

        # --- MÓDULO 1: ENTRADAS (16 inputs) ---
        input_group = QGroupBox("Parámetros de Entrada")
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(5)
        
        self.inputs = []
        for i in range(16):
            lbl = QLabel(f"In {i+1}:")
            lbl.setStyleSheet("color: white; font-size: 10px;")
            line = QLineEdit()
            line.setObjectName("InputField")
            line.setPlaceholderText("Valor...")
            self.inputs.append(line)
            input_layout.addWidget(lbl, i//2, (i%2)*2)
            input_layout.addWidget(line, i//2, (i%2)*2 + 1)
            
        calc_btn = QPushButton("CALCULAR")
        calc_btn.setObjectName("CalcBtn")
        calc_btn.clicked.connect(self.calculate_link)
        input_layout.addWidget(calc_btn, 8, 0, 1, 4)
        
        layout.addWidget(input_group)

        # --- MÓDULO 2: SALIDAS (16 outputs) ---
        output_group = QGroupBox("Resultados y Presupuesto")
        output_layout = QGridLayout(output_group)
        output_layout.setSpacing(5)

        self.outputs = []
        for i in range(16):
            lbl = QLabel(f"Out {i+1}:")
            lbl.setStyleSheet("color: white; font-size: 10px;")
            line = QLineEdit()
            line.setObjectName("OutputField")
            line.setReadOnly(True)
            self.outputs.append(line)
            output_layout.addWidget(lbl, i//2, (i%2)*2)
            output_layout.addWidget(line, i//2, (i%2)*2 + 1)

        save_btn = QPushButton("GUARDAR DATOS")
        save_btn.setObjectName("SaveBtn")
        output_layout.addWidget(save_btn, 8, 0, 1, 4)
        
        layout.addWidget(output_group)
        
        return container

    @Slot()
    def calculate_link(self):
        # Simulación de cálculo
        for i, inp in enumerate(self.inputs):
            val = inp.text()
            if val:
                # Lógica dummy de transformación
                result = f"Calc: {float(val)*1.2:.2f}" if val.replace('.','',1).isdigit() else "Error: NaN"
                self.outputs[i].setText(result)
                self.outputs[i].setStyleSheet("color: #3ea6ff;") # Resaltar resultado
            else:
                self.outputs[i].setText("")
        
        # Actualizar descripción
        current_text = self.desc_text.toPlainText()
        self.desc_text.setText(current_text + "\n[CÁLCULO REALIZADO] Presupuesto estimado generado.")

    @Slot()
    def reset_io(self):
        for inp in self.inputs:
            inp.clear()
        for out in self.outputs:
            out.clear()
            out.setStyleSheet("color: #aaaaaa;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())