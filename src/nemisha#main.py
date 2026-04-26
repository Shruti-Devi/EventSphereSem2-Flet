import os

import flet as ft
import httpx
from datetime import date, datetime

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

    def session_set(key: str, value):
        s = page.session
        if hasattr(s, "set"):
            s.set(key, value)
        else:
            s[key] = value

    auth_token: str | None = None
    DARK_TEXT = ft.Colors.BLACK87
    MUTED_TEXT = ft.Colors.BLACK54

    def auth_headers() -> dict:
        if auth_token:
            return {"Authorization": f"Token {auth_token}"}
        return {}

    async def api_call(method: str, endpoint: str, payload: dict | None = None, use_auth: bool = False):
        url = f"{BASE_URL}{endpoint if endpoint.startswith('/') else '/' + endpoint}"
        headers = auth_headers() if use_auth else None
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.request(method, url, json=payload, headers=headers)
            except Exception as ex:
                return None, {"message": str(ex)}
        try:
            data = resp.json()
        except Exception:
            data = {"message": resp.text}
        return resp, data

    def _to_float(value, default=0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

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

        async def login_click(e):
            nonlocal auth_token
            if email_input.value == "" or password_input.value == "":
                status_text.value = "Enter your email and password."
            page.update()
            if status_text.value != "":
                return

            status_text.value = "Logging in..."
            page.update()

            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{BASE_URL}/api/mobile-login/",
                        json={
                            "email": email_input.value,
                            "password": password_input.value,
                        },
                    )
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    if response.status_code == 200 and data.get("success") is True:
                        status_text.value = ""
                        if isinstance(data, dict) and data.get("token"):
                            auth_token = data.get("token")
                            session_set("auth_token", data.get("token"))
                        setup_main_layout()
                        await show_packages_page()
                        return

                    status_text.value = data.get("message", "Login failed.")
                except Exception as ex:
                    status_text.value = f"Error: {ex}"

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
            read_only=True,
            bgcolor=ft.Colors.WHITE,
            border_color=INPUT_BORDER,
            focused_border_color=LINK_COLOR,
        )

        def dob_change(e):
            if dob_picker.value:
                v = dob_picker.value
                if isinstance(v, datetime):
                    v = v.date()
                dob.value = v.isoformat()
                page.update()

        dob_picker = ft.DatePicker(
            first_date=date(1900, 1, 1),
            last_date=date.today(),
            on_change=dob_change,
        )
        page.overlay.append(dob_picker)

        def open_dob_picker(e):
            dob_picker.open = True
            page.update()
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
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    if response.status_code == 201:
                        page.snack_bar = ft.SnackBar(
                            ft.Text(data.get("message", "Account created successfully."))
                        )
                        page.snack_bar.open = True
                        if isinstance(data, dict) and data.get("token"):
                            auth_token = data.get("token")
                            session_set("auth_token", data.get("token"))
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
                    ft.TextButton(
                        "Pick Date of Birth",
                        style=ft.ButtonStyle(color=LINK_COLOR),
                        on_click=open_dob_picker,
                    ),
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
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

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

    #upon login in

    content_container = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    def get_header():
        return ft.Container(
            bgcolor=CARD_COLOR,
            padding=ft.Padding.only(left=20, right=20, top=10, bottom=10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.EVENT_AVAILABLE, color=PRIMARY_COLOR, size=30),
                            ft.Text("Event Sphere", size=24, weight=ft.FontWeight.BOLD, color=DARK_TEXT),
                        ]
                    ),
                    ft.Button(
                        "Help?",
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=show_help_form,
                    ),
                ],
            ),
        )

    def get_footer():
        def contact_item(icon_name: str, text: str):
            return ft.Row(
                spacing=12,
                controls=[
                    ft.Image(src=f"{BASE_URL}/static/icons/{icon_name}", width=24, height=24),
                    ft.Text(text, size=16, color=DARK_TEXT),
                ],
            )

        def social_item(icon_name: str, label: str, url: str):
            return ft.Row(
                spacing=12,
                controls=[
                    ft.Image(src=f"{BASE_URL}/static/icons/{icon_name}", width=24, height=24),
                    ft.TextButton(label, url=url, style=ft.ButtonStyle(color=DARK_TEXT)),
                ],
            )

        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=ft.Padding.symmetric(horizontal=20, vertical=18),
            width=float("inf"),
            alignment=ft.Alignment.CENTER,
            content=ft.Container(
                width=1200,
                content=ft.Row(
                    wrap=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=10,
                            controls=[
                                ft.Text("Let's Chat:", size=22, weight=ft.FontWeight.BOLD, color=DARK_TEXT),
                                contact_item("phone.svg", "+230 58192674"),
                                contact_item("mail.svg", "Eventsphere@gmail.com"),
                                contact_item("location.svg", "Royal Road, Reduit"),
                            ],
                        ),
                        ft.Column(
                            spacing=10,
                            controls=[
                                ft.Text("Our Socials:", size=22, weight=ft.FontWeight.BOLD, color=DARK_TEXT),
                                social_item("instagram.png", "@eventsphere_creations", "https://www.instagram.com/"),
                                social_item("tik-tok.png", "@eventsphere", "https://www.tiktok.com/en/#"),
                                social_item("facebook.png", "@event_sphere_creations", "https://www.facebook.com/mauritius.visit/"),
                                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                                ft.Text("© 2026 Event Sphere", size=12, color=ft.Colors.BLACK45),
                            ],
                        ),
                    ],
                ),
            ),
        )

    def setup_main_layout():
        page.clean()
        page.add(
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    get_header(),
                    ft.Divider(height=1, color=ft.Colors.BLACK12),
                    content_container,
                    ft.Divider(height=1, color=ft.Colors.BLACK12),
                    get_footer(),
                ],
            )
        )

    def show_help_form(e=None):
        border_color = "#CCCCCC"
        contact_container_bg = "#F0EDED"

        name_field = ft.TextField(
            label="Full Name",
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border_color=border_color,
            focused_border_color=LINK_COLOR,
            label_style=ft.TextStyle(color=LABEL_COLOR, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=DARK_TEXT),
        )
        email_field = ft.TextField(
            label="Email Address",
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border_color=border_color,
            focused_border_color=LINK_COLOR,
            label_style=ft.TextStyle(color=LABEL_COLOR, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=DARK_TEXT),
        )
        phone_field = ft.TextField(
            label="Phone Number",
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border_color=border_color,
            focused_border_color=LINK_COLOR,
            label_style=ft.TextStyle(color=LABEL_COLOR, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=DARK_TEXT),
        )
        msg_field = ft.TextField(
            label="Message / Details",
            multiline=True,
            min_lines=4,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border_color=border_color,
            focused_border_color=LINK_COLOR,
            label_style=ft.TextStyle(color=LABEL_COLOR, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=DARK_TEXT),
        )
        how_heard = ft.Dropdown(
            label="How Did You Hear About Us?",
            value="Other",
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            border_color=border_color,
            focused_border_color=LINK_COLOR,
            label_style=ft.TextStyle(color=LABEL_COLOR, weight=ft.FontWeight.W_600),
            text_style=ft.TextStyle(color=DARK_TEXT),
            options=[
                ft.dropdown.Option("Social Media", "Social Media"),
                ft.dropdown.Option("Google Search", "Google Search"),
                ft.dropdown.Option("Referral", "Referral"),
                ft.dropdown.Option("Advertisement", "Advertisement"),
                ft.dropdown.Option("Other", "Other"),
            ],
        )
        status_msg = ft.Text("", color=ft.Colors.RED_700)

        async def submit_help(e):
            if (name_field.value or "").strip() == "" or (email_field.value or "").strip() == "" or (msg_field.value or "").strip() == "":
                status_msg.value = "Please fill in all required fields."
                page.update()
                return

            status_msg.value = "Sending..."
            page.update()

            response, data = await api_call(
                "POST",
                "/api/contact-submissions/",
                payload={
                    "full_name": (name_field.value or "").strip(),
                    "email": (email_field.value or "").strip(),
                    "phone_number": (phone_field.value or "").strip(),
                    "message": (msg_field.value or "").strip(),
                    "how_heard": how_heard.value or "Other",
                },
                use_auth=True,
            )
            if response is None:
                status_msg.value = data.get("message", "Network error.")
                page.update()
                return

            if response.status_code in (200, 201):
                page.snack_bar = ft.SnackBar(ft.Text("Thank you! Your message has been sent."))
                page.snack_bar.open = True
                await show_packages_page()
                return

            status_msg.value = f"Error {response.status_code}: {data}"
            page.update()

        contact_header = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(
                    src=f"{BASE_URL}/static/icons/contact-mail.png",
                    width=60,
                    height=60,
                ),
                ft.Text("Contact Us", size=34, weight=ft.FontWeight.BOLD, color=DARK_TEXT),
            ],
        )

        form_container = ft.Container(
            bgcolor=contact_container_bg,
            border_radius=12,
            padding=ft.Padding.all(32),
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Text(
                        "We respect your privacy. Your information will only be used to respond to your inquiry.",
                        size=12,
                        color=MUTED_TEXT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    name_field,
                    email_field,
                    phone_field,
                    msg_field,
                    how_heard,
                    status_msg,
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=ft.Button(
                            "Send Message",
                            bgcolor=PAGE_COLOR,
                            color=DARK_TEXT,
                            height=46,
                            width=220,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=submit_help,
                        ),
                    ),
                ],
            ),
        )

        content_container.controls = [
            ft.Container(
                padding=ft.Padding.symmetric(horizontal=20, vertical=30),
                content=ft.Column(
                    spacing=18,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        contact_header,
                        ft.Container(width=1200, content=form_container),
                        ft.TextButton("Back to Packages", on_click=show_packages_page),
                    ],
                ),
            )
        ]
        page.update()

    
    async def show_packages_page(e=None):
        text_overflow_ellipsis = getattr(getattr(ft, "TextOverflow", None), "ELLIPSIS", None)
        filter_border = "#EEE9E9"
        all_packages: list[dict] = []
        package_features: dict[int, list[str]] = {}
        details_dialog = ft.AlertDialog(modal=True)

        def open_details_dialog(pkg: dict):
            title = pkg.get("title") or pkg.get("name", "Package")
            price = _to_float(pkg.get("price"), 0)
            rating = pkg.get("rating", "N/A")
            review_count = pkg.get("review_count")
            description = pkg.get("description", "")
            feats = package_features.get(int(pkg.get("id") or 0), [])[:10]

            details_dialog.title = ft.Text(title, weight=ft.FontWeight.BOLD, color=DARK_TEXT)
            details_dialog.content = ft.Column(
                tight=True,
                controls=[
                    ft.Text(description, size=14, color=DARK_TEXT),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                f"⭐ {rating}" + (f" ({review_count})" if review_count is not None else ""),
                                color=ft.Colors.AMBER_700,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"Rs {price:,.2f}",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=PRIMARY_COLOR,
                            ),
                        ],
                    ),
                    ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                    ft.Text("Includes:", weight=ft.FontWeight.BOLD, color=DARK_TEXT),
                    ft.Column(
                        tight=True,
                        controls=[
                            ft.Text(f"• {f}", size=13, color=DARK_TEXT) for f in feats
                        ]
                        or [ft.Text("• Basic event setup", size=13, color=DARK_TEXT)],
                    ),
                ],
            )
            def _close_dialog(e=None):
                details_dialog.open = False
                page.update()

            details_dialog.actions = [ft.TextButton("Close", on_click=_close_dialog)]
            page.dialog = details_dialog
            details_dialog.open = True
            page.update()

        title_to_image = {
            "Premium Wedding Package": "premium_wedding.jpeg",
            "Intimate Wedding Package": "intimate_wedding.jpeg",
            "Social Event Package": "social_event.jpeg",
            "Graduation Celebration Package": "graduation.jpeg",
            "Birthday Celebration Package": "birthday.jpeg",
            "Corporate Excellence Package": "corporate.jpeg",
        }

        category_dd = ft.Dropdown(
            width=260,
            border_radius=20,
            content_padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            bgcolor=ft.Colors.WHITE,
            border_color=filter_border,
            focused_border_color=filter_border,
            label="Event type",
            value="all",
            label_style=ft.TextStyle(color=LABEL_COLOR),
            text_style=ft.TextStyle(color=DARK_TEXT),
            options=[
                ft.dropdown.Option("all", "All Events"),
                ft.dropdown.Option("wedding", "Wedding"),
                ft.dropdown.Option("birthday", "Birthday"),
                ft.dropdown.Option("corporate", "Corporate"),
                ft.dropdown.Option("graduation", "Graduation"),
                ft.dropdown.Option("social", "Social Event"),
            ],
        )

        price_dd = ft.Dropdown(
            width=260,
            border_radius=20,
            content_padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            bgcolor=ft.Colors.WHITE,
            border_color=filter_border,
            focused_border_color=filter_border,
            label="Price",
            value="all",
            label_style=ft.TextStyle(color=LABEL_COLOR),
            text_style=ft.TextStyle(color=DARK_TEXT),
            options=[
                ft.dropdown.Option("all", "All Prices"),
                ft.dropdown.Option("low", "Under Rs 100,000"),
                ft.dropdown.Option("medium", "Rs 100k – Rs 300k"),
                ft.dropdown.Option("high", "Over Rs 300,000"),
            ],
        )

        sort_dd = ft.Dropdown(
            width=260,
            border_radius=20,
            content_padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            bgcolor=ft.Colors.WHITE,
            border_color=filter_border,
            focused_border_color=filter_border,
            label="Sort",
            value="popular",
            label_style=ft.TextStyle(color=LABEL_COLOR),
            text_style=ft.TextStyle(color=DARK_TEXT),
            options=[
                ft.dropdown.Option("popular", "Most Popular"),
                ft.dropdown.Option("price_low", "Price: Low → High"),
                ft.dropdown.Option("price_high", "Price: High → Low"),
                ft.dropdown.Option("rating", "Highest Rating"),
            ],
        )

        result_count = ft.Text("", color=DARK_TEXT, size=12)

        packages_grid = ft.GridView(
            expand=True,
            max_extent=320,
            child_aspect_ratio=0.45,
            spacing=25,
            run_spacing=25,
        )

        def apply_filters():
            filtered = list(all_packages)

            category_value = category_dd.value or "all"
            if category_value != "all":
                filtered = [p for p in filtered if (p.get("category") or "").lower() == category_value]

            price_value = price_dd.value or "all"
            if price_value != "all":
                def _in_price(p: dict) -> bool:
                    v = _to_float(p.get("price"), 0)
                    if price_value == "low":
                        return v < 100000
                    if price_value == "medium":
                        return 100000 <= v <= 300000
                    return v > 300000

                filtered = [p for p in filtered if _in_price(p)]

            sort_value = sort_dd.value or "popular"
            if sort_value == "rating":
                filtered.sort(key=lambda p: _to_float(p.get("rating"), 0), reverse=True)
            elif sort_value == "price_low":
                filtered.sort(key=lambda p: _to_float(p.get("price"), 0))
            elif sort_value == "price_high":
                filtered.sort(key=lambda p: _to_float(p.get("price"), 0), reverse=True)
            else:
                filtered.sort(
                    key=lambda p: (
                        0 if p.get("is_popular") else 1,
                        -_to_float(p.get("rating"), 0),
                        _to_float(p.get("price"), 0),
                    )
                )

            result_count.value = f"Showing {len(filtered)} of {len(all_packages)} packages"

            packages_grid.controls.clear()
            if not filtered:
                packages_grid.controls.append(
                    ft.Container(
                        padding=20,
                        content=ft.Text("No packages available.", color=DARK_TEXT, size=14),
                    )
                )
                page.update()
                return

            for pkg in filtered:
                pkg_id = int(pkg.get("id") or 0)
                title = pkg.get("title") or pkg.get("name", "No title")
                description = pkg.get("description", "")
                price = _to_float(pkg.get("price"), 0)
                rating = pkg.get("rating", "N/A")
                review_count = pkg.get("review_count", 0)

                description_kwargs = {
                    "max_lines": 3,
                    "size": 13,
                    "color": DARK_TEXT,
                }
                if text_overflow_ellipsis is not None:
                    description_kwargs["overflow"] = text_overflow_ellipsis

                def open_details(e, p=pkg):
                    open_details_dialog(p)

                img_name = title_to_image.get(title)
                img = (
                    ft.Image(
                        src=f"{BASE_URL}/static/banner_and_images/{img_name}",
                        height=200,
                        width=float("inf"),
                        fit=ft.BoxFit.COVER,
                    )
                    if img_name
                    else ft.Container(
                        height=200,
                        bgcolor=ft.Colors.BLUE_GREY_50,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.IMAGE, size=60, color=ft.Colors.GREY_500),
                    )
                )

                feats = package_features.get(pkg_id, [])[:2]
                feat_text_kwargs = {"size": 12, "color": DARK_TEXT, "max_lines": 1}
                if text_overflow_ellipsis is not None:
                    feat_text_kwargs["overflow"] = text_overflow_ellipsis
                feats_controls = (
                    [ft.Text(f"• {f}", **feat_text_kwargs) for f in feats]
                    or [ft.Text("• Basic event setup", size=12, color=DARK_TEXT)]
                )

                badge = (
                    ft.Container(
                        top=12,
                        right=12,
                        bgcolor=PAGE_COLOR,
                        border_radius=20,
                        padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                        content=ft.Text("Most Popular", size=12, weight=ft.FontWeight.BOLD, color=DARK_TEXT),
                    )
                    if pkg.get("is_popular")
                    else None
                )

                card = ft.Container(
                    border=ft.Border.all(2, PRIMARY_COLOR),
                    border_radius=16,
                    bgcolor=ft.Colors.WHITE,
                    shadow=ft.BoxShadow(
                        blur_radius=12,
                        spread_radius=1,
                        color=ft.Colors.BLACK12,
                        offset=ft.Offset(0, 4),
                    ),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            img,
                            ft.Container(
                                padding=20,
                                content=ft.Column(
                                    expand=True,
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Column(
                                            spacing=10,
                                            controls=[
                                                ft.Text(
                                                    title,
                                                    size=18,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=DARK_TEXT,
                                                ),
                                                ft.Text(description, **description_kwargs),
                                                ft.Text(
                                                    f"⭐ {rating} ({review_count})",
                                                    size=12,
                                                    color=ft.Colors.AMBER_700,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                                ft.Text(
                                                    f"Rs {price:,.0f}",
                                                    size=20,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=PRIMARY_COLOR,
                                                ),
                                                ft.Text(
                                                    "Includes:",
                                                    size=12,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=DARK_TEXT,
                                                ),
                                                ft.Column(spacing=2, controls=feats_controls),
                                            ],
                                        ),
                                        ft.Button(
                                            "View details",
                                            bgcolor=PRIMARY_COLOR,
                                            color=ft.Colors.WHITE,
                                            height=44,
                                            width=float("inf"),
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(radius=12),
                                            ),
                                            on_click=open_details,
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                )

                packages_grid.controls.append(
                    ft.Stack(controls=[card] + ([badge] if badge else []))
                )

            page.update()

        def clear_filters(e=None):
            category_dd.value = "all"
            price_dd.value = "all"
            sort_dd.value = "popular"
            apply_filters()

        def _on_filter_change(e):
            apply_filters()

        category_dd.on_change = _on_filter_change
        price_dd.on_change = _on_filter_change
        sort_dd.on_change = _on_filter_change

        content_container.controls = [
            ft.Container(
                align=ft.Alignment.TOP_CENTER,
                width=1200,
                bgcolor=ft.Colors.WHITE,
                border_radius=16,
                padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Image(
                                    src=f"{BASE_URL}/static/icons/browse.svg",
                                    width=40,
                                    height=40,
                                ),
                                ft.Text(
                                    "Browse Event Packages",
                                    size=30,
                                    weight=ft.FontWeight.BOLD,
                                    color=DARK_TEXT,
                                ),
                            ]
                        ),
                        ft.Row(
                            wrap=True,
                            spacing=15,
                            controls=[category_dd, price_dd, sort_dd],
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                result_count,
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        ft.Button(
                                            "Apply filters",
                                            bgcolor=PRIMARY_COLOR,
                                            color=ft.Colors.WHITE,
                                            on_click=lambda _: apply_filters(),
                                        ),
                                        ft.TextButton(
                                            "Clear",
                                            style=ft.ButtonStyle(color=LINK_COLOR),
                                            on_click=clear_filters,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        packages_grid,
                    ],
                ),
            )
        ]

        packages_grid.controls = [ft.Container(padding=20, content=ft.ProgressRing())]
        page.update()

        try:
            pkg_res, packages_data = await api_call("GET", "/api/event-packages/", use_auth=True)
            feat_res, features_data = await api_call("GET", "/api/package-features/", use_auth=True)

            if pkg_res is None:
                packages_grid.controls = [
                    ft.Container(
                        padding=20,
                        content=ft.Text(
                            f"Error: {packages_data.get('message', 'Network error.')}",
                            color=ft.Colors.RED_700,
                        ),
                    )
                ]
                page.update()
                return

            if pkg_res.status_code != 200:
                packages_grid.controls = [
                    ft.Container(
                        padding=20,
                        content=ft.Text(
                            f"Failed to load packages (Status: {pkg_res.status_code})",
                            color=ft.Colors.RED_700,
                        ),
                    )
                ]
                page.update()
                return

                if isinstance(packages_data, list):
                    all_packages = packages_data
                elif isinstance(packages_data, dict):
                    all_packages = packages_data.get("results", [])
                else:
                    all_packages = []

            if feat_res is None or getattr(feat_res, "status_code", 0) != 200:
                features_data = []

                if isinstance(features_data, list):
                    for f in features_data:
                        pid = int(f.get("package") or 0)
                        if pid:
                            package_features.setdefault(pid, []).append(f.get("feature") or "")
                    for pid in list(package_features.keys()):
                        package_features[pid] = [x for x in package_features[pid] if x]

                apply_filters()
        except Exception as ex:
            packages_grid.controls = [
                ft.Container(padding=20, content=ft.Text(f"Error: {ex}", color=ft.Colors.RED_700))
            ]
            page.update()

    show_login_page()

ft.run(main)
