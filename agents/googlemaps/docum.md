# Route Chat with Maps and Natural Language

This project implements a geospatial + language interface to "chat with a route" using a combination of the Google Maps Routes API, OpenStreetMap (via Overpass API), and a Leaflet.js frontend. The system allows you to visualize a route, annotate it with cities, towns, and natural landmarks, and integrate a future chat-based assistant.

---

## ✅ Implemented Features

### 1. Google Maps Route Retrieval
- Uses `google-maps-routing` to fetch route between origin and destination.
- Retrieves:
  - Encoded polyline
  - Navigation steps
  - Distance and duration

### 2. Polyline Sampling
- `sample_polyline()` samples points along the route using either:
  - Distance-based intervals (e.g., every 5 km)
  - Every Nth point from polyline

### 3. Overpass API Queries
- Cities, towns, and villages (`place=city|town|village`)
  - Queried using both `around:radius` for each point **and** `way(poly:...)`
- Natural features (rivers, lakes, peaks, woods, cliffs, etc.)
  - Queried using `natural=*`, `waterway=*` with optional polyline method

### 4. Visualization (HTML Maps)
- Uses `folium` to render:
  - Polyline route
  - Points for cities, towns, and natural landmarks
- Output map is saved to `route_map.html`

### 5. Interactive Chat UI
- `map_chat_ui.html` contains:
  - Embedded Leaflet map
  - Side-panel chat UI
  - Loads JSON route + marker data
  - Markers styled by type (red = city, blue = lake, etc.)
  - Simulated chat interface for LLM integration

---

## 📂 File Overview

- `routechat.py` — Main Python pipeline (route, sample, query, render)
- `map_chat_ui.html` — Dynamic UI to explore route and chat with it
- `sampled_points.json` — Sampled route coordinates
- `polyline_route.json` — Full decoded polyline
- `places_along_route.json` — List of OSM places nearby
- `natural_features_along_route.json` — List of rivers, lakes, etc.

---

## 🧠 Next Steps / TODOs

- [ ] Order cities along route for better LLM context
- [ ] Store all route + geo info in a lightweight database (e.g. SQLite or JSONL)
- [ ] Replace demo reply with a real LLM backend (e.g. Flask API with local LLM)
- [ ] Allow interactive map elements to trigger chat inputs (e.g. click a city → ask question)
- [ ] Support search: “Are there any rivers after Fresno?”

---

## 🧪 Running the App

1. Run `routechat.py` to generate JSON files and render folium map.
2. Serve HTML using Python:
   ```bash
   python -m http.server 8000
   ```
3. Open `http://localhost:8000/map_chat_ui.html`

---

## 📦 Dependencies

- Python: `googlemaps`, `polyline`, `geopy`, `folium`, `requests`
- Web: `Leaflet.js`, basic HTML/CSS/JS

---

MIT License. Built with 🤖 + 🗺️

--- 
