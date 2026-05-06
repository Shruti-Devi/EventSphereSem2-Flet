# EventSphereSem2-Flet

A mobile application built with Python and Flet that connects to the EventSphere Django REST API. Users can log in, browse event packages, view venue locations on a map, and read reviews. The colours and styling follow the existing EventSphere web platform.

---

## Built With

| Library | Purpose |
|---|---|
| [Flet](https://flet.dev/) | Python framework for building mobile apps |
| [flet_map](https://github.com/flet-dev/flet-map) | Interactive map display |
| [flet_geolocator](https://github.com/flet-dev/flet-geolocator) | Device GPS and location access |
| [httpx](https://www.python-httpx.org/) | Async HTTP requests to the REST API |

---

## Features

1. **Authentication** — Users can log in, register a new account, or request a password reset. All API calls are secured with Token Authentication.
2. **Package Browsing** — Browse and filter event packages by category, price range, and rating, with a live search bar.
3. **Package Details** — View full package information including description, price, guest capacity, and a list of included features.
4. **Venue Map** — An interactive map displays all venues linked to a package, with markers colour-coded by proximity to the user.
5. **Geolocation** — The app accesses the device GPS to find the user's current position and calculates the distance to each venue.
6. **Map Tap** — Users can tap anywhere on the map to set a custom reference point, and the distance calculations update instantly.
7. **Reviews** — Each package has a dedicated reviews page showing reviewer name, star rating, comment, and date.

---

## Setup & Installation

1. **Clone the repository**

2. **Create a virtual environment and activate it**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

3. **Install dependencies**
    ```bash
    pip install flet flet-map flet-geolocator httpx
    ```

4. **Make sure the EventSphere Django backend is running**

---

## Running the App

```bash
cd src

# Desktop (for testing)
flet run main.py

# Android
flet run --android main.py
```
