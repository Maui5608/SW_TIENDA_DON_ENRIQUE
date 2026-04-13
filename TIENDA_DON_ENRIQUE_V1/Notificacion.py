import flet as ft
import pymysql
from Inventario import inventario_view
from Productos import productos_view

# --- COLORES ---
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
            database="tienda_don_enrique"
        )
    except:
        return None


# 🔢 CONTADOR GENERAL (INVENTARIO + PRODUCTOS)
def contar_notificaciones():
    db = conectar()
    if not db:
        return 0

    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM inventario WHERE stock_actual < stock_minimo) +
                (SELECT COUNT(*) FROM productos WHERE stock_actual <= stock_minimo)
        """)
        total = cursor.fetchone()[0]
        return total if total else 0
    except:
        return 0
    finally:
        db.close()


# 📦 INVENTARIO BAJO
def obtener_alertas_inventario():
    db = conectar()
    if not db:
        return []

    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT i.id_producto, i.nombre, i.stock_actual, i.stock_minimo, p.nombre
            FROM inventario i
            JOIN proveedores p ON i.id_proveedor = p.id_proveedor
            WHERE i.stock_actual < i.stock_minimo
            ORDER BY (i.stock_minimo - i.stock_actual) DESC
        """)
        return cursor.fetchall()
    except:
        return []
    finally:
        db.close()


# 🧾 PRODUCTOS BAJO
def obtener_alertas_productos():
    db = conectar()
    if not db:
        return []

    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT id_producto, nombre, stock_actual, stock_minimo, categoria
            FROM productos
            WHERE stock_actual <= stock_minimo
            ORDER BY (stock_minimo - stock_actual) DESC
        """)
        return cursor.fetchall()
    except:
        return []
    finally:
        db.close()


def notificacion_view(page: ft.Page, regresar_menu, usuario="Usuario"):
    page.bgcolor = COLOR_BG
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    lista = ft.Column(spacing=15)

    def cargar():
        lista.controls.clear()

        inv = obtener_alertas_inventario()
        prod = obtener_alertas_productos()

        if not inv and not prod:
            lista.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay alertas de stock.",
                        color=COLOR_SUCCESS,
                        weight="bold"
                    ),
                    padding=20,
                    bgcolor="#162033",
                    border_radius=12
                )
            )
            page.update()
            return

        # 🔴 INVENTARIO
        if inv:
            lista.controls.append(
                ft.Text("INVENTARIO", color=COLOR_ACCENT, weight="bold", size=18)
            )

            for d in inv:
                faltan = d[3] - d[2]
                lista.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(d[1], expand=True, color="white", weight="bold"),
                            ft.Text(f"{d[2]}/{d[3]}", color=COLOR_DANGER),
                            ft.Text(f"Faltan {faltan}", color=COLOR_DANGER),
                            ft.IconButton(
                                ft.Icons.ARROW_FORWARD_ROUNDED,
                                icon_color=COLOR_ACCENT,
                                tooltip="Abrir inventario",
                                on_click=lambda e: inventario_view(page, regresar_menu, usuario)
                            )
                        ]),
                        bgcolor="#162033",
                        padding=15,
                        border_radius=12
                    )
                )

        # 🔵 PRODUCTOS
        if prod:
            lista.controls.append(
                ft.Text("PRODUCTOS", color=COLOR_ACCENT, weight="bold", size=18)
            )

            for d in prod:
                faltan = d[3] - d[2]
                lista.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(d[1], expand=True, color="white", weight="bold"),
                            ft.Text(f"{d[2]}/{d[3]}", color=COLOR_DANGER),
                            ft.Text(f"Faltan {faltan}", color=COLOR_DANGER),
                            ft.IconButton(
                                ft.Icons.ARROW_FORWARD_ROUNDED,
                                icon_color=COLOR_ACCENT,
                                tooltip="Abrir productos",
                                on_click=lambda e: productos_view(page, regresar_menu)
                            )
                        ]),
                        bgcolor="#162033",
                        padding=15,
                        border_radius=12
                    )
                )

        page.update()

    # --- HEADER ---
    header = ft.Row([
        ft.IconButton(
            ft.Icons.ARROW_BACK,
            on_click=lambda _: regresar_menu(page),
            icon_color="white"
        ),
        ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color=COLOR_ACCENT, size=40),
        ft.Text("Notificaciones de Stock", size=28, weight="bold", color="white")
    ])

    page.clean()
    page.add(
        ft.Column([
            header,
            lista
        ], spacing=20)
    )

    cargar()