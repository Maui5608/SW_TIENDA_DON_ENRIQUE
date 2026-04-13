import flet as ft
import pymysql
import re 

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

def clientes_view(page: ft.Page, regresar_menu):
    id_actual = {"id": None}

    estilo_tf = {
        "border_color": "white24", 
        "color": "white", 
        "focused_border_color": "cyan400",
        "border_radius": 10,
        "text_size": 14
    }


    txt_nombre = ft.TextField(label="Nombre", width=200, **estilo_tf)
    txt_apellido = ft.TextField(label="Apellido", width=200, **estilo_tf)
    txt_contacto = ft.TextField(
        label="Teléfono", 
        width=200, 
        keyboard_type=ft.KeyboardType.NUMBER, 
        max_length=15,
        **estilo_tf
    )
    txt_correo = ft.TextField(label="Correo Electrónico", width=250, **estilo_tf)
    
    txt_buscar = ft.TextField(
        label="Buscar cliente...", 
        expand=True, 
        border_color="cyan900", 
        prefix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: cargar_clientes(e.control.value)
    )

    lista_clientes = ft.ListView(
        expand=True, 
        spacing=10, 
        padding=10,
        auto_scroll=False 
    )

    def notificar(mensaje, color="blue"):
        page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def limpiar_formulario():
        txt_nombre.value = ""
        txt_apellido.value = ""
        txt_contacto.value = ""
        txt_correo.value = "" 
        id_actual["id"] = None
        btn_accion.text = "Registrar Cliente"
        btn_accion.bgcolor = "blue700"
        page.update()

    def guardar_cliente(e):
  
        nombre = txt_nombre.value.strip()
        apellido = txt_apellido.value.strip()
        telefono = txt_contacto.value.strip()
        correo = txt_correo.value.strip()


        if not all([nombre, apellido, telefono, correo]):
            notificar("Todos los campos son obligatorios", "red700")
            return

     
        re_texto = r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{2,30}$"
        if not re.match(re_texto, nombre):
            notificar("Nombre inválido (solo letras, min. 2)", "red700")
            return
        if not re.match(re_texto, apellido):
            notificar("Apellido inválido (solo letras, min. 2)", "red700")
            return

      
        if not telefono.isdigit() or not (8 <= len(telefono) <= 15):
            notificar("Teléfono debe tener entre 8 y 15 dígitos", "red700")
            return

   
        re_correo = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(re_correo, correo):
            notificar("Formato de correo no válido", "red700")
            return

      
        conn = conectar()
        if not conn: 
            notificar("Error de base de datos", "red")
            return
            
        cursor = conn.cursor()
        try:
            if id_actual["id"] is None:
                
                cursor.execute(
                    "INSERT INTO clientes (nombre, apellido, contacto, correo) VALUES (%s, %s, %s, %s)", 
                    (nombre, apellido, telefono, correo)
                )
                notificar("Cliente guardado exitosamente", "green700")
            else:
                
                cursor.execute(
                    "UPDATE clientes SET nombre=%s, apellido=%s, contacto=%s, correo=%s WHERE id_cliente=%s", 
                    (nombre, apellido, telefono, correo, id_actual["id"])
                )
                notificar("Cliente actualizado", "cyan700")
            
            conn.commit()
            limpiar_formulario()
            cargar_clientes()
        except pymysql.Error as err:
            notificar(f"Error: {err}", "red800")
        finally:
            conn.close()

    def eliminar_cliente(id_cliente):
        conn = conectar()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id_cliente=%s", (id_cliente,))
        conn.commit()
        conn.close()
        notificar("Cliente eliminado", "red")
        cargar_clientes()

    def preparar_edicion(cliente):
        id_actual["id"] = cliente[0]
        txt_nombre.value = cliente[1]
        txt_apellido.value = cliente[2]
        txt_contacto.value = str(cliente[3])
        txt_correo.value = cliente[4] 
        btn_accion.text = "Actualizar Cambios"
        btn_accion.bgcolor = "orange800"
        historial_desplegable.initially_expanded = True 
        page.update()

    def cargar_clientes(filtro=""):
        lista_clientes.controls.clear()
        conn = conectar()
        if not conn: return
        cursor = conn.cursor()
        
        query = "SELECT id_cliente, nombre, apellido, contacto, correo FROM clientes"
        if filtro:
            query += " WHERE nombre LIKE %s OR apellido LIKE %s OR correo LIKE %s"
            cursor.execute(query, (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%"))
        else:
            query += " ORDER BY id_cliente DESC"
            cursor.execute(query)

        for c in cursor.fetchall():
            lista_clientes.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON_PIN, color="cyan"),
                        ft.Column([
                            ft.Text(f"{c[1]} {c[2]}", weight="bold"),
                            ft.Text(f"📧 {c[4]}", size=12, color="cyan200"),
                            ft.Text(f"📞 {c[3]}", size=11, color="white60"),
                        ], expand=True, spacing=2),
                        ft.IconButton(ft.Icons.EDIT, icon_color="yellow", on_click=lambda e, data=c: preparar_edicion(data)),
                        ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, id=c[0]: eliminar_cliente(id)),
                    ]),
                    bgcolor="#10FFFFFF", padding=10, border_radius=8
                )
            )
        conn.close()
        page.update()

    btn_accion = ft.ElevatedButton("Registrar Cliente", on_click=guardar_cliente, bgcolor="blue700", color="white")

    historial_desplegable = ft.ExpansionTile(
        title=ft.Text("VER HISTORIAL DE CLIENTES", color="cyan", weight="bold"),
        subtitle=ft.Text("Haz clic para expandir u ocultar la lista", size=12),
        controls=[
            ft.Container(
                content=lista_clientes,
                height=400,
                padding=10,
                bgcolor="#05FFFFFF",
                border_radius=10,
                border=ft.border.all(1, "white10")
            )
        ]
    )

    layout = ft.Container(
        expand=True,
        gradient=ft.RadialGradient(center=ft.Alignment(0, -0.5), radius=1.5, colors=["#1a253a", "#05050a"]),
        padding=25,
        content=ft.Column([
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: regresar_menu(page), icon_color="white"),
                ft.Text("Módulo de CLIENTES", size=26, weight="black"),
                ft.Icon(ft.Icons.PERSON_PIN_ROUNDED, color="cyan400", size=35),
            ], alignment="center"),

            ft.Container(
                content=ft.Column([
                    ft.Row([txt_nombre, txt_apellido], alignment="center", wrap=True),
                    ft.Row([txt_contacto, txt_correo], alignment="center", wrap=True),
                    ft.Row([btn_accion, ft.TextButton("Limpiar", on_click=lambda _: limpiar_formulario())], alignment="center"),
                ], spacing=15),
                padding=20, bgcolor="#0AFFFFFF", border_radius=15, border=ft.border.all(1, "white10")
            ),

            ft.Row([
                txt_buscar,
                ft.FloatingActionButton(icon=ft.Icons.SEARCH, on_click=lambda _: cargar_clientes(txt_buscar.value), mini=True)
            ]),

            historial_desplegable
            
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    )

    page.clean()
    page.add(layout)
    cargar_clientes()