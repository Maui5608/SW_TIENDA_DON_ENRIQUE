import flet as ft
import pymysql

# --- Mantenemos tu configuración de Colores ---
COLOR_BG = "#0f172a"
COLOR_CARD = "#1e293b"
COLOR_ACCENT = "#3b82f6"
COLOR_SUCCESS = "#10b981"
COLOR_DANGER = "#ef4444"
COLOR_TEXT_DIM = "#94a3b8"

def conectar():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="tienda_don_enrique",
            autocommit=True
        )
    except Exception as ex:
        print(f"Error de conexión: {ex}")
        return None

# --- Nueva Función de Actualización Rápida ---
def cambiar_estado_directo(id_p, nuevo_estado, page, callback):
    db = conectar()
    if not db: return
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE venta SET estado = %s WHERE id_pedido = %s", (nuevo_estado, id_p))
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Pedido #{id_p} actualizado a {nuevo_estado}"),
            bgcolor=COLOR_ACCENT
        )
        page.snack_bar.open = True
        callback() # Recarga la lista para mostrar cambios
    finally:
        db.close()

# Cambia el nombre aquí para que Menu.py lo encuentre
def pedidos_view(page: ft.Page, regresar_menu):
    page.bgcolor = COLOR_BG
    lista_monitor = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    # ... resto del código ...

    def cargar_datos():
        lista_monitor.controls.clear()
        db = conectar()
        if not db: return
        
        try:
            cursor = db.cursor()
            # Traemos la info necesaria incluyendo el nombre del cliente
            cursor.execute("""
                SELECT v.id_pedido, c.nombre, v.tipo_prenda, v.cantidad, v.estado, v.costo, c.apellido
                FROM venta v JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.id_pedido DESC
            """)
            
            for p in cursor.fetchall():
                lista_monitor.controls.append(
                    ft.Container(
                        padding=20,
                        bgcolor=COLOR_CARD,
                        border_radius=15,
                        content=ft.Row([
                            # Info Principal
                            ft.Column([
                                ft.Text(f"PEDIDO #{p[0]}", weight="bold", color=COLOR_ACCENT, size=12),
                                ft.Text(f"{p[1]} {p[6]}", size=18, weight="bold", color="white"),
                                ft.Text(f"{p[3]}x {p[2]}", color=COLOR_TEXT_DIM),
                            ], expand=True, spacing=2),
                            
                            # Costo
                            ft.Text(f"${p[5]}", size=20, weight="bold", color=COLOR_SUCCESS),
                            
                            ft.VerticalDivider(width=20, color="white10"),

                            # ÚNICA ACCIÓN: Selector de Estado
                            ft.Column([
                                ft.Text("ESTADO", size=10, color=COLOR_TEXT_DIM, weight="bold"),
                                ft.Dropdown(
                                    value=p[4],
                                    width=160,
                                    text_size=12,
                                    bgcolor=COLOR_BG,
                                    border_color="#334155",
                                    options=[
                                        ft.dropdown.Option("Pendiente"),
                                        ft.dropdown.Option("En proceso"),
                                        ft.dropdown.Option("Terminado"),
                                        ft.dropdown.Option("Entregado"),
                                    ],
                                    on_change=lambda e, id_p=p[0]: cambiar_estado_directo(
                                        id_p, e.control.value, page, cargar_datos
                                    )
                                ),
                            ], spacing=5)
                        ])
                    )
                )
        finally:
            db.close()
        page.update()

    # --- Estructura Visual Principal ---
    header = ft.Row([
        ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW, on_click=lambda _: regresar_menu(page), icon_color="white"),
        ft.Column([
            ft.Text("Monitor de Ventas", size=28, weight="bold", color="white"),
            ft.Text("Visualización de información y control de estados", color=COLOR_TEXT_DIM, size=14),
        ], expand=True),
        ft.Icon(ft.icons.MONITOR_HEART_ROUNDED, color=COLOR_ACCENT, size=30)
    ], alignment="spaceBetween")

    page.clean()
    page.add(
        ft.Container(
            expand=True,
            padding=20,
            content=ft.Column([
                header,
                ft.Divider(height=20, color="white10"),
                ft.Container(content=lista_monitor, expand=True)
            ])
        )
    )
    cargar_datos()