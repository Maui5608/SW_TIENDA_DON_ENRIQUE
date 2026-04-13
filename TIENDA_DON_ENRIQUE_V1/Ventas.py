import flet as ft
import pymysql
from datetime import datetime, timedelta

# --- Configuración de Colores ---
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
    except Exception as ex:
        print(f"Error de conexión: {ex}")
        return None

def ventas_view(page: ft.Page, regresar_menu, usuario="Usuario"):
    page.bgcolor = COLOR_BG
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    id_cliente = {"id": None}
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

    txt_buscar_cliente = ft.TextField(
        label="Nombre del Cliente", 
        expand=True, 
        prefix_icon=ft.icons.PERSON_SEARCH,
        on_submit=lambda e: buscar_cliente(e),
        **estilo_input
    )
    
    lbl_cliente = ft.Text("Ningún cliente seleccionado", color=COLOR_TEXT_DIM, italic=True)

 
    dlg = ft.AlertDialog(
        bgcolor=COLOR_CARD,
        title=ft.Text("Seleccionar Cliente", color="white"),
        content=ft.Text("Cargando..."),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda _: cerrar_dialogo())
        ],
    )
  
    page.overlay.append(dlg)


    def cerrar_dialogo():
        dlg.open = False
        page.update()

    def seleccionar_cliente(id_c, nom, ape):
        id_cliente["id"] = id_c
        lbl_cliente.value = f"✅ Cliente: {nom} {ape}"
        lbl_cliente.color = COLOR_SUCCESS
        lbl_cliente.italic = False
        dlg.open = False 
        page.update()

    def buscar_cliente(e):
        nombre = txt_buscar_cliente.value.strip()
        if not nombre:
            msg("Ingresa un nombre para buscar", COLOR_DANGER)
            return

        db = conectar()
        if not db: return
        cursor = db.cursor()
       
        query = "SELECT id_cliente, nombre, apellido FROM clientes WHERE nombre LIKE %s OR apellido LIKE %s"
        cursor.execute(query, (f"%{nombre}%", f"%{nombre}%"))
        datos = cursor.fetchall()
        db.close()

        if not datos:
            msg("No se encontró ningún cliente con ese nombre", COLOR_DANGER)
        elif len(datos) == 1:
        
            seleccionar_cliente(datos[0][0], datos[0][1], datos[0][2])
        else:
        
            lista_items = []
            for d in datos:
                lista_items.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.icons.PERSON, color=COLOR_ACCENT),
                        title=ft.Text(f"{d[1]} {d[2]}", color="white"),
                        subtitle=ft.Text(f"ID Sistema: {d[0]}", color=COLOR_TEXT_DIM),
                        on_click=lambda e, res=d: seleccionar_cliente(res[0], res[1], res[2])
                    )
                )
            
            dlg.content = ft.Column(lista_items, scroll=ft.ScrollMode.AUTO, height=300, tight=True)
            dlg.open = True
            page.update()

 
    txt_prenda = ft.TextField(label="Tipo de Prenda", expand=2, **estilo_input)
    txt_cantidad = ft.TextField(label="Cant.", expand=1, keyboard_type=ft.KeyboardType.NUMBER, **estilo_input)
    txt_diseno = ft.TextField(label="Descripción del Diseño", expand=3, **estilo_input)
    txt_fecha = ft.TextField(label="Fecha Entrega", expand=1, hint_text="AAAA-MM-DD", **estilo_input)
    
    txt_estado = ft.Dropdown(
        label="Estado del Pedido", expand=1, **estilo_input,
        options=[
            ft.dropdown.Option("Pendiente"),
            ft.dropdown.Option("En proceso"),
            ft.dropdown.Option("Terminado"),
            ft.dropdown.Option("Entregado"),
        ],
        value="Pendiente"
    )

    txt_costo = ft.TextField(label="Costo Total", expand=1, prefix_text="$ ", **estilo_input)
    txt_nota = ft.TextField(label="Notas adicionales", multiline=True, min_lines=2, **estilo_input)

    btn_guardar = ft.ElevatedButton(
        "GUARDAR PEDIDO", icon=ft.icons.SAVE_ROUNDED,
        style=ft.ButtonStyle(color="white", bgcolor=COLOR_ACCENT, shape=ft.RoundedRectangleBorder(radius=10), padding=20),
        on_click=lambda e: guardar(e)
    )

    tabla = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def msg(t, c=COLOR_ACCENT):
        page.snack_bar = ft.SnackBar(content=ft.Text(t, weight="bold"), bgcolor=c)
        page.snack_bar.open = True
        page.update()

    def cargar():
        tabla.controls.clear()
        db = conectar()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT v.id_pedido, c.nombre, v.tipo_prenda, v.cantidad, v.diseno, v.estado, v.costo, v.nota, c.apellido
                FROM venta v JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.id_pedido DESC
            """)
            filas = cursor.fetchall()
            for p in filas:
                status_color = COLOR_SUCCESS if p[5] == "Entregado" else "orange" if p[5] == "En proceso" else COLOR_TEXT_DIM
                tabla.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"#{p[0]}", color=COLOR_ACCENT, weight="bold", size=12),
                                ft.Text(f"{p[1]} {p[8]}", weight="bold", size=14, overflow=ft.TextOverflow.ELLIPSIS),
                            ], width=120),
                            ft.Column([
                                ft.Text(f"{p[3]}x {p[2]}", size=14),
                                ft.Text(str(p[4])[:30] + "..." if p[4] else "", size=12, color=COLOR_TEXT_DIM, italic=True),
                            ], expand=True),
                            ft.Container(
                                content=ft.Text(str(p[5]).upper(), size=10, weight="bold", color="white"),
                                bgcolor=status_color, padding=5, border_radius=5
                            ),
                            ft.Text(f"${p[6]}", width=70, text_align="right", weight="bold"),
                            ft.IconButton(ft.icons.EDIT_NOTE_ROUNDED, icon_color=COLOR_ACCENT, on_click=lambda e, val=p: editar(val)),
                            ft.IconButton(ft.icons.DELETE_FOREVER_ROUNDED, icon_color=COLOR_DANGER, on_click=lambda e, val=p[0]: eliminar(val)),
                        ]),
                        bgcolor="#162033", padding=15, border_radius=12,
                    )
                )
        except Exception as e: print(f"Error cargando datos: {e}")
        finally: db.close()
        page.update()

    def limpiar():
        txt_prenda.value = txt_cantidad.value = txt_diseno.value = txt_fecha.value = txt_costo.value = txt_nota.value = ""
        txt_buscar_cliente.value = ""
        lbl_cliente.value = "Ningún cliente seleccionado"
        lbl_cliente.color = COLOR_TEXT_DIM
        id_cliente["id"] = None
        editando["id"] = None
        btn_guardar.text = "GUARDAR PEDIDO"
        btn_guardar.bgcolor = COLOR_ACCENT
        page.update()

    def guardar(e):
        if not id_cliente["id"]:
            msg("Por favor, busca y selecciona un cliente primero", COLOR_DANGER)
            return
        
        db = conectar()
        if not db: return
        cursor = db.cursor()
        try:
            if editando["id"]:
                sql = "UPDATE venta SET tipo_prenda=%s, cantidad=%s, diseno=%s, fecha_entrega=%s, estado=%s, costo=%s, nota=%s WHERE id_pedido=%s"
                val = (txt_prenda.value, txt_cantidad.value, txt_diseno.value, txt_fecha.value, txt_estado.value, txt_costo.value, txt_nota.value, editando["id"])
            else:
                sql = "INSERT INTO venta (id_cliente, tipo_prenda, cantidad, diseno, fecha_entrega, estado, costo, nota) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                val = (id_cliente["id"], txt_prenda.value, txt_cantidad.value, txt_diseno.value, txt_fecha.value, txt_estado.value, txt_costo.value, txt_nota.value)
            
            cursor.execute(sql, val)
            db.commit()
            msg("¡Pedido guardado correctamente!", COLOR_SUCCESS)
            limpiar()
            cargar()
        except Exception as ex: msg(f"Error: {ex}", COLOR_DANGER)
        finally: db.close()

    def editar(p):
        editando["id"] = p[0]
     
        id_cliente["id"] = "desconocido_pero_fijo" 
        lbl_cliente.value = f"📝 Editando Pedido de: {p[1]}"
        lbl_cliente.color = COLOR_ACCENT
        txt_prenda.value = p[2]
        txt_cantidad.value = str(p[3])
        txt_diseno.value = p[4]
        txt_estado.value = p[5]
        txt_costo.value = str(p[6])
        txt_nota.value = p[7]
        btn_guardar.text = "ACTUALIZAR DATOS"
        btn_guardar.bgcolor = "purple"
        page.update()

    def eliminar(id_p):
        db = conectar()
        if not db: return
        cursor = db.cursor()
        cursor.execute("DELETE FROM venta WHERE id_pedido = %s", (id_p,))
        db.commit()
        db.close()
        cargar()
        msg("Pedido eliminado", "orange")

    def Boton_historial(e):
        cont_historial.visible = not cont_historial.visible
        e.control.text = "Ocultar Historial" if cont_historial.visible else "Ver Historial"
        page.update()


    header = ft.Container(
        content=ft.Row([
            ft.IconButton(ft.icons.ARROW_BACK_IOS_NEW_ROUNDED, on_click=lambda _: regresar_menu(page), icon_color="white"),
            ft.Icon(ft.icons.SHOPPING_CART_CHECKOUT_ROUNDED, color=COLOR_ACCENT, size=40),
            ft.Column([
                ft.Text("Módulo de Ventas", size=28, weight="bold", color="white"),
                ft.Text(f"Operador: {usuario}", color=COLOR_TEXT_DIM, size=14),
            ], expand=True),
        ]),
        margin=ft.margin.only(bottom=20)
    )

    section_cliente = ft.Container(
        content=ft.Column([
            ft.Text("1. Buscar Cliente", color=COLOR_ACCENT, weight="bold"),
            ft.Row([txt_buscar_cliente, ft.IconButton(ft.icons.SEARCH, bgcolor=COLOR_ACCENT, icon_color="white", on_click=buscar_cliente, height=50)]),
            lbl_cliente
        ]),
        bgcolor=COLOR_CARD, padding=20, border_radius=15,
    )

    section_form = ft.Container(
        content=ft.Column([
            ft.Text("2. Detalles del Pedido", color=COLOR_ACCENT, weight="bold"),
            ft.Row([txt_prenda, txt_cantidad]),
            txt_diseno,
            ft.Row([txt_fecha, txt_estado, txt_costo]),
            txt_nota,
            ft.Row([btn_guardar, ft.TextButton("Limpiar", on_click=lambda _: limpiar())], alignment="spaceBetween")
        ]),
        bgcolor=COLOR_CARD, padding=20, border_radius=15,
    )

    cont_historial = ft.Container(
        content=ft.Column([
            ft.Text("Historial de Pedidos", weight="bold", size=18),
            ft.Divider(color="white10"),
            ft.Container(content=tabla, height=400) 
        ]),
        visible=False, bgcolor=COLOR_CARD, padding=20, border_radius=15,
    )

    page.clean()
    page.add(
        ft.Column([
            header,
            section_cliente,
            section_form,
            ft.ElevatedButton("Ver Historial", icon=ft.icons.HISTORY, on_click=Boton_historial),
            cont_historial
        ], scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=20)
    )
    cargar()