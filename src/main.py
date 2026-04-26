import os
import math
import flet as ft
import flet_map as ftm
import httpx
import requests
from requests.exceptions import RequestException
from datetime import date, datetime
import asyncio

try:
    import flet_geolocator as ftg
except Exception:
    ftg = None

PAGE_COLOR = "#CFD7E9"
CARD_COLOR = "#F8F6F6"
PRIMARY_COLOR = "#6D879D"
LINK_COLOR = "#3498DB"
LABEL_COLOR = "#576983"
INPUT_BORDER = "#DDDDDD"
BASE_URL = os.getenv("EVENTSPHERE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
SHOW_MAP_IN_DETAILS = False


def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


async def show_reviews_page(page: ft.Page, package_id: int, on_back=None):
    """Fetch and display reviews. on_back should be your show_details_page function."""
    
    
    container = page.data.get("main_container")
    if not container:
        print("Container not found!")
        return
    
    # Show loading state
    container.controls.clear()
    container.controls.append(
        ft.Container(
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text("Loading reviews...", size=16, color=PRIMARY_COLOR)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True
        )
    )
    page.update()
    
    try:
        
        headers = {"Content-Type": "application/json"}
        token = page.data.get("token")
        if token:
            headers["Authorization"] = f"Token {token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://127.0.0.1:8000/api/testimonials/by-package/{package_id}/",
                headers=headers,
                timeout=5.0,
            )
        
        if response.status_code != 200:
            container.controls.clear()
            container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                        ft.Text(f"Error {response.status_code}: Failed to load reviews", size=18, color=ft.Colors.RED_700),
                        ft.Button("Go Back", on_click=lambda _: on_back(package_id) if on_back else None)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True
                )
            )
            page.update()
            return
        
        reviews = response.json()

        
        reviews_content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            controls=[
                ft.Container(
                    content=ft.Image(src=f"{BASE_URL}/static/banner_and_images/reviews_banner.jpg", width=float("inf"), height=200, fit="cover"),
                    bgcolor=ft.Colors.GREY_200,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_size=28,
                                on_click=lambda _: on_back(package_id) if on_back else None,
                                tooltip="Back to package details"
                            ),
                            ft.Text("Reviews", size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR, expand=True),
                        ]),
                        ft.Divider(height=20),
                        # ... [rest of your review cards/empty state code stays exactly the same] ...
                        *([
                            ft.Card(
                                elevation=3,
                                content=ft.Container(
                                    padding=20,
                                    margin=ft.Margin.only(bottom=15),
                                    content=ft.Row([
                                        ft.CircleAvatar(
                                            foreground_image_src=r.get("reviewer_photo") if r.get("reviewer_photo") else None,
                                            content=ft.Icon(ft.Icons.PERSON, size=30, color=ft.Colors.WHITE) if not r.get("reviewer_photo") else None,
                                            bgcolor=ft.Colors.GREY_300 if not r.get("reviewer_photo") else None,
                                            radius=35,
                                        ),
                                        ft.Column([
                                            ft.Text(r.get("reviewer_name", "Anonymous"), weight=ft.FontWeight.BOLD, size=18),
                                            ft.Row([ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=20) for _ in range(int(float(r.get("rating", 0))))], spacing=2),
                                            ft.Text(r.get("review_text", ""), size=15, italic=True, color=ft.Colors.GREY_800),
                                            ft.Text(f"Date: {r.get('date', 'Unknown')}", size=12, color=ft.Colors.GREY_600)
                                        ], spacing=8, expand=True)
                                    ], spacing=15)
                                ),
                            )
                            for r in reviews
                        ] if reviews else [
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.INFO_OUTLINE, size=80, color=ft.Colors.GREY_400),
                                    ft.Text("No reviews yet!", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                                    ft.Text("Be the first to share your experience.", size=16, color=ft.Colors.GREY_500)
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                                padding=ft.Padding.all(60)
                            )
                        ]),
                        ft.Container(height=30)
                    ], spacing=15),
                    padding=ft.Padding.all(25),
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.Margin.only(top=-30)
                )
            ]
        )
        
        container.controls.clear()
        container.controls.append(reviews_content)
        page.update()

        
    except httpx.RequestError as e:
        print(f"Network Error: {e}")
        container.controls.clear()
        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                    ft.Text(f"Network Error: {e}", size=18, color=ft.Colors.RED_700),
                    ft.Button("Go Back", on_click=lambda _: on_back(package_id) if on_back else None)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True
            )
        )
        page.update()
    except Exception as e:
        print(f"Unexpected Error: {e}")
        container.controls.clear()
        container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                    ft.Text(f"Error: {e}", size=18, color=ft.Colors.RED_700),
                    ft.Button("Go Back", on_click=lambda _: on_back(package_id) if on_back else None)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True
            )
        )
        page.update()

