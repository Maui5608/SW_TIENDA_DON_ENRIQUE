import flet as ft
from Cliente import clientes_view
from Ventas import ventas_view
from Proveedores import proveedores_view
from Inventario import inventario_view
from Pedidos import pedidos_view
from Productos import productos_view
from Notificacion import notificacion_view, contar_notificaciones


def menu_view(page: ft.Page, regresar_login, usuario="Usuario"):

    page.clean()
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#05050a"
    
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    def volver_al_menu(page):
        menu_view(page, regresar_login, usuario)

    def cambiar_modulo(e):
        opcion = e.control.data
        if opcion == "Clientes":
            clientes_view(page, volver_al_menu)
        elif opcion == "Ventas":
            ventas_view(page, volver_al_menu, usuario=usuario)
        elif opcion == "Proveedores": 
            proveedores_view(page, volver_al_menu)
        elif opcion == "Inventario": 
            inventario_view(page, volver_al_menu)
        elif opcion == "Pedidos":
            pedidos_view(page, volver_al_menu)
        elif opcion == "Productos":
            productos_view(page, volver_al_menu)
        page.update()

    def nav_item(texto, icono, color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=color, size=20), 
                ft.Text(texto, color="white", size=14, weight=ft.FontWeight.W_500)
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            border_radius=20,
            bgcolor="#1a1a2e",
            on_click=cambiar_modulo,
            data=texto,
            on_hover=lambda e: setattr(
                e.control, "bgcolor", "#2a2a40" if e.data == "true" else "#1a1a2e"
            ) or e.control.update()
        )


    cantidad_alertas = contar_notificaciones()
    badge_texto = "9+" if cantidad_alertas > 9 else str(cantidad_alertas)

    boton_notificaciones = ft.Container(
        width=44,
        height=44,
        content=ft.Stack([
            ft.IconButton(
                icon=ft.Icons.NOTIFICATIONS_OUTLINED, 
                icon_color="white70",
                tooltip="Notificaciones",
                on_click=lambda _: notificacion_view(page, volver_al_menu, usuario=usuario)
            ),
            ft.Container(
                content=ft.Text(
                    badge_texto,
                    size=10,
                    weight="bold",
                    color="white"
                ),
                width=18,
                height=18,
                bgcolor="red",
                border_radius=9,
                alignment=ft.alignment.center,
                left=24,
                top=2,
                visible=cantidad_alertas > 0
            )
        ])
    )

  
    barra_superior = ft.Container(
        content=ft.Row([
            # Lado Izquierdo
            ft.Row([
                ft.Icon(ft.Icons.PERSON_PIN_CIRCLE_ROUNDED, color="cyanaccent"),
                ft.Text(f"Bienvenido, {usuario}", color="white", size=16, weight="bold"),
            ], spacing=10),
            ft.Container(expand=True),
            boton_notificaciones,

            # Cerrar sesión (igual)
            ft.IconButton(
                icon=ft.Icons.LOGOUT_ROUNDED,
                icon_color="red400",
                tooltip="Cerrar sesión",
                on_click=lambda _: [page.controls.clear(), regresar_login(page)]
            )
        ]),
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
        bgcolor="#0f172a"
    )
    menu_horizontal = ft.Row(
        [
            nav_item("Clientes", ft.Icons.PEOPLE_ALT_ROUNDED, "cyan"),
            nav_item("Ventas", ft.Icons.SHOPPING_BAG_ROUNDED, "purpleaccent"),
            nav_item("Productos", ft.Icons.CHECKROOM_ROUNDED, "amber"), 
            nav_item("Pedidos", ft.Icons.LIST_ALT_ROUNDED, "pinkaccent"),
            nav_item("Inventario", ft.Icons.INVENTORY_2_ROUNDED, "orange"),
            nav_item("Proveedores", ft.Icons.LOCAL_SHIPPING_ROUNDED, "blue"),
            nav_item("Reportes", ft.Icons.ANALYTICS_ROUNDED, "greenaccent"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=12,
    )
    IMAGEN_BANNER = "https://i.pinimg.com/736x/10/03/b2/1003b29b605cc204932a9ab773f161b8.jpg"
    contenido_central = ft.Container(
        expand=True,
        alignment=ft.alignment.top_center,
        padding=ft.padding.symmetric(horizontal=40, vertical=20),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
            controls=[
                ft.Icon(
                    ft.Icons.DASHBOARD_ROUNDED,
                    size=70,
                    color="cyanaccent",
                    opacity=0.9
                ),
                ft.Text(
                    "SISTEMA DE GESTIÓN",
                    size=38,
                    weight=ft.FontWeight.BOLD,
                    color="white"
                ),
                ft.Text(
                    f"Hola y Bienvenido {usuario}",
                    color="white70",
                    size=18
                ),

            
                ft.Container(
                    width=float("inf"),
                    height=240,
                    border_radius=25,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    image=ft.DecorationImage(
                        src=IMAGEN_BANNER,
                        fit=ft.ImageFit.COVER
                    ),
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=["#00000000", "#000000AA"]
                    ),
                    shadow=ft.BoxShadow(
                        blur_radius=30,
                        color="#00000080",
                        offset=ft.Offset(0, 10)
                    )
                ),
            ]
        )
    )

    workspace = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#1a253a", "#05050a"],
        ),
        content=ft.Column([
            barra_superior,
            ft.Container(height=30),
            menu_horizontal,
            contenido_central
        ], spacing=0),
        padding=0
    )

    page.add(workspace)
    page.update()