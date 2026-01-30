import flet as ft
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import base64
import re
from io import BytesIO

# Configuración obligatoria para entornos sin monitor
matplotlib.use('Agg')

def main(page: ft.Page):
    page.title = "TopoGraph Pro v3.1"
    page.theme_mode = "dark"
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    # --- Lógica de Conversión DMS a Decimal ---
    def dms_a_decimal(coord_str):
        if not coord_str: return 0.0
        try:
            # Si el usuario ya metió un número decimal
            return float(coord_str)
        except ValueError:
            # Extraer números de la cadena tipo: 19° 25' 42" N
            partes = re.findall(r"[-+]?\d*\.\d+|\d+", coord_str)
            if len(partes) >= 1:
                g = float(partes[0])
                m = float(partes[1]) if len(partes) > 1 else 0
                s = float(partes[2]) if len(partes) > 2 else 0
                decimal = g + (m / 60) + (s / 3600)
                # Invertir signo para Sur u Oeste
                if any(c in coord_str.upper() for c in ['S', 'O', 'W']):
                    decimal *= -1
                return decimal
            return 0.0

    # --- Generador de Gráficos ---
    def generar_terreno(lat, lon):
        try:
            x = np.linspace(-5, 5, 50)
            y = np.linspace(-5, 5, 50)
            X, Y = np.meshgrid(x, y)
            # El terreno varía según las coordenadas ingresadas
            Z = np.sin(X + lat/5) * np.cos(Y + lon/5) * 4
            
            fig = plt.figure(figsize=(6, 4), facecolor='#121212')
            ax = fig.add_subplot(111, projection='3d')
            ax.set_facecolor('#121212')
            
            surf = ax.plot_surface(X, Y, Z, cmap='terrain', edgecolor='none')
            ax.set_axis_off()
            
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            plt.close(fig)
            return base64.b64encode(buf.getvalue()).decode("utf-8")
        except Exception as e:
            print(f"Error Matplotlib: {e}")
            return None

    # --- Componentes de Interfaz ---

    # SOLUCIÓN AL ERROR: Usamos un src genérico y NO pasamos src_base64 en el constructor
    img_display = ft.Image(
        src="https://via.placeholder.com/1x1/00000000/00000000.png", # Pixel transparente
        width=500,
        height=350,
        fit="contain",
        visible=False
    )

    txt_lat = ft.TextField(label="Latitud (DMS)", hint_text="19° 25' 42\" N", expand=True)
    txt_lon = ft.TextField(label="Longitud (DMS)", hint_text="99° 7' 39\" O", expand=True)

    history_log = ft.Column()
    history_container = ft.Container(
        content=ft.Column([
            ft.Text("HISTORIAL DE COORDENADAS", weight="bold", color="blue200"),
            history_log
        ]),
        visible=False,
        bgcolor="#1e1e1e",
        padding=15,
        border_radius=10,
        border=ft.Border(
            top=ft.BorderSide(1, "white10"), bottom=ft.BorderSide(1, "white10"),
            left=ft.BorderSide(1, "white10"), right=ft.BorderSide(1, "white10")
        )
    )

    # --- Acciones ---
    def procesar(e):
        lat_val = dms_a_decimal(txt_lat.value)
        lon_val = dms_a_decimal(txt_lon.value)
        
        b64 = generar_terreno(lat_val, lon_val)
        if b64:
            # Asignamos la propiedad después de la inicialización
            img_display.src_base64 = b64
            img_display.visible = True
            history_log.controls.insert(0, ft.Text(f"• Lat: {lat_val:.4f}, Lon: {lon_val:.4f}", size=12))
            page.update()

    def toggle_history(e):
        history_container.visible = not history_container.visible
        btn_toggle.text = "Ocultar Historial" if history_container.visible else "Ver Historial"
        page.update()

    btn_toggle = ft.TextButton("Ver Historial", icon="history", on_click=toggle_history)

    # --- Construcción de la Página ---
    page.add(
        ft.Text("TopoView v3.1 - DMS Processor", size=28, weight="bold"),
        ft.Container(
            content=img_display, 
            bgcolor="#0a0a0a", 
            border_radius=15, 
            padding=10,
            alignment=ft.Alignment(0, 0)
        ),
        ft.Row([txt_lat, txt_lon]),
        ft.ElevatedButton("Generar Terreno", icon="explore", on_click=procesar, width=300),
        ft.Divider(height=30),
        btn_toggle,
        history_container
    )

if __name__ == "__main__":
    ft.app(target=main)