async def main(page: ft.Page):
    if not hasattr(page, "data") or page.data is None:
        page.data = {}

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

        async def login_click(e):
            status_text.value = ""
            if email_input.value == "" or password_input.value == "":
                status_text.value = "Enter your email and password."
                page.update()
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
                    data = response.json()

                    # if response.status_code == 200 and data.get("success") is True:
                    #     status_text.value = ""
                    #     await show_main_ui()
                    #     return
                    if response.status_code == 200 and data.get("success") is True:
                        print("Login response:", data)  # Debug: See what's returned
                        page.data["token"] = data.get("token")
                        print("Stored token:", page.data.get("token"))  # Debug: Verify storage
                        status_text.value = ""
                        await show_main_ui()
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
                    ft.TextButton(
                        "Pick Date of Birth",
                        style=ft.ButtonStyle(color=LINK_COLOR),
                        on_click=open_dob_picker,
                    ),
                    address,
                    phone,
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

    # --- MAIN UI ---
    async def show_main_ui():
        page.clean()
        page.padding = 0
        page.bgcolor = "#F0F2F5"
        main_container = ft.Column(expand=True, spacing=0)
        page.data["main_container"] = main_container
        page.add(build_header(), ft.Container(content=main_container, expand=True), build_footer())
        await show_packages_page()

    def build_header():
        return ft.Container(
            content=ft.Row([
                ft.Row([ft.Image(src=f"{BASE_URL}/static/icons/eventsphere_logo.png", width=30, height=30), ft.Text("Event Sphere", size=20, weight="bold", color="white")]),
                ft.TextButton("Logout", style=ft.ButtonStyle(color="white"), on_click=lambda _: show_login_page())
            ], alignment="spaceBetween"),
            bgcolor=PRIMARY_COLOR, padding=ft.padding.symmetric(horizontal=20, vertical=10)
        )

    def build_footer():
        return ft.Container(content=ft.Text("© 2026 Event Sphere - Royal Road, Reduit", color="white70", text_align="center", size=12), bgcolor="#2C3E50", padding=15, width=float("inf"))

    async def show_packages_page(e=None):
        container = page.data.get("main_container")
        if not container: return
        container.controls.clear()

        cat_drop = ft.Dropdown(
            label="Category", value="all", width=150, 
            options=[
                ft.dropdown.Option("all", "All Events"), ft.dropdown.Option("wedding", "Wedding"), 
                ft.dropdown.Option("birthday", "Birthday"), ft.dropdown.Option("corporate", "Corporate"), 
                ft.dropdown.Option("graduation", "Graduation"), ft.dropdown.Option("social", "Social Event")
            ]
        )
        prc_drop = ft.Dropdown(
            label="Price Range", value="all", width=150, 
            options=[ft.dropdown.Option("all", "All Prices"), ft.dropdown.Option("low", "Under Rs 100k"), ft.dropdown.Option("high", "Over Rs 100k")]
        )
        srt_drop = ft.Dropdown(
            label="Sort By", value="popular", width=150, 
            options=[
                ft.dropdown.Option("popular", "Most Popular"), ft.dropdown.Option("price_low", "Price: Low -> High"), 
                ft.dropdown.Option("price_high", "Price: High -> Low"), ft.dropdown.Option("rating", "Highest Rating")
            ]
        )
        search_f = ft.TextField(label="Search packages by name...", expand=True, prefix_icon=ft.Icons.SEARCH)
        
        package_grid = ft.GridView(expand=True, runs_count=3, max_extent=450, child_aspect_ratio=0.6, spacing=25, run_spacing=25, padding=30)
        count_text = ft.Text("Loading packages...", weight="bold", color=ft.Colors.GREY_700)
        all_pkgs = []

        async def update_grid(e=None):
            package_grid.controls.clear()
            search_t = search_f.value.lower() if search_f.value else ""
            filtered = []
            for p in all_pkgs:
                if search_t and search_t not in p.get("title", "").lower(): continue
                if cat_drop.value != "all" and p.get("category", "").lower() != cat_drop.value.lower(): continue
                val = float(p.get("price", 0))
                if prc_drop.value == "low" and val > 100000: continue
                if prc_drop.value == "high" and val <= 100000: continue
                filtered.append(p)
            
            if srt_drop.value == "price_low": filtered.sort(key=lambda x: float(x.get("price", 0)))
            elif srt_drop.value == "price_high": filtered.sort(key=lambda x: float(x.get("price", 0)), reverse=True)
            elif srt_drop.value == "rating": filtered.sort(key=lambda x: float(x.get("rating", 0)), reverse=True)
            elif srt_drop.value == "popular": filtered.sort(key=lambda x: x.get("is_popular", False), reverse=True)

            count_text.value = f"Showing {len(filtered)} of {len(all_pkgs)} packages"
            for p in filtered: package_grid.controls.append(build_package_card(p))
            page.update()

        cat_drop.on_change = update_grid
        prc_drop.on_change = update_grid
        srt_drop.on_change = update_grid
        search_f.on_change = update_grid

        apply_btn = ft.ElevatedButton("Apply Filters", on_click=update_grid, bgcolor=PRIMARY_COLOR, color="white")
        async def reset_f(e):
            search_f.value = ""; cat_drop.value = "all"; prc_drop.value = "all"; srt_drop.value = "popular"
            await update_grid()
        reset_btn = ft.ElevatedButton("Reset Filters", on_click=reset_f)

        async def load_pkgs():
            nonlocal all_pkgs
            package_grid.controls.clear()
            package_grid.controls.append(ft.Container(ft.ProgressRing(), alignment=ft.Alignment(0, 0), padding=50))
            page.update()
            async with httpx.AsyncClient() as client:
                try:
                    r = await client.get(f"{BASE_URL}/api/event-packages/", headers={"Authorization": f"Token {page.data['token']}"})
                    if r.status_code == 200:
                        data = r.json()
                        all_pkgs = data.get("results") if isinstance(data, dict) else data
                        await update_grid()
                except Exception: package_grid.controls.append(ft.Text("Failed to load packages."))
            page.update()

        container.controls.extend([
            ft.Container(ft.Row([cat_drop, prc_drop, srt_drop, apply_btn, reset_btn], alignment="center", spacing=10), padding=ft.padding.only(top=20)),
            ft.Container(search_f, padding=ft.padding.symmetric(horizontal=50, vertical=10)),
            ft.Container(count_text, alignment=ft.Alignment(0, 0)),
            package_grid
        ])
        page.update(); await load_pkgs()

    def build_package_card(p):
        img_url = f"{BASE_URL}/static/banner_and_images/product_default.jpg"
        t = p.get("title", "")
        if "Premium" in t: img_url = f"{BASE_URL}/static/banner_and_images/premium_wedding.jpeg"
        elif "Intimate" in t: img_url = f"{BASE_URL}/static/banner_and_images/intimate_wedding.jpeg"
        elif "Social" in t: img_url = f"{BASE_URL}/static/banner_and_images/social_event.jpeg"
        elif "Graduation" in t: img_url = f"{BASE_URL}/static/banner_and_images/graduation.jpeg"
        elif "Birthday" in t: img_url = f"{BASE_URL}/static/banner_and_images/birthday.jpeg"
        elif "Corporate" in t: img_url = f"{BASE_URL}/static/banner_and_images/corporate.jpeg"

        return ft.Card(elevation=4, content=ft.Container(width=400, bgcolor="white", border_radius=12, content=ft.Column([
            ft.Stack([ft.Image(src=img_url, width=400, height=220, fit="cover"), ft.Container(ft.Text("Most Popular", size=10, weight="bold", color="white"), bgcolor=ft.Colors.ORANGE_700, padding=5, border_radius=5, right=10, top=10, visible=p.get("is_popular", False))]),
            ft.Container(content=ft.Column([ft.Text(t, size=20, weight="bold"), ft.Text(p.get("description", "")[:120] + "...", size=13, color=ft.Colors.GREY_600), ft.Row([ft.Icon(ft.Icons.STAR, color="amber", size=16), ft.Text(f"{p.get('rating')} ({p.get('review_count')})", size=12, weight="bold", color="amber")]), ft.Text(f"Rs {float(p.get('price', 0)):,.2f}", size=22, weight="bold", color=PRIMARY_COLOR), ft.ElevatedButton("View More Details", bgcolor=PRIMARY_COLOR, color="white", width=float("inf"), on_click=lambda _, pid=p.get("id"): show_details_page(pid))], spacing=10), padding=15)])))

    def show_details_page(package_id=None):
        container = page.data.get("main_container")
        if not container:
            return
        
        
        container.controls.clear()
        
        
        loading = ft.Container(
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text("Loading package details...", size=16, color=PRIMARY_COLOR)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True
        )
        container.controls.append(loading)
        page.update()
        
        async def display_package_details(package):
            container.controls.clear()
            
            # Extract package data
            title = package.get("title", "Untitled")
            description = package.get("description", "No description available")
            category = package.get("category", "Uncategorized")
            price = float(package.get("price", 0))
            rating = float(package.get("rating", 0))
            guest_capacity = package.get("guest_capacity", 0)
            is_popular = package.get("is_popular", False)
            features = package.get("features", [])
            
            # Choose image based on category
            category_images = {
                "wedding": f"{BASE_URL}/static/banner_and_images/premium_wedding.jpeg",
                "birthday": f"{BASE_URL}/static/banner_and_images/birthday.jpeg",
                "corporate": f"{BASE_URL}/static/banner_and_images/corporate.jpeg",
                "graduation": f"{BASE_URL}/static/banner_and_images/graduation.jpeg",
                "social": f"{BASE_URL}/static/banner_and_images/social_event.jpeg"
            }
            image_url = category_images.get(category, f"{BASE_URL}/static/banner_and_images/product_default.jpg")

            map_status = ft.Text(
                "Loading venue locations...",
                size=13,
                color=ft.Colors.GREY_700,
                visible=SHOW_MAP_IN_DETAILS,
            )
            map_holder = ft.Container(
                height=280,
                border_radius=12,
                bgcolor=ft.Colors.GREY_100,
                visible=SHOW_MAP_IN_DETAILS,
                content=ft.Column(
                    [
                        ft.Container(height=30),
                        ft.Row(
                            [ft.ProgressRing(), ft.Text("Loading map...", size=14, color=PRIMARY_COLOR)],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

            async def _load_map_markers():
                headers = {"Content-Type": "application/json"}
                token = page.data.get("token")
                if token:
                    headers["Authorization"] = f"Token {token}"

                venue_ids = package.get("venues") or []
                if not venue_ids:
                    try:
                        async with httpx.AsyncClient() as client:
                            vo_res = await client.get(
                                f"{BASE_URL}/api/venue-options/",
                                headers=headers,
                                timeout=8.0,
                            )
                        if vo_res.status_code == 200 and isinstance(vo_res.json(), list):
                            venue_ids = [
                                vo.get("venue")
                                for vo in vo_res.json()
                                if vo.get("package") == package.get("id") and vo.get("venue") is not None
                            ]
                    except Exception:
                        venue_ids = venue_ids

                if not venue_ids:
                    map_status.value = "No venues found for this package."
                    map_holder.content = ft.Container(
                        content=ft.Text("No venues to display on map.", color=ft.Colors.GREY_700),
                        alignment=ft.Alignment(0, 0),
                    )
                    page.update()
                    return

                try:
                    async with httpx.AsyncClient() as client:
                        venues_res = await client.get(
                            f"{BASE_URL}/api/venues/",
                            headers=headers,
                            timeout=8.0,
                        )

                    if venues_res.status_code != 200:
                        map_status.value = f"Failed to load venues (Status: {venues_res.status_code})"
                        map_holder.content = ft.Container(
                            content=ft.Text("Failed to load venue data.", color=ft.Colors.RED_700),
                            alignment=ft.Alignment(0, 0),
                        )
                        page.update()
                        return

                    venues_data = venues_res.json()
                    if isinstance(venues_data, dict):
                        venues_data = venues_data.get("results", [])

                    venue_id_set = set(int(v) for v in venue_ids if str(v).isdigit())
                    venues_for_package = [
                        v for v in venues_data
                        if int(v.get("id", -1)) in venue_id_set
                    ]

                    venues_with_coords = []
                    for v in venues_for_package:
                        lat = v.get("latitude")
                        lng = v.get("longitude")
                        if lat is None or lng is None:
                            continue
                        try:
                            venues_with_coords.append(
                                {
                                    "id": v.get("id"),
                                    "name": v.get("name", "Venue"),
                                    "location": v.get("location", ""),
                                    "latitude": float(lat),
                                    "longitude": float(lng),
                                }
                            )
                        except Exception:
                            continue

                    if not venues_with_coords:
                        map_status.value = "Venues loaded, but no coordinates available yet."
                        map_holder.content = ft.Container(
                            content=ft.Text("No venue coordinates available.", color=ft.Colors.GREY_700),
                            alignment=ft.Alignment(0, 0),
                        )
                        page.update()
                        return

                    center_lat = sum(v["latitude"] for v in venues_with_coords) / len(venues_with_coords)
                    center_lng = sum(v["longitude"] for v in venues_with_coords) / len(venues_with_coords)

                    markers = []
                    for v in venues_with_coords:
                        markers.append(
                            ftm.Marker(
                                coordinates=ftm.MapLatitudeLongitude(v["latitude"], v["longitude"]),
                                width=36,
                                height=36,
                                tooltip=f"{v.get('name', 'Venue')} {('- ' + v.get('location')) if v.get('location') else ''}".strip(),
                                content=ft.Icon(ft.Icons.LOCATION_ON, size=36, color=ft.Colors.RED_600),
                            )
                        )

                    map_status.value = f"Showing {len(markers)} venue location(s)."
                    map_holder.content = ftm.Map(
                        height=280,
                        initial_center=ftm.MapLatitudeLongitude(center_lat, center_lng),
                        initial_zoom=11,
                        layers=[
                            ftm.TileLayer(url_template="https://tile.memomaps.de/tilegen/{z}/{x}/{y}.png"),
                            ftm.MarkerLayer(markers=markers),
                        ],
                    )
                    page.update()
                except Exception as ex:
                    map_status.value = f"Map error: {ex}"
                    map_holder.content = ft.Container(
                        content=ft.Text("Unable to display map.", color=ft.Colors.RED_700),
                        alignment=ft.Alignment(0, 0),
                    )
                    page.update()

            # Build the details UI
            details_content = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                controls=[
                    # Hero Image
                    ft.Container(
                        content=ft.Image(src=image_url, width=float("inf"), height=300, fit="cover"),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                    
                    # Main Content Container
                    ft.Container(
                        content=ft.Column(
                            [
                                # Back button and title
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.ARROW_BACK,
                                            icon_size=28,
                                            on_click=lambda _: asyncio.create_task(show_packages_page()),
                                            tooltip="Back to packages"
                                        ),
                                        ft.Text("Package Details", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR, expand=True),
                                        ft.Container(width=40)
                                    ]
                                ),
                                
                                
                                # Category and Rating Row
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Text(category.upper(), size=14, weight=ft.FontWeight.W_500, color=PRIMARY_COLOR),
                                            bgcolor=ft.Colors.GREY_100,
                                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                            border_radius=15
                                        ),
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER, size=18),
                                                ft.Text(f"{rating}", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                               
                                            ],
                                            spacing=5
                                        )
                                    ],
                                    spacing=10
                                ),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.INVENTORY, size=24, color=PRIMARY_COLOR),
                                        ft.Text(package.get("title", "Package"), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
                                    ],
                                    spacing=10
                                ),
                                ft.Divider(height=20),
                                
                                # Price and Capacity Cards
                                ft.Row(
                                    [
                                        ft.Card(
                                            content=ft.Container(
                                                content=ft.Column(
                                                    [
                                                        ft.Row(
                                                            [
                                                                ft.Icon(ft.Icons.ATTACH_MONEY, size=16, color=ft.Colors.GREY_600),
                                                                ft.Text("Price", size=14, color=ft.Colors.GREY_600)
                                                            ],
                                                            spacing=5
                                                        ),
                                                        ft.Text(f"Rs {price:,.2f}", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
                                                    ],
                                                    spacing=5,
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                                ),
                                                padding=20,
                                                bgcolor = ft.Colors.WHITE,
                                            ),
                                            elevation=2,
                                            expand=True
                                        ),
                                        ft.Card(
                                            content=ft.Container(
                                                content=ft.Column(
                                                    [
                                                        ft.Row(
                                                            [
                                                                ft.Icon(ft.Icons.GROUP, size=16, color=ft.Colors.GREY_600),
                                                                ft.Text("Guest Capacity", size=14, color=ft.Colors.GREY_600)
                                                            ],
                                                            spacing=5
                                                        ),
                                                        ft.Text(f"Up to {guest_capacity}", size=28, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
                                                    ],
                                                    spacing=5,
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                                                ),
                                                padding=20,
                                                bgcolor = ft.Colors.WHITE,
                                            ),
                                            elevation=2,
                                            expand=True
                                        )
                                    ],
                                    spacing=20
                                ),
                                
                                ft.Divider(height=20),
                                
                                # Description Section
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.DESCRIPTION, size=24, color=PRIMARY_COLOR),
                                        ft.Text("Description", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87)
                                    ],
                                    spacing=10
                                ),
                                ft.Text(description, size=16, color=ft.Colors.GREY_800),
                                
                                # Features Section
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.STAR, size=24, color=PRIMARY_COLOR),
                                        ft.Text("Package Features", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
                                    ],
                                    spacing=10
                                ),
                                ft.Column(
                                    [
                                        ft.Row(
                                            [
                                                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=22),
                                                ft.Text(feature.get("feature", ""), size=15, expand=True,color=ft.Colors.BLACK87)
                                            ],
                                            spacing=10
                                        ) for feature in features
                                    ]
                                ) if features else ft.Text("No features listed", size=15, color=ft.Colors.GREY_600),
                                
                                ft.Divider(height=30),

                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.MAP, size=24, color=PRIMARY_COLOR),
                                        ft.Text("Venue Map", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                    ],
                                    spacing=10,
                                    visible=SHOW_MAP_IN_DETAILS,
                                ),
                                map_status,
                                ft.Container(
                                    content=map_holder,
                                    border_radius=12,
                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                    visible=SHOW_MAP_IN_DETAILS,
                                ),
                                
                                ft.Divider(height=30),
                                
                                
                                ft.Row(
                                    [
                                    ft.ElevatedButton(
                                        "View Venues",
                                        icon=ft.Icons.LOCATION_ON,
                                        bgcolor=PRIMARY_COLOR,
                                        color="white",
                                        width=180,
                                        height=45,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                        on_click=lambda _, pid=package.get("id"): asyncio.create_task(show_venues_page(pid))
                                    ),
                                    ft.Button(
                                        "View Reviews",
                                        icon=ft.Icons.RATE_REVIEW,
                                        bgcolor=PRIMARY_COLOR,
                                        color="white",
                                        width=180,
                                        height=45,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                                        on_click=lambda e, pid=package.get("id"): asyncio.create_task(
                                            show_reviews_page(page, pid, on_back=show_details_page)
                                        )
                                    )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=20
                                ),
                                
                                ft.Container(height=20)
                            ],
                            spacing=15
                        ),
                        padding=ft.padding.all(25),
                        bgcolor=ft.Colors.WHITE,
                        margin=ft.margin.only(top=-30)
                    )
                ]
            )
            
            container.controls.append(details_content)
            page.update()
            if SHOW_MAP_IN_DETAILS:
                asyncio.create_task(_load_map_markers())

        async def show_venues_page(package_id):
            container = page.data.get("main_container")
            if not container:
                return
            
            container.controls.clear()

            venues_status = ft.Text("Loading venues...", size=14, color=ft.Colors.GREY_700)
            venues_list = ft.Column(spacing=12)
            nearest_card = ft.Container()
            user_location_text = ft.Text("", size=13, color=ft.Colors.GREY_700)
            selected_location_text = ft.Text("Tip: tap the map to select a location.", size=13, color=ft.Colors.GREY_700)
            selected_pos_state = {"pos": None}
            venues_map_holder = ft.Container(
                height=320,
                border_radius=12,
                bgcolor=ft.Colors.GREY_100,
                content=ft.Column(
                    [
                        ft.Container(height=40),
                        ft.Row(
                            [ft.ProgressRing(), ft.Text("Loading map...", size=14, color=PRIMARY_COLOR)],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

            async def _load_venues_and_map(use_geolocation: bool = True):
                headers = {"Content-Type": "application/json"}
                token = page.data.get("token")
                if token:
                    headers["Authorization"] = f"Token {token}"

                try:
                    async with httpx.AsyncClient() as client:
                        vo_res = await client.get(
                            f"{BASE_URL}/api/venue-options/",
                            headers=headers,
                            timeout=8.0,
                        )

                    if vo_res.status_code != 200:
                        venues_status.value = f"Failed to load venue options (Status: {vo_res.status_code})"
                        venues_map_holder.content = ft.Container(
                            content=ft.Text("Failed to load venue options.", color=ft.Colors.RED_700),
                            alignment=ft.Alignment(0, 0),
                        )
                        page.update()
                        return

                    vo_data = vo_res.json()
                    if isinstance(vo_data, dict):
                        vo_data = vo_data.get("results", [])

                    venue_ids = [
                        vo.get("venue")
                        for vo in vo_data
                        if vo.get("package") == package_id and vo.get("venue") is not None
                    ]
                    venue_id_set = set(int(v) for v in venue_ids if str(v).isdigit())

                    if not venue_id_set:
                        venues_status.value = "No venues found for this package."
                        venues_map_holder.content = ft.Container(
                            content=ft.Text("No venues to display on map.", color=ft.Colors.GREY_700),
                            alignment=ft.Alignment(0, 0),
                        )
                        page.update()
                        return

                    async with httpx.AsyncClient() as client:
                        venues_res = await client.get(
                            f"{BASE_URL}/api/venues/",
                            headers=headers,
                            timeout=8.0,
                        )

                    if venues_res.status_code != 200:
                        venues_status.value = f"Failed to load venues (Status: {venues_res.status_code})"
                        venues_map_holder.content = ft.Container(
                            content=ft.Text("Failed to load venue data.", color=ft.Colors.RED_700),
                            alignment=ft.Alignment(0, 0),
                        )
                        page.update()
                        return

                    venues_data = venues_res.json()
                    if isinstance(venues_data, dict):
                        venues_data = venues_data.get("results", [])

                    venues_for_package = [
                        v for v in venues_data
                        if int(v.get("id", -1)) in venue_id_set
                    ]

                    def _render_venue_list(venues, distances_by_id=None):
                        venues_list.controls.clear()
                        for v in venues:
                            vid = int(v.get("id", -1)) if str(v.get("id", "")).isdigit() else -1
                            dkm = distances_by_id.get(vid) if isinstance(distances_by_id, dict) else None
                            venues_list.controls.append(
                                ft.Card(
                                    elevation=2,
                                    content=ft.Container(
                                        padding=16,
                                        content=ft.Column(
                                            [
                                                ft.Text(v.get("name", "Venue"), size=18, weight=ft.FontWeight.BOLD),
                                                ft.Text(v.get("location", ""), size=14, color=ft.Colors.GREY_700),
                                                ft.Text(
                                                    f"Distance: {dkm:.2f} km" if dkm is not None else "",
                                                    size=13,
                                                    color=ft.Colors.GREY_700,
                                                    visible=dkm is not None,
                                                ),
                                                ft.Row(
                                                    [
                                                        ft.Icon(ft.Icons.GROUP, size=16, color=PRIMARY_COLOR),
                                                        ft.Text(f"Capacity: {v.get('capacity', 'N/A')}", size=14),
                                                    ],
                                                    spacing=8,
                                                ),
                                            ],
                                            spacing=6,
                                        ),
                                    ),
                                )
                            )

                    _render_venue_list(venues_for_package)

                    venues_with_coords = []
                    for v in venues_for_package:
                        lat = v.get("latitude")
                        lng = v.get("longitude")
                        if lat is None or lng is None:
                            continue
                        try:
                            venues_with_coords.append(
                                {
                                    "id": v.get("id"),
                                    "name": v.get("name", "Venue"),
                                    "location": v.get("location", ""),
                                    "latitude": float(lat),
                                    "longitude": float(lng),
                                }
                            )
                        except Exception:
                            continue

                    if not venues_with_coords:
                        venues_status.value = f"Showing {len(venues_for_package)} venue(s). (No coordinates available.)"
                        venues_map_holder.content = ft.Container(
                            content=ft.Text("No venue coordinates available.", color=ft.Colors.GREY_700),
                            alignment=ft.Alignment(0, 0),
                        )
                        page.update()
                        return

                    user_pos = None
                    nearest_card.content = None
                    if not use_geolocation:
                        user_location_text.value = ""
                    if use_geolocation and ftg is not None:
                        try:
                            geo = page.data.get("geolocator")
                            if geo is None:
                                geo = ftg.Geolocator(
                                    configuration=ftg.GeolocatorConfiguration(
                                        accuracy=ftg.GeolocatorPositionAccuracy.LOW
                                    ),
                                    on_position_change=lambda e: None,
                                    on_error=lambda e: None,
                                )
                                page.data["geolocator"] = geo

                            perm = await geo.request_permission()
                            perm_s = str(perm).lower()
                            if "denied" in perm_s or "restricted" in perm_s:
                                user_location_text.value = "Location permission denied. Showing venues only."
                            else:
                                p = await geo.get_current_position()
                                user_pos = (float(p.latitude), float(p.longitude))
                                user_location_text.value = f"Your location: {user_pos[0]:.5f}, {user_pos[1]:.5f}"
                        except Exception as ex:
                            user_location_text.value = f"Geolocation unavailable: {ex}"
                    elif use_geolocation and ftg is None:
                        user_location_text.value = "Geolocation not installed. Add dependency: flet-geolocator"

                    center_lat = sum(v["latitude"] for v in venues_with_coords) / len(venues_with_coords)
                    center_lng = sum(v["longitude"] for v in venues_with_coords) / len(venues_with_coords)

                    render_state = {"fn": None}

                    def _render_for_reference():
                        reference_pos = selected_pos_state.get("pos") or user_pos
                        using_selected = selected_pos_state.get("pos") is not None

                        distances_by_id = {}
                        if reference_pos is not None:
                            for v in venues_for_package:
                                lat = v.get("latitude")
                                lng = v.get("longitude")
                                if lat is None or lng is None:
                                    continue
                                try:
                                    vid = int(v.get("id", -1))
                                    distances_by_id[vid] = _haversine_distance_km(
                                        float(reference_pos[0]), float(reference_pos[1]), float(lat), float(lng)
                                    )
                                except Exception:
                                    continue

                            sorted_venues = sorted(
                                venues_for_package,
                                key=lambda v: distances_by_id.get(int(v.get("id", -1)), 10**9),
                            )
                            _render_venue_list(sorted_venues, distances_by_id=distances_by_id)
                        else:
                            _render_venue_list(venues_for_package)

                        if using_selected and reference_pos is not None:
                            selected_location_text.value = f"Selected location: {float(reference_pos[0]):.5f}, {float(reference_pos[1]):.5f}"
                        else:
                            selected_location_text.value = "Tip: tap the map to select a location."

                        if reference_pos is not None and distances_by_id:
                            nearest_vid = min(distances_by_id, key=lambda k: distances_by_id[k])
                            nearest_v = next((v for v in venues_for_package if int(v.get("id", -1)) == nearest_vid), None)
                            if nearest_v is not None:
                                nearest_card.content = ft.Card(
                                    elevation=2,
                                    content=ft.Container(
                                        padding=16,
                                        content=ft.Row(
                                            [
                                                ft.Icon(ft.Icons.NEAR_ME, color=PRIMARY_COLOR, size=26),
                                                ft.Column(
                                                    [
                                                        ft.Text("Nearest venue", weight=ft.FontWeight.BOLD, size=16),
                                                        ft.Text(nearest_v.get("name", "Venue"), size=16),
                                                        ft.Text(
                                                            f"{nearest_v.get('location', '')} • {distances_by_id[nearest_vid]:.2f} km away",
                                                            size=13,
                                                            color=ft.Colors.GREY_700,
                                                        ),
                                                    ],
                                                    spacing=2,
                                                    expand=True,
                                                ),
                                            ],
                                            spacing=12,
                                        ),
                                    ),
                                )
                        else:
                            nearest_card.content = None

                        markers = []
                        highlight_ids = set()
                        if reference_pos is not None and distances_by_id:
                            nearest_sorted_ids = sorted(distances_by_id.keys(), key=lambda k: distances_by_id[k])
                            highlight_ids = set(nearest_sorted_ids[:5])
                        for v in venues_with_coords:
                            vid = int(v.get("id", -1)) if str(v.get("id", "")).isdigit() else -1
                            marker_color = LABEL_COLOR
                            marker_size = 36
                            if vid != -1 and reference_pos is not None and distances_by_id:
                                if vid == nearest_vid:
                                    marker_color = LINK_COLOR
                                    marker_size = 40
                                elif vid in highlight_ids:
                                    marker_color = PRIMARY_COLOR
                                    marker_size = 38
                            markers.append(
                                ftm.Marker(
                                    coordinates=ftm.MapLatitudeLongitude(v["latitude"], v["longitude"]),
                                    width=marker_size,
                                    height=marker_size,
                                    tooltip=f"{v.get('name', 'Venue')} {('- ' + v.get('location')) if v.get('location') else ''}".strip(),
                                    content=ft.Icon(ft.Icons.LOCATION_ON, size=marker_size, color=marker_color),
                                )
                            )

                        if user_pos is not None:
                            markers.append(
                                ftm.Marker(
                                    coordinates=ftm.MapLatitudeLongitude(user_pos[0], user_pos[1]),
                                    width=30,
                                    height=30,
                                    tooltip="You are here",
                                    content=ft.Icon(ft.Icons.MY_LOCATION, size=30, color=PRIMARY_COLOR),
                                )
                            )

                        if using_selected and reference_pos is not None:
                            markers.append(
                                ftm.Marker(
                                    coordinates=ftm.MapLatitudeLongitude(float(reference_pos[0]), float(reference_pos[1])),
                                    width=30,
                                    height=30,
                                    tooltip="Selected location",
                                    content=ft.Icon(ft.Icons.PLACE, size=30, color=LABEL_COLOR),
                                )
                            )

                        map_center = (
                            (float(reference_pos[0]), float(reference_pos[1]))
                            if reference_pos is not None
                            else (center_lat, center_lng)
                        )

                        venues_status.value = (
                            f"Showing {len(venues_for_package)} venue(s) and {len(markers)} marker(s). "
                            f"{'Nearest venues are highlighted.' if reference_pos is not None else ''}"
                        ).strip()
                        venues_map_holder.content = ftm.Map(
                            height=320,
                            initial_center=ftm.MapLatitudeLongitude(map_center[0], map_center[1]),
                            initial_zoom=12 if reference_pos is not None else 11,
                            layers=[
                                ftm.TileLayer(url_template="https://tile.memomaps.de/tilegen/{z}/{x}/{y}.png"),
                                ftm.MarkerLayer(markers=markers),
                            ],
                            on_tap=handle_map_tap,
                        )
                        page.update()

                    def handle_map_tap(e: ftm.MapTapEvent):
                        if getattr(e, "coordinates", None) is not None:
                            selected_pos_state["pos"] = (e.coordinates.latitude, e.coordinates.longitude)
                            if render_state["fn"] is not None:
                                render_state["fn"]()

                    render_state["fn"] = _render_for_reference
                    _render_for_reference()
                except Exception as ex:
                    venues_status.value = f"Venues/map error: {ex}"
                    venues_map_holder.content = ft.Container(
                        content=ft.Text("Unable to display venues map.", color=ft.Colors.RED_700),
                        alignment=ft.Alignment(0, 0),
                    )
                    page.update()
            
            # Create venues page content
            venues_content = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                controls=[
                    
                    ft.Container(
                        content=ft.Image(src=f"{BASE_URL}/static/banner_and_images/venues_banner.jpg", width=float("inf"), height=200, fit="cover"),
                        bgcolor=ft.Colors.GREY_200,
                    ),
                    
                    # Main Content Container
                    ft.Container(
                        content=ft.Column(
                            [
                                # Back button and title
                                ft.Row(
                                    [
                                    ft.IconButton(
                                        icon=ft.Icons.ARROW_BACK,
                                        icon_size=28,
                                        on_click=lambda _, pid=package_id: show_details_page(pid),
                                        tooltip="Back to package details"
                                    ),
                                        ft.Text("Venues", size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR, expand=True),
                                    ]
                                ),
                                
                                ft.Divider(height=20),

                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.MAP, size=24, color=PRIMARY_COLOR),
                                        ft.Text("Venue Map", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                    ],
                                    spacing=10,
                                ),
                                venues_status,
                                user_location_text,
                                selected_location_text,
                                ft.Row(
                                    [
                                        ft.OutlinedButton(
                                            "Use my location",
                                            icon=ft.Icons.MY_LOCATION,
                                            on_click=lambda e: (
                                                selected_pos_state.__setitem__("pos", None),
                                                asyncio.create_task(_load_venues_and_map(True)),
                                            ),
                                        ),
                                        ft.OutlinedButton(
                                            "Show venues only",
                                            on_click=lambda e: asyncio.create_task(_load_venues_and_map(False)),
                                        ),
                                    ],
                                    spacing=10,
                                    wrap=True,
                                ),
                                nearest_card,
                                ft.Container(
                                    content=venues_map_holder,
                                    border_radius=12,
                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                ),
                                ft.Divider(height=20),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.LOCATION_ON, size=24, color=PRIMARY_COLOR),
                                        ft.Text("Venues", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                    ],
                                    spacing=10,
                                ),
                                venues_list,
                                
                                ft.Container(height=20)
                            ],
                            spacing=15
                        ),
                        padding=ft.padding.all(25),
                        bgcolor=ft.Colors.WHITE,
                        margin=ft.margin.only(top=-30)
                    )
                ]
            )
            
            container.controls.append(venues_content)
            page.update()
            asyncio.create_task(_load_venues_and_map(True))
        
        
        async def fetch_details():
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(
                        f"{BASE_URL}/api/event-packages/{package_id}/",
                        headers={"Authorization": f"Token {page.data['token']}"}
                    )
                    
                    if response.status_code == 200:
                        package = response.json()
                        await display_package_details(package)
                    else:
                        container.controls.clear()
                        container.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                                    ft.Text(f"Error {response.status_code}: Failed to load package details", 
                                            size=18, color=ft.Colors.RED_700),
                                    ft.ElevatedButton("Go Back", on_click=lambda _: asyncio.create_task(show_packages_page()))
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                expand=True
                            )
                        )
                    page.update()
                    
                except Exception as e:
                    container.controls.clear()
                    container.controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED_400),
                                ft.Text(f"Error: {str(e)}", size=18, color=ft.Colors.RED_700),
                                ft.ElevatedButton("Go Back", on_click=lambda _: asyncio.create_task(show_packages_page()))
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            expand=True
                        )
                    )
                    page.update()
        
        asyncio.create_task(fetch_details())

    show_login_page()


if __name__ == "__main__":
    ft.app(target=main)
