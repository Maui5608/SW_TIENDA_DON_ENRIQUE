import flet as ft
import pymysql
from datetime import datetime

# --- COLORES (UNIFICADOS) ---
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

def inventario_view(page: ft.Page, regresar_menu, usuario="Usuario"):
    page.bgcolor = COLOR_BG
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    id_proveedor = {"id": None}
    editando = {"id": None}

    estilo_input = {
        "border_color": "#334155",
        "focused_border_color": COLOR_ACCENT,
        "label_style": ft.TextStyle(color=COLOR_TEXT_DIM),
        "color": "white",
        "border_radius": 12,
        "bgcolor": "#0f172a",
        "content_padding": 15,
        "text_size": 14,
    }

    # -------- MENSAJES --------
    def msg(t, c=COLOR_ACCENT):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(t, weight="bold"),
            bgcolor=c
        )
        page.snack_bar.open = True
        page.update()

    # -------- DIALOGO (CORRECTO) --------
    def cerrar_dialogo():
        dlg.open = False
        page.update()

    dlg = ft.AlertDialog(
        bgcolor=COLOR_CARD,
        title=ft.Text("Seleccionar Proveedor", color="white"),
        content=ft.Text("Cargando..."),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo())
        ],
    )

    page.overlay.append(dlg)

    # -------- LÓGICA DE PROVEEDOR --------
    def seleccionar_proveedor(id_p, nombre_p):
        id_proveedor["id"] = id_p
        lbl_proveedor.value = f"✅ Proveedor: {nombre_p}"
        lbl_proveedor.color = COLOR_SUCCESS
        lbl_proveedor.italic = False
        dlg.open = False
        page.update()

    def buscar_proveedor(e):
        nombre = txt_buscar.value.strip()
        if not nombre:
            msg("Ingresa un nombre para buscar", COLOR_DANGER)
            return

        db = conectar()
        if not db:
            msg("Error de conexión", COLOR_DANGER)
            return

        cursor = db.cursor()
        cursor.execute(
            "SELECT id_proveedor, nombre, contacto FROM proveedores WHERE nombre LIKE %s",
            (f"%{nombre}%",)
        )
        datos = cursor.fetchall()
        db.close()

        if not datos:
            msg("No se encontró ningún proveedor", COLOR_DANGER)

        elif len(datos) == 1:
            seleccionar_proveedor(datos[0][0], datos[0][1])

        else:
            lista_items = []
            for d in datos:
                lista_items.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.PERSON, color=COLOR_ACCENT),
                        title=ft.Text(d[1], color="white"),
                        subtitle=ft.Text(f"ID: {d[0]} | Tel: {d[2]}", color=COLOR_TEXT_DIM),
                        on_click=lambda e, res=d: seleccionar_proveedor(res[0], res[1])
                    )
                )

            dlg.content = ft.Column(
                lista_items,
                scroll=ft.ScrollMode.AUTO,
                height=300,
                tight=True
            )
            dlg.open = True
            page.update()

    # -------- COMPONENTES --------
    txt_buscar = ft.TextField(
        label="Buscar proveedor",
        prefix_icon=ft.icons.SEARCH,
        on_submit=buscar_proveedor,
        expand=True,
        **estilo_input
    )

    lbl_proveedor = ft.Text(
        "Ningún proveedor seleccionado",
        color=COLOR_TEXT_DIM,
        italic=True
    )

    txt_nombre = ft.TextField(label="Nombre del Producto", **estilo_input)
    txt_desc = ft.TextField(label="Descripción", multiline=True, min_lines=2, **estilo_input)
    txt_precio = ft.TextField(label="Precio", prefix_text="$ ", **estilo_input)
    txt_stock = ft.TextField(label="Stock Actual", keyboard_type=ft.KeyboardType.NUMBER, **estilo_input)
    txt_min = ft.TextField(label="Stock Mínimo", keyboard_type=ft.KeyboardType.NUMBER, **estilo_input)

    txt_categoria = ft.Dropdown(
        label="Categoría",
        options=[
            ft.dropdown.Option("Hilos"), ft.dropdown.Option("Telas"),
            ft.dropdown.Option("Playeras"), ft.dropdown.Option("Gorras"),
            ft.dropdown.Option("Sudaderas"), ft.dropdown.Option("Pantalones"),
            ft.dropdown.Option("Bordados"), ft.dropdown.Option("Accesorios"),
            ft.dropdown.Option("Insumos"), ft.dropdown.Option("Otros"),
        ],
        value="Hilos",
        **estilo_input
    )

    txt_ubicacion = ft.TextField(label="Ubicación en Estante", **estilo_input)

    tabla = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def cargar():
        tabla.controls.clear()
        db = conectar()
        if not db:
            return

        cursor = db.cursor()
        cursor.execute("""
            SELECT i.id_producto, i.nombre, i.descripcion, i.precio_unitario,
                   i.stock_actual, i.stock_minimo, i.categoria,
                   i.ubicacion_estante, i.id_proveedor, p.nombre
            FROM inventario i
            JOIN proveedores p ON i.id_proveedor = p.id_proveedor
            ORDER BY i.id_producto DESC
        """)

        for d in cursor.fetchall():
            color_stock = COLOR_DANGER if d[4] <= d[5] else COLOR_SUCCESS
            tabla.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"#{d[0]}", color=COLOR_ACCENT, size=12),
                            ft.Text(d[1], weight="bold", color="white")
                        ], width=150),
                        ft.Text(f"${d[3]}", width=80, color="white"),
                        ft.Text(f"Stock: {d[4]}", color=color_stock, width=100, weight="bold"),
                        ft.Text(d[9], color=COLOR_TEXT_DIM, expand=True),
                        ft.IconButton(ft.icons.EDIT_NOTE, icon_color=COLOR_ACCENT,
                                      on_click=lambda e, x=d: editar(x)),
                        ft.IconButton(ft.icons.DELETE_FOREVER, icon_color=COLOR_DANGER,
                                      on_click=lambda e, x=d[0]: eliminar(x))
                    ]),
                    bgcolor="#162033", padding=15, border_radius=12
                )
            )
        db.close()
        page.update()

    def guardar(e):
        if not txt_nombre.value or not id_proveedor["id"] or not txt_precio.value:
            msg("Nombre, Precio y Proveedor son obligatorios", COLOR_DANGER)
            return

        db = conectar()
        cursor = db.cursor()

        try:
            if editando["id"]:
                sql = """UPDATE inventario SET nombre=%s, descripcion=%s, precio_unitario=%s,
                         stock_actual=%s, stock_minimo=%s, categoria=%s, ubicacion_estante=%s,
                         id_proveedor=%s, ultima_actualizacion=%s WHERE id_producto=%s"""
                valores = (
                    txt_nombre.value, txt_desc.value, float(txt_precio.value),
                    int(txt_stock.value or 0), int(txt_min.value or 0),
                    txt_categoria.value, txt_ubicacion.value,
                    id_proveedor["id"], datetime.now(), editando["id"]
                )
            else:
                sql = """INSERT INTO inventario
                         (nombre, descripcion, precio_unitario, stock_actual, stock_minimo,
                          categoria, ubicacion_estante, id_proveedor, ultima_actualizacion)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                valores = (
                    txt_nombre.value, txt_desc.value, float(txt_precio.value),
                    int(txt_stock.value or 0), int(txt_min.value or 0),
                    txt_categoria.value, txt_ubicacion.value,
                    id_proveedor["id"], datetime.now()
                )

            cursor.execute(sql, valores)
            db.commit()
            msg("¡Operación exitosa!", COLOR_SUCCESS)
            limpiar()
            cargar()

        except Exception as ex:
            msg(f"Error: {ex}", COLOR_DANGER)
        finally:
            db.close()

    def editar(d):
        editando["id"] = d[0]
        txt_nombre.value = d[1]
        txt_desc.value = d[2]
        txt_precio.value = str(d[3])
        txt_stock.value = str(d[4])
        txt_min.value = str(d[5])
        txt_categoria.value = d[6]
        txt_ubicacion.value = d[7]
        id_proveedor["id"] = d[8]
        lbl_proveedor.value = f"📝 Editando para: {d[9]}"
        lbl_proveedor.color = COLOR_ACCENT
        page.update()

    def eliminar(id_prod):
        db = conectar()
        cursor = db.cursor()
        cursor.execute("DELETE FROM inventario WHERE id_producto=%s", (id_prod,))
        db.commit()
        db.close()
        cargar()
        msg("Producto eliminado", "orange")

    def limpiar():
        txt_nombre.value = txt_desc.value = txt_precio.value = ""
        txt_stock.value = txt_min.value = txt_ubicacion.value = ""
        txt_categoria.value = "Hilos"
        lbl_proveedor.value = "Ningún proveedor seleccionado"
        lbl_proveedor.color = COLOR_TEXT_DIM
        id_proveedor["id"] = editando["id"] = None
        page.update()

    header = ft.Container(
        content=ft.Row([
            ft.IconButton(ft.icons.ARROW_BACK,
                          on_click=lambda _: regresar_menu(page),
                          icon_color="white"),
            ft.Icon(ft.icons.INVENTORY, color=COLOR_ACCENT, size=40),
            ft.Column([
                ft.Text("Gestión de Inventario", size=28, weight="bold", color="white"),
                ft.Text(f"Operador: {usuario}", color=COLOR_TEXT_DIM),
            ])
        ]),
        margin=ft.margin.only(bottom=20)
    )

    section_proveedor = ft.Container(
        content=ft.Column([
            ft.Text("1. Selección de Proveedor", color=COLOR_ACCENT, weight="bold"),
            ft.Row([
                txt_buscar,
                ft.IconButton(ft.icons.SEARCH, bgcolor=COLOR_ACCENT,
                              icon_color="white", on_click=buscar_proveedor)
            ]),
            lbl_proveedor
        ]),
        bgcolor=COLOR_CARD, padding=20, border_radius=15
    )

    section_form = ft.Container(
        content=ft.Column([
            ft.Text("2. Detalles del Producto", color=COLOR_ACCENT, weight="bold"),
            txt_nombre,
            txt_desc,
            ft.Row([txt_precio, txt_stock, txt_min]),
            ft.Row([txt_categoria, txt_ubicacion]),
            ft.Row([
                ft.ElevatedButton(
                    "GUARDAR PRODUCTO",
                    icon=ft.icons.SAVE,
                    style=ft.ButtonStyle(bgcolor=COLOR_ACCENT, color="white"),
                    on_click=guardar
                ),
                ft.TextButton("Limpiar Formulario", on_click=lambda _: limpiar())
            ], alignment="spaceBetween")
        ]),
        bgcolor=COLOR_CARD, padding=20, border_radius=15
    )

    cont_historial = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Productos en Existencia", weight="bold",
                        size=18, color="white"),
                ft.Icon(ft.icons.LIST_ALT, color=COLOR_TEXT_DIM)
            ], alignment="spaceBetween"),
            ft.Divider(color="white10"),
            ft.Container(tabla, height=350)
        ]),
        visible=False,
        bgcolor=COLOR_CARD, padding=20, border_radius=15
    )

    def toggle_historial(e):
        cont_historial.visible = not cont_historial.visible
        e.control.text = "Ocultar Lista" if cont_historial.visible else "Mostrar Inventario"
        e.control.icon = ft.icons.VISIBILITY_OFF if cont_historial.visible else ft.icons.HISTORY
        page.update()

    page.clean()
    page.add(
        ft.Column([
            header,
            section_proveedor,
            section_form,
            ft.ElevatedButton(
                "Mostrar Inventario",
                icon=ft.icons.HISTORY,
                on_click=toggle_historial,
                style=ft.ButtonStyle(color=COLOR_TEXT_DIM)
            ),
            cont_historial
        ], spacing=20)
    )

    cargar()