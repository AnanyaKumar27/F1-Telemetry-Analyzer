# 🏎️ F1 Telemetry Analyzer

An interactive web app for analyzing Formula 1 telemetry data. Built with Python, [FastF1](https://docs.fastf1.dev/), Streamlit, and Plotly — compare drivers' speed, throttle/brake, tyre strategy, sector times, and full-race pace using real F1 timing data.

## Features

- **Speed Trace Comparison** — overlay two drivers' speed across a lap
- **Throttle & Brake Analysis** — stacked speed/throttle/brake telemetry view
- **Track Map** — color-coded by speed, or by "track dominance" (who's faster where)
- **Tyre Stint Analysis** — lap time by tyre compound across a stint
- **Sector Time Comparison** — lap and sector time deltas between two drivers
- **Full Race Pace** — lap-by-lap pace trend with pit stop markers and rolling average
- Interactive Plotly charts (hover, zoom, pan)

## Tech Stack

- **Python**
- [**FastF1**](https://github.com/theOehrly/Fast-F1) — F1 timing & telemetry data
- **Streamlit** — interactive web app framework
- **Plotly** — interactive charts
- **Pandas / NumPy** — data processing

## Screenshots

<img width="1904" height="910" alt="image" src="https://github.com/user-attachments/assets/f51a8072-dfd0-44b7-b167-ab95a8decdc5" />


## Setup & Run Locally

1. Clone the repo
```bash
   git clone https://github.com/AnanyaKumar27/F1-Telemetry-Analyzer.git
   cd F1-Telemetry-Analyzer
```

2. Create and activate a virtual environment
```bash
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   source .venv/bin/activate   # Mac/Linux
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

4. Run the app
```bash
   streamlit run app.py
```

5. In the sidebar, enter a year, Grand Prix, session type, and two driver codes (e.g. `VER`, `HAM`), then click **Load & Analyze**.

## Notes

- FastF1 caches downloaded session data locally in a `cache/` folder to speed up repeated loads.
- Data is fetched live from F1's timing API via FastF1, so the first load of a session may take a few seconds.
- This app is best run locally — some cloud hosting environments (e.g. Streamlit Community Cloud) may have restricted network access to F1's data servers, causing intermittent load failures.

## Possible Future Additions

- Corner-by-corner braking point comparison
- Gear shift map
- Multi-driver (3+) comparisons
- Historical season trends
