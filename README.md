# EventSphereSem2-Flet

A mobile application built with Python and Flet that connects to the EventSphere Django REST API. Users can log in, browse event packages, view venue locations on a map, and read reviews.

Built With

Flet — Python framework for building mobile apps
flet_map — Interactive map display
flet_geolocator — Device GPS and location access
httpx — Async HTTP requests to the REST API


Features:

Login, Register, and Forgot Password
Browse and filter event packages by category, price, and rating
View full package details (description, price, features, guest capacity)
Interactive map showing venue locations with proximity highlighting
Geolocation — detects user's position and calculates distance to each venue
Tap the map to set a custom reference point and recalculate distances
View customer reviews per package
All API calls use Token Authentication
The colors and text follow the existing EventSphere web pages.

Setup & Installation
1.Clone the repository
2.Create a virtual environment and activate it
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # Windows: .venv\Scripts\activate
  ```
3.Install dependencies
  ```bash
  pip install flet flet-map flet-geolocator httpx
  ```
4.Make sure the EventSphere Django backend is running
5.Running the App
```bash
  cd src
  
  # Desktop (for testing)
  flet run main.py
  
  # Android
  flet run --android main.py
```



