import flet as ft
import pymysql
from Menu import menu_view
import asyncio
import random 

animando = {"activo": False} 

def validar_usuario(usuario, password):
    try:
        conexion = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="",
            database="tienda_don_enrique",
            cursorclass=pymysql.cursors.DictCursor
        )

        

        cursor = conexion.cursor()

        cursor.execute(
            "SELECT nombre_usuario, password_hash FROM usuarios WHERE nombre_usuario = %s",
            (usuario,)
        )

        resultado = cursor.fetchone()
      

        conexion.close()

        if resultado and password == resultado["password_hash"]:
            return resultado

        return None

    except Exception as e:
        print("💥 ERROR REAL:", e)  # 👈 AQUÍ VERÁS EL ERROR EXACTO
        return None
    
animando = {"activo": False}

def main(page: ft.Page):

    page.controls.clear()
    page.window_width = 900
    page.window_height = 700
    page.window_resizable = False
    page.title = "Acceso - Tienda Don Enrique"

    # ---------------- CAMPOS ----------------
    txt_user = ft.TextField(
        hint_text="Usuario",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=14,
        bgcolor="#13263d",
        border_color=ft.Colors.TRANSPARENT,
        color=ft.Colors.WHITE,
    )

    txt_pass = ft.TextField(
        hint_text="Contraseña",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_radius=14,
        bgcolor="#13263d",
        border_color=ft.Colors.TRANSPARENT,
        color=ft.Colors.WHITE,
        on_submit=lambda e: login_click(e)
    )

    lbl_mensaje = ft.Text("", size=14)
    prg_load = ft.ProgressBar(width=300, visible=False)

    def login_click(e):
        if not txt_user.value or not txt_pass.value:
            lbl_mensaje.value = "⚠️ Completa todos los campos"
            lbl_mensaje.color = ft.Colors.ORANGE_400
            page.update()
            return

        user_data = validar_usuario(txt_user.value, txt_pass.value)

        if user_data and "nombre_usuario" in user_data:
            animando["activo"] = False  # 👈 DETIENE animación
            menu_view(page, main, usuario=user_data["nombre_usuario"])
        else:
            lbl_mensaje.value = "Usuario o contraseña incorrectos"
            lbl_mensaje.color = ft.Colors.RED_ACCENT
            page.update()

    btn_login = ft.Container(
        content=ft.Text(
            "INICIAR SESIÓN",
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLACK,
        ),
        width=320,
        height=55,
        alignment=ft.alignment.center,
        border_radius=30,
        gradient=ft.LinearGradient(
            colors=["#1efcff", "#00c9ff"],
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
        ),
        shadow=ft.BoxShadow(
            blur_radius=25,
            spread_radius=1,
            color="#00eaff66"
        ),
        on_click=login_click,
    )

    # ---------------- TARJETA LOGIN ----------------
    login_card = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.CHECKROOM_ROUNDED, size=80, color="#2efcff"),
                ft.Text("Don Enrique", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Sistema de Gestión", size=15, color=ft.Colors.WHITE70),
                ft.Container(height=10),
                txt_user,
                txt_pass,
                lbl_mensaje,
                prg_load,
                ft.Container(height=10),
                btn_login,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        ),
        padding=40,
        width=400,
        border_radius=30,
        gradient=ft.LinearGradient(
            colors=["#0f1e33", "#091423"],
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
        ),
        shadow=ft.BoxShadow(
            blur_radius=45,
            spread_radius=2,
            color=ft.Colors.BLACK54
        ),
    )

    # ---------------- FONDO ABSTRACTO AZUL ----------------
    def bloque(x=None, y=0, w=100, h=100, color="#fff", opacity=0.3, right=None):
        return ft.Container(
            left=x,
            right=right,
            top=y,
            width=w,
            height=h,
            bgcolor=color,
            opacity=opacity,
            border_radius=20,
            animate_position=ft.Animation(
                duration=4000,
                curve=ft.AnimationCurve.EASE_IN_OUT
            )

    )


    bloques_animados = []
    # IZQUIERDA
    b1 = bloque(20, 40, 140, 220, "#1b3a5c", 0.35)
    bloques_animados.append(b1)

    b2 = bloque(200, 60, 180, 120, "#1f4d7a", 0.30)
    bloques_animados.append(b2)

    b3 = bloque(80, 300, 220, 160, "#163d5c", 0.35)
    bloques_animados.append(b3)

    b8 = bloque(80, 200, 220, 160, "#4240AC", 0.30)
    bloques_animados.append(b8)

    # DERECHA
    b4 = bloque(right=20, y=50, w=160, h=200, color="#225387", opacity=0.30)
    bloques_animados.append(b4)

    b5 = bloque(right=60, y=300, w=200, h=150, color="#1f4d7a", opacity=0.25)
    bloques_animados.append(b5)

    b6 = bloque(right=30, y=500, w=180, h=130, color="#143654", opacity=0.35)
    bloques_animados.append(b6)

    b9 = bloque(right=30, y=400, w=180, h=130, color="#113555", opacity=0.35)
    bloques_animados.append(b9)

    # CENTRO
    b7 = bloque(250, 350, 140, 260, "#102e4a", 0.40)
    bloques_animados.append(b7)

    fondo = ft.Stack(
        [
            ft.Container(expand=True, bgcolor="#140730"),

            b1, b2, b3,
            b4, b5, b6,
            b7, b8, b9,
            
            bloque(60, 120, 12, 12, ft.Colors.WHITE, 0.6),
            bloque(right=100, y=200, w=10, h=10, color=ft.Colors.WHITE, opacity=0.5),
            bloque(right=50, y=450, w=8, h=8, color=ft.Colors.WHITE, opacity=0.5),
        ],
        expand=True,
    )

    async def animar_fondo():
        animando["activo"] = True

        while animando["activo"]:
            for b in bloques_animados:
                if b.left is not None:
                    b.left = random.randint(0, 600)
                if b.right is not None:
                    b.right = random.randint(0, 600)

                b.top = random.randint(0, 500)
                b.update()

            await asyncio.sleep(4)
  
    page.add(
    ft.Stack(
        [
            fondo,
            ft.Container(
                content=login_card,
                alignment=ft.alignment.center,
                expand=True,
            ),
        ],
        expand=True,
    )
)

# 🔥 Evita múltiples animaciones

    page.run_task(animar_fondo)

if __name__ == "__main__":
    ft.app(target=main)