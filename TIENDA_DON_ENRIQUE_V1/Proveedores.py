import flet as ft
import pymysql
import re

# --- CONFIGURACIÓN DE BASE DE DATOS ---
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

def proveedores_view(page: ft.Page, regresar_menu):
    id_actual = {"id": None}

    estilo_tf = {
        "border_color": "white24",
        "color": "white",
        "focused_border_color": "cyan400",
        "border_radius": 10,
        "text_size": 14
    }

    # --- CAMPOS DE TEXTO ---
    txt_nombre = ft.TextField(label="Nombre del Proveedor", width=250, **estilo_tf)
    txt_contacto = ft.TextField(label="Contacto / Teléfono", width=200, **estilo_tf)
    txt_fecha = ft.TextField(label="Fecha (AAAA-MM-DD)", width=200, value="2026-03-24", **estilo_tf)

    # --- GESTIÓN DE INSUMOS DINÁMICOS ---
    insumos_fields = []
    contenedor_insumos = ft.Column(spacing=10)

    def agregar_insumo(valor=""):
        tf = ft.TextField(label="Insumo", width=200, value=valor, **estilo_tf)
        def eliminar_fila(e):
            insumos_fields.remove(tf)
            contenedor_insumos.controls.remove(fila)
            page.update()
            
        fila = ft.Row([
            tf, 
            ft.IconButton(ft.Icons.REMOVE_CIRCLE, icon_color="red", on_click=eliminar_fila)
        ], alignment="center")
        
        insumos_fields.append(tf)
        contenedor_insumos.controls.append(fila)
        page.update()

    # --- LÓGICA DE NOTIFICACIÓN Y LIMPIEZA ---
    def notificar(m, c="blue"):
        page.snack_bar = ft.SnackBar(ft.Text(m), bgcolor=c)
        page.snack_bar.open = True
        page.update()

    def limpiar_formulario():
        txt_nombre.value = ""
        txt_contacto.value = ""
        txt_fecha.value = "2026-03-24"
        contenedor_insumos.controls.clear()
        insumos_fields.clear()
        agregar_insumo() # Dejar al menos uno vacío
        id_actual["id"] = None
        btn_accion.text = "Registrar Proveedor"
        btn_accion.bgcolor = "blue700"
        page.update()

    # --- OPERACIONES CRUD ---
    def guardar_proveedor(e):
        nombre = txt_nombre.value.strip()
        contacto = txt_contacto.value.strip()
        fecha = txt_fecha.value.strip()

        if not nombre or not any(tf.value.strip() for tf in insumos_fields):
            notificar("El nombre y al menos un insumo son obligatorios", "red700")
            return

        conn = conectar()
        if not conn: return
        cursor = conn.cursor()

        try:
            if id_actual["id"] is None:
                # INSERTAR NUEVO
                cursor.execute(
                    "INSERT INTO proveedores (nombre, fecha_venta, contacto) VALUES (%s,%s,%s)",
                    (nombre, fecha, contacto)
                )
                id_prov = cursor.lastrowid
            else:
                # ACTUALIZAR EXISTENTE
                id_prov = id_actual["id"]
                cursor.execute(
                    "UPDATE proveedores SET nombre=%s, fecha_venta=%s, contacto=%s WHERE id_proveedor=%s",
                    (nombre, fecha, contacto, id_prov)
                )
                cursor.execute("DELETE FROM proveedor_insumos WHERE id_proveedor=%s", (id_prov,))

            # Guardar insumos
            for tf in insumos_fields:
                val = tf.value.strip()
                if val:
                    cursor.execute(
                        "INSERT INTO proveedor_insumos (id_proveedor, insumo) VALUES (%s,%s)",
                        (id_prov, val)
                    )

            conn.commit()
            notificar("Datos guardados correctamente", "green700")
            limpiar_formulario()
            cargar_proveedores()
        except Exception as err:
            notificar(f"Error: {err}", "red")
        finally:
            conn.close()

    def eliminar_proveedor(idp):
        conn = conectar()
        if not conn: return
        cursor = conn.cursor()
        cursor.execute("DELETE FROM proveedores WHERE id_proveedor=%s", (idp,))
        conn.commit()
        conn.close()
        notificar("Proveedor eliminado", "red")
        cargar_proveedores()

    def preparar_edicion(p):
        id_actual["id"] = p[0]
        txt_nombre.value = p[1]
        txt_fecha.value = str(p[2])
        txt_contacto.value = p[3]

        contenedor_insumos.controls.clear()
        insumos_fields.clear()

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT insumo FROM proveedor_insumos WHERE id_proveedor=%s", (p[0],))
        for i in cursor.fetchall():
            agregar_insumo(i[0])
        conn.close()

        btn_accion.text = "Actualizar Cambios"
        btn_accion.bgcolor = "orange800"
        historial_desplegable.initially_expanded = True
        page.update()

    def cargar_proveedores(filtro=""):
        lista_proveedores.controls.clear()
        conn = conectar()
        if not conn: return
        cursor = conn.cursor()

        query = """
            SELECT p.id_proveedor, p.nombre, p.fecha_venta, p.contacto,
            (SELECT GROUP_CONCAT(insumo SEPARATOR ', ') FROM proveedor_insumos WHERE id_proveedor = p.id_proveedor) as insumos
            FROM proveedores p
        """
        
        if filtro:
            query += " WHERE p.nombre LIKE %s"
            cursor.execute(query, (f"%{filtro}%",))
        else:
            query += " ORDER BY p.id_proveedor DESC"
            cursor.execute(query)

        for p in cursor.fetchall():
            lista_proveedores.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCAL_SHIPPING, color="cyan"),
                        ft.Column([
                            ft.Text(p[1], weight="bold"),
                            ft.Text(f"📦 {p[4] if p[4] else 'Sin insumos'}", size=12, color="cyan200"),
                            ft.Text(f"📞 {p[3]} | 📅 {p[2]}", size=11, color="white60"),
                        ], expand=True, spacing=2),
                        ft.IconButton(ft.Icons.EDIT, icon_color="yellow", on_click=lambda e, d=p: preparar_edicion(d)),
                        ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, i=p[0]: eliminar_proveedor(i)),
                    ]),
                    bgcolor="#10FFFFFF", padding=10, border_radius=8
                )
            )
        conn.close()
        page.update()

    # --- ELEMENTOS DE LA INTERFAZ ---
    btn_accion = ft.ElevatedButton("Registrar Proveedor", on_click=guardar_proveedor, bgcolor="blue700", color="white")
    
    txt_buscar = ft.TextField(
        label="Buscar proveedor...", 
        expand=True, 
        border_color="cyan900", 
        prefix_icon=ft.Icons.SEARCH,
        on_submit=lambda e: cargar_proveedores(e.control.value)
    )

    lista_proveedores = ft.ListView(expand=True, spacing=10, padding=10)

    historial_desplegable = ft.ExpansionTile(
        title=ft.Text("VER HISTORIAL DE PROVEEDORES", color="cyan", weight="bold"),
        subtitle=ft.Text("Haz clic para expandir u ocultar la lista", size=12),
        controls=[
            ft.Container(
                content=lista_proveedores,
                height=400,
                padding=10,
                bgcolor="#05FFFFFF",
                border_radius=10,
                border=ft.border.all(1, "white10")
            )
        ]
    )

    # --- DISEÑO FINAL ---
    layout = ft.Container(
        expand=True,
        gradient=ft.RadialGradient(center=ft.Alignment(0, -0.5), radius=1.5, colors=["#1a253a", "#05050a"]),
        padding=25,
        content=ft.Column([
            # Cabecera con botón regresar
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: regresar_menu(page), icon_color="white"),
                ft.Text("Módulo de PROVEEDORES", size=26, weight="black"),
                ft.Icon(ft.Icons.LOCAL_SHIPPING_ROUNDED, color="cyan400", size=35),
            ], alignment="center"),

            # Formulario
            ft.Container(
                content=ft.Column([
                    ft.Row([txt_nombre, txt_contacto], alignment="center", wrap=True),
                    ft.Divider(height=1, color="white10"),
                    ft.Row([
                        ft.Text("Insumos Entregados", color="cyan", weight="bold"),
                        ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color="cyan", on_click=lambda _: agregar_insumo())
                    ], alignment="center"),
                    contenedor_insumos,
                    ft.Row([txt_fecha], alignment="center"),
                    ft.Row([btn_accion, ft.TextButton("Limpiar", on_click=lambda _: limpiar_formulario())], alignment="center"),
                ], spacing=15),
                padding=20, bgcolor="#0AFFFFFF", border_radius=15, border=ft.border.all(1, "white10")
            ),

            # Buscador
            ft.Row([
                txt_buscar,
                ft.FloatingActionButton(icon=ft.Icons.SEARCH, on_click=lambda _: cargar_proveedores(txt_buscar.value), mini=True)
            ]),

            # Historial
            historial_desplegable
            
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
    )

    page.clean()
    page.add(layout)
    agregar_insumo() # Inicializar con un campo de insumo
    cargar_proveedores()