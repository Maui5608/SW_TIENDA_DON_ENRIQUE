import flet as ft
import pymysql


def conectar():
    try:
        return pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="tienda_don_enrique"
        )
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None


def productos_view(page: ft.Page, regresar_menu):
    id_actual = {"id": None}

    # --- ESTILOS ---
    estilo_tf = {
        "border_color": "white24",
        "color": "white",
        "focused_border_color": "cyan400",
        "border_radius": 10,
        "text_size": 14
    }

    # --- CAMPOS ---
    txt_nombre = ft.TextField(label="Nombre del Producto", width=250, **estilo_tf)
    txt_descripcion = ft.TextField(label="Descripción", width=400, multiline=True, **estilo_tf)
    txt_p_compra = ft.TextField(label="Precio Compra", width=150, prefix_text="$", **estilo_tf)
    txt_p_venta = ft.TextField(label="Precio Venta", width=150, prefix_text="$", **estilo_tf)
    txt_stock = ft.TextField(label="Stock Actual", width=120, keyboard_type=ft.KeyboardType.NUMBER, **estilo_tf)
    txt_stock_min = ft.TextField(label="Stock Mínimo", width=120, keyboard_type=ft.KeyboardType.NUMBER, **estilo_tf)

    ddl_categoria = ft.Dropdown(
        label="Categoría",
        width=220,
        border_radius=10,
        bgcolor="#0AFFFFFF",
        color="white",
        focused_border_color="cyan400",
        options=[
            ft.dropdown.Option("Polo"),
            ft.dropdown.Option("Polo cuello V"),
            ft.dropdown.Option("Polo cuello redondo"),
            ft.dropdown.Option("Camisa manga corta"),
            ft.dropdown.Option("Camisa manga larga"),
            ft.dropdown.Option("Playera"),
            ft.dropdown.Option("Sudadera"),
            ft.dropdown.Option("Pantalón"),
            ft.dropdown.Option("Short"),
            ft.dropdown.Option("Accesorios"),
        ],
    )

    txt_buscar = ft.TextField(
        label="Buscar producto...",
        expand=True,
        border_color="cyan900",
        prefix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: cargar_productos(e.control.value)
    )

    lista_productos = ft.ListView(expand=True, spacing=10, padding=10)

    # --- UTILIDADES ---
    def notificar(mensaje, color="blue"):
        page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def limpiar_formulario():
        txt_nombre.value = ""
        txt_descripcion.value = ""
        txt_p_compra.value = ""
        txt_p_venta.value = ""
        txt_stock.value = ""
        txt_stock_min.value = ""
        ddl_categoria.value = None
        id_actual["id"] = None
        btn_accion.text = "Registrar Producto"
        btn_accion.bgcolor = "blue700"
        page.update()

    # --- CRUD ---
    def guardar_producto(e):
        if not all([txt_nombre.value, txt_p_venta.value, txt_stock.value, ddl_categoria.value]):
            notificar("Nombre, Categoría, Precio Venta y Stock son obligatorios", "red700")
            return

        conn = conectar()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            datos = (
                txt_nombre.value,
                txt_descripcion.value,
                txt_p_compra.value,
                txt_p_venta.value,
                txt_stock.value,
                txt_stock_min.value,
                ddl_categoria.value
            )

            if id_actual["id"] is None:
                sql = """
                INSERT INTO productos 
                (nombre, descripcion, precio_compra, precio_venta, stock_actual, stock_minimo, categoria)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, datos)
                notificar("Producto registrado", "green700")
            else:
                sql = """
                UPDATE productos SET 
                nombre=%s, descripcion=%s, precio_compra=%s, precio_venta=%s,
                stock_actual=%s, stock_minimo=%s, categoria=%s
                WHERE id_producto=%s
                """
                cursor.execute(sql, datos + (id_actual["id"],))
                notificar("Producto actualizado", "cyan700")

            conn.commit()
            limpiar_formulario()
            cargar_productos()
        except Exception as ex:
            notificar(f"Error: {ex}", "red800")
        finally:
            conn.close()

    def preparar_edicion(p):
        id_actual["id"] = p[0]
        txt_nombre.value = p[1]
        txt_descripcion.value = p[2]
        txt_p_compra.value = str(p[3])
        txt_p_venta.value = str(p[4])
        txt_stock.value = str(p[5])
        txt_stock_min.value = str(p[6])
        ddl_categoria.value = p[8]
        btn_accion.text = "Actualizar Cambios"
        btn_accion.bgcolor = "orange800"
        historial_desplegable.initially_expanded = True
        page.update()

    def eliminar_producto(id_p):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id_p,))
        conn.commit()
        conn.close()
        notificar("Producto eliminado", "red")
        cargar_productos()

    def cargar_productos(filtro=""):
        lista_productos.controls.clear()
        conn = conectar()
        if not conn:
            return

        cursor = conn.cursor()
        query = "SELECT * FROM productos"
        if filtro:
            query += " WHERE nombre LIKE %s OR categoria LIKE %s"
            cursor.execute(query, (f"%{filtro}%", f"%{filtro}%"))
        else:
            query += " ORDER BY id_producto DESC"
            cursor.execute(query)

        for p in cursor.fetchall():
            color_stock = "red" if p[5] <= p[6] else "green"

            lista_productos.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_2, color="cyan"),
                        ft.Column([
                            ft.Text(p[1], weight="bold", size=15),
                            ft.Text(f"Cat: {p[8]} | ${p[4]}", size=12, color="cyan200"),
                            ft.Text(f"Stock: {p[5]} (Mín: {p[6]})", size=11, color=color_stock),
                        ], expand=True, spacing=2),
                        ft.IconButton(ft.Icons.EDIT, icon_color="yellow",
                                      on_click=lambda e, data=p: preparar_edicion(data)),
                        ft.IconButton(ft.Icons.DELETE, icon_color="red",
                                      on_click=lambda e, id=p[0]: eliminar_producto(id)),
                    ]),
                    bgcolor="#10FFFFFF",
                    padding=10,
                    border_radius=8
                )
            )

        conn.close()
        page.update()

    # --- UI ---
    btn_accion = ft.ElevatedButton(
        "Registrar Producto",
        on_click=guardar_producto,
        bgcolor="blue700",
        color="white"
    )

    historial_desplegable = ft.ExpansionTile(
        title=ft.Text("INVENTARIO DE PRODUCTOS", color="cyan", weight="bold"),
        subtitle=ft.Text("Consulta existencias y precios", size=12),
        controls=[
            ft.Container(
                content=lista_productos,
                height=400,
                padding=10,
                bgcolor="#05FFFFFF",
                border_radius=10
            )
        ]
    )

    layout = ft.Container(
        expand=True,
        gradient=ft.RadialGradient(
            center=ft.Alignment(0, -0.5),
            radius=1.5,
            colors=["#1a253a", "#05050a"]
        ),
        padding=25,
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK,
                              on_click=lambda _: regresar_menu(page),
                              icon_color="white"),
                ft.Text("Módulo de PRODUCTOS", size=26, weight="black"),
                ft.Icon(ft.Icons.CHECKROOM, color="cyan400", size=35),
            ], alignment="center"),

            ft.Container(
                content=ft.Column([
                    ft.Row([txt_nombre, ddl_categoria], alignment="center", wrap=True),
                    ft.Row([txt_descripcion], alignment="center"),
                    ft.Row([txt_p_compra, txt_p_venta, txt_stock, txt_stock_min],
                           alignment="center", wrap=True),
                    ft.Row([btn_accion,
                            ft.TextButton("Limpiar", on_click=lambda _: limpiar_formulario())],
                           alignment="center"),
                ], spacing=15),
                padding=20,
                bgcolor="#0AFFFFFF",
                border_radius=15,
                border=ft.border.all(1, "white10")
            ),

            ft.Row([
                txt_buscar,
                ft.FloatingActionButton(
                    icon=ft.Icons.SEARCH,
                    on_click=lambda _: cargar_productos(txt_buscar.value),
                    mini=True
                )
            ]),

            historial_desplegable
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    )

    page.clean()
    page.add(layout)
    cargar_productos()