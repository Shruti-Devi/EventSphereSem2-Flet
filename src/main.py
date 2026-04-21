import os

import flet as ft
import httpx


PAGE_COLOR = "#CFD7E9"
CARD_COLOR = "#F8F6F6"
PRIMARY_COLOR = "#6D879D"
LINK_COLOR = "#3498DB"
LABEL_COLOR = "#576983"
INPUT_BORDER = "#DDDDDD"
BASE_URL = os.getenv("EVENTSPHERE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


async def main(page: ft.Page):
    page.title = "EventSphere"
    page.bgcolor = PAGE_COLOR
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    def show_blank_page():
        page.clean()
        page.add(ft.Container(expand=True))

    def show_login_page(e=None):
        email_input = ft.TextField(
            label="Email",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        password_input = ft.TextField(
            label="Password",
            width=320,
            password=True,
            can_reveal_password=True,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        status_text = ft.Text("", color=ft.Colors.RED_700, text_align=ft.TextAlign.CENTER)

        def login_click(e):
            if email_input.value == "" or password_input.value == "":
                status_text.value = "Enter your email and password."
            else:
                status_text.value = ""
                show_blank_page()
            page.update()

        login_card = ft.Container(
            width=380,
            bgcolor=CARD_COLOR,
            border_radius=12,
            padding=30,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Welcome Back!",
                        size=38,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_COLOR,
                        text_align=ft.TextAlign.CENTER,
                        font_family="Times New Roman",
                    ),
                    ft.Text(
                        "Sign in to your account to continue planning amazing events",
                        size=16,
                        color=ft.Colors.BLACK,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    email_input,
                    password_input,
                    ft.ElevatedButton(
                        "Login",
                        width=320,
                        height=48,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=login_click,
                    ),
                    status_text,
                    ft.TextButton(
                        "Forgot password?",
                        style=ft.ButtonStyle(color=LINK_COLOR),
                        on_click=show_forgot_page,
                    ),
                    ft.TextButton(
                        "Don't have an account? Register here.",
                        style=ft.ButtonStyle(color=LINK_COLOR),
                        on_click=show_register_page,
                    ),
                ],
            ),
        )

        page.clean()
        page.add(
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[login_card],
            )
        )
        page.update()

    def show_register_page(e=None):
        username = ft.TextField(
            label="Username",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        first_name = ft.TextField(
            label="First Name",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        last_name = ft.TextField(
            label="Last Name",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        email = ft.TextField(
            label="Email",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        password1 = ft.TextField(
            label="Password",
            width=320,
            password=True,
            can_reveal_password=True,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        password2 = ft.TextField(
            label="Confirm Password",
            width=320,
            password=True,
            can_reveal_password=True,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        dob = ft.TextField(
            label="Date of Birth",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        address = ft.TextField(
            label="Address",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        phone = ft.TextField(
            label="Phone Number",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        status_text = ft.Text("", color=ft.Colors.RED_700, text_align=ft.TextAlign.CENTER)

        async def register_click(e):
            if username.value == "":
                status_text.value = "Username is required."
                page.update()
                return

            if first_name.value == "" or last_name.value == "" or email.value == "":
                status_text.value = "First name, last name and email are required."
                page.update()
                return

            if password1.value == "" or password2.value == "":
                status_text.value = "Password and confirm password are required."
                page.update()
                return

            if dob.value == "" or address.value == "" or phone.value == "":
                status_text.value = "Date of birth, address and phone are required."
                page.update()
                return

            if password1.value != password2.value:
                status_text.value = "Passwords do not match."
                page.update()
                return

            status_text.value = "Registering..."
            page.update()

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{BASE_URL}/api/mobile-register/",
                        json={
                            "username": username.value,
                            "first_name": first_name.value,
                            "last_name": last_name.value,
                            "email": email.value,
                            "password1": password1.value,
                            "password2": password2.value,
                            "dob": dob.value,
                            "address": address.value,
                            "phone": phone.value,
                        },
                    )
                    data = response.json()

                    if response.status_code == 201:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(data.get("message", "Account created successfully."))
                        )
                        page.snack_bar.open = True
                        show_login_page()
                        return

                    status_text.value = data.get("message", "Register failed.")
                except Exception as ex:
                    status_text.value = f"Error: {ex}"

            page.update()

        register_card = ft.Container(
            width=380,
            bgcolor=CARD_COLOR,
            border_radius=12,
            padding=30,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Register",
                        size=38,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_COLOR,
                        text_align=ft.TextAlign.CENTER,
                        font_family="Times New Roman",
                    ),
                    ft.Text(
                        "Join Event Sphere to start planning your perfect events",
                        size=16,
                        color=ft.Colors.BLACK,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.TextButton(
                        "Back",
                        style=ft.ButtonStyle(color=LINK_COLOR),
                        on_click=show_login_page,
                    ),
                    username,
                    first_name,
                    last_name,
                    email,
                    password1,
                    password2,
                    dob,
                    address,
                    phone,
                    ft.Text(
                        "Profile Picture",
                        size=14,
                        color=LABEL_COLOR,
                        text_align=ft.TextAlign.LEFT,
                    ),
                    ft.Text(
                        "Kept out here to keep the Flet version simple.",
                        size=12,
                        color=ft.Colors.BLACK54,
                        text_align=ft.TextAlign.LEFT,
                    ),
                    ft.ElevatedButton(
                        "Register",
                        width=320,
                        height=48,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=register_click,
                    ),
                    status_text,
                    ft.TextButton(
                        "Already have an account? Login here.",
                        style=ft.ButtonStyle(color=LINK_COLOR),
                        on_click=show_login_page,
                    ),
                ],
            ),
        )

        page.clean()
        page.add(
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[register_card],
            )
        )
        page.update()

    def show_forgot_page(e=None):
        email_input = ft.TextField(
            label="Email",
            width=320,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )
        status_text = ft.Text("", color=ft.Colors.RED_700, text_align=ft.TextAlign.CENTER)

        async def forgot_click(e):
            if email_input.value == "":
                status_text.value = "Enter your email."
                page.update()
                return

            status_text.value = "Sending request..."
            page.update()

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{BASE_URL}/api/mobile-forgot-password/",
                        json={"email": email_input.value},
                    )
                    data = response.json()

                    if response.status_code == 200:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(data.get("message", "Reset request sent."))
                        )
                        page.snack_bar.open = True
                        show_login_page()
                        return

                    status_text.value = data.get("message", "Reset request failed.")
                except Exception as ex:
                    status_text.value = f"Error: {ex}"

            page.update()

        forgot_card = ft.Container(
            width=380,
            bgcolor=CARD_COLOR,
            border_radius=12,
            padding=30,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Forgot Password",
                        size=38,
                        weight=ft.FontWeight.BOLD,
                        color=PRIMARY_COLOR,
                        text_align=ft.TextAlign.CENTER,
                        font_family="Times New Roman",
                    ),
                    ft.Text(
                        "Enter your email address to reset your password",
                        size=16,
                        color=ft.Colors.BLACK,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.TextButton(
                        "Back",
                        style=ft.ButtonStyle(color=LINK_COLOR),
                        on_click=show_login_page,
                    ),
                    email_input,
                    ft.ElevatedButton(
                        "Send Reset Link",
                        width=320,
                        height=48,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=forgot_click,
                    ),
                    status_text,
                    ft.TextButton(
                        "Back to login",
                        style=ft.ButtonStyle(color=LINK_COLOR),
                        on_click=show_login_page,
                    ),
                ],
            ),
        )

        page.clean()
        page.add(
            ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[forgot_card],
            )
        )
        page.update()

    show_login_page()


ft.run(main)
