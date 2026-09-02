import streamlit as st
import fastf1
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go

os.makedirs('cache', exist_ok=True)
fastf1.Cache.enable_cache('cache')

st.set_page_config(page_title="F1 Telemetry Analyzer", layout="wide")
st.title("🏎️ F1 Telemetry Analyzer")
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        font-size: 16px;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] { font-size: 22px; }
    .stButton>button {
        background-color: #E10600;
        color: white;
        font-weight: 600;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar inputs ---
st.sidebar.header("Session Settings")
year = st.sidebar.selectbox("Year", [2024, 2023, 2022])
gp = st.sidebar.text_input("Grand Prix", "Monza")
session_type = st.sidebar.selectbox("Session", ["R", "Q", "FP1", "FP2", "FP3"])
driver1 = st.sidebar.text_input("Driver 1", "VER")
driver2 = st.sidebar.text_input("Driver 2", "HAM")
load_btn = st.sidebar.button("Load & Analyze")

if load_btn:
    with st.spinner("Loading session data..."):
        session = fastf1.get_session(year, gp, session_type)
        session.load()

        lap1 = session.laps.pick_driver(driver1).pick_fastest()
        lap2 = session.laps.pick_driver(driver2).pick_fastest()
        tel1 = lap1.get_telemetry()
        tel2 = lap2.get_telemetry()

    st.session_state['session'] = session
    st.session_state['lap1'] = lap1
    st.session_state['lap2'] = lap2
    st.session_state['tel1'] = tel1
    st.session_state['tel2'] = tel2
    st.session_state['driver1'] = driver1
    st.session_state['driver2'] = driver2

# Only show tabs once data is loaded
if 'tel1' in st.session_state:
    session = st.session_state['session']
    lap1, lap2 = st.session_state['lap1'], st.session_state['lap2']
    tel1, tel2 = st.session_state['tel1'], st.session_state['tel2']
    driver1, driver2 = st.session_state['driver1'], st.session_state['driver2']

    tab1, tab2, tab3, tab4, tab5,tab6 = st.tabs(
        ["Speed", "Throttle/Brake", "Track Map", "Tyre Stints", "Sector Times","Race Pace"]
    )

    # --- Tab 1: Speed comparison ---
    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=tel1['Distance'], y=tel1['Speed'], name=driver1,
                                  line=dict(color='#3B82F6', width=2)))
        fig.add_trace(go.Scatter(x=tel2['Distance'], y=tel2['Speed'], name=driver2,
                                  line=dict(color='#F97316', width=2)))
        fig.update_layout(
            title=f'{driver1} vs {driver2} - {gp} {year}',
            xaxis_title='Distance (m)', yaxis_title='Speed (km/h)',
            hovermode='x unified', template='plotly_dark', height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Lap Time Summary")
        col1, col2 = st.columns(2)
        col1.metric(driver1, str(lap1['LapTime']))
        col2.metric(driver2, str(lap2['LapTime']))

    # --- Tab 2: Throttle & Brake ---
    with tab2:
        from plotly.subplots import make_subplots

        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                             subplot_titles=("Speed", "Throttle", "Brake"))

        fig.add_trace(go.Scatter(x=tel1['Distance'], y=tel1['Speed'], name=driver1,
                                  line=dict(color='#3B82F6')), row=1, col=1)
        fig.add_trace(go.Scatter(x=tel2['Distance'], y=tel2['Speed'], name=driver2,
                                  line=dict(color='#F97316')), row=1, col=1)

        fig.add_trace(go.Scatter(x=tel1['Distance'], y=tel1['Throttle'], name=driver1,
                                  line=dict(color='#3B82F6'), showlegend=False), row=2, col=1)
        fig.add_trace(go.Scatter(x=tel2['Distance'], y=tel2['Throttle'], name=driver2,
                                  line=dict(color='#F97316'), showlegend=False), row=2, col=1)

        fig.add_trace(go.Scatter(x=tel1['Distance'], y=tel1['Brake'], name=driver1,
                                  line=dict(color='#3B82F6'), showlegend=False), row=3, col=1)
        fig.add_trace(go.Scatter(x=tel2['Distance'], y=tel2['Brake'], name=driver2,
                                  line=dict(color='#F97316'), showlegend=False), row=3, col=1)

        fig.update_layout(height=800, template='plotly_dark', hovermode='x unified')
        fig.update_xaxes(title_text="Distance (m)", row=3, col=1)
        st.plotly_chart(fig, use_container_width=True)

    # --- Tab 3: Track map (Speed / Dominance) ---
    with tab3:
        map_mode = st.radio("Map mode", ["Speed (single driver)", "Dominance (who's faster)"], horizontal=True)

        if map_mode == "Speed (single driver)":
            driver_for_map = st.radio("Driver", [driver1, driver2], horizontal=True, key="speed_map_driver")
            tel_map = tel1 if driver_for_map == driver1 else tel2

            fig = go.Figure(go.Scatter(
                x=tel_map['X'], y=tel_map['Y'], mode='markers',
                marker=dict(size=5, color=tel_map['Speed'], colorscale='Viridis',
                            colorbar=dict(title='Speed (km/h)'))
            ))
            fig.update_layout(title=f'{driver_for_map} - Track Map Colored by Speed',
                               template='plotly_dark', height=600,
                               xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor='x'))
            st.plotly_chart(fig, use_container_width=True)

        else:
            n_bins = 100
            tel1_r = tel1.copy()
            tel2_r = tel2.copy()
            tel1_r['bin'] = pd.cut(tel1_r['Distance'], n_bins, labels=False)
            tel2_r['bin'] = pd.cut(tel2_r['Distance'], n_bins, labels=False)

            avg1 = tel1_r.groupby('bin')[['Speed', 'X', 'Y']].mean()
            avg2 = tel2_r.groupby('bin')[['Speed']].mean()

            faster = np.where(avg1['Speed'].values >= avg2['Speed'].values, 1, 0)
            colors = ['#3B82F6' if f == 1 else '#F97316' for f in faster]

            fig = go.Figure(go.Scatter(
                x=avg1['X'], y=avg1['Y'], mode='markers',
                marker=dict(size=8, color=colors)
            ))
            fig.update_layout(title=f'Track Dominance: Blue = {driver1} faster, Orange = {driver2} faster',
                               template='plotly_dark', height=600,
                               xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor='x'))
            st.plotly_chart(fig, use_container_width=True)

    # --- Tab 4: Tyre stints ---
    with tab4:
        stint_driver = st.radio("Driver for tyre stints", [driver1, driver2], horizontal=True, key="stint_driver")
        driver_stints = session.laps.pick_driver(stint_driver)

        fig = go.Figure()
        compound_colors = {'SOFT': '#EF4444', 'MEDIUM': '#F59E0B', 'HARD': '#E5E7EB',
                            'INTERMEDIATE': '#22C55E', 'WET': '#3B82F6'}

        for compound in driver_stints['Compound'].unique():
            stint_laps = driver_stints[driver_stints['Compound'] == compound]
            fig.add_trace(go.Scatter(
                x=stint_laps['LapNumber'], y=stint_laps['LapTime'].dt.total_seconds(),
                mode='markers', name=compound,
                marker=dict(size=8, color=compound_colors.get(compound, '#999999'))
            ))

        fig.update_layout(title=f'{stint_driver} - Lap Time by Tyre Compound',
                           xaxis_title='Lap Number', yaxis_title='Lap Time (s)',
                           template='plotly_dark', height=500)
        st.plotly_chart(fig, use_container_width=True)
        # --- Tab 5: Sector time comparison ---
    with tab5:
        sector_data = pd.DataFrame({
            'Driver': [driver1, driver2],
            'Lap Time': [str(lap1['LapTime']), str(lap2['LapTime'])],
            'Sector 1': [str(lap1['Sector1Time']), str(lap2['Sector1Time'])],
            'Sector 2': [str(lap1['Sector2Time']), str(lap2['Sector2Time'])],
            'Sector 3': [str(lap1['Sector3Time']), str(lap2['Sector3Time'])],
            'Compound': [lap1['Compound'], lap2['Compound']]
        })

        st.subheader("Sector Time Comparison")
        st.dataframe(sector_data, use_container_width=True)

        s1_delta = (lap1['Sector1Time'] - lap2['Sector1Time']).total_seconds()
        s2_delta = (lap1['Sector2Time'] - lap2['Sector2Time']).total_seconds()
        s3_delta = (lap1['Sector3Time'] - lap2['Sector3Time']).total_seconds()

        st.subheader(f"Delta ({driver1} vs {driver2})")
        col1, col2, col3 = st.columns(3)
        col1.metric("Sector 1", f"{s1_delta:+.3f}s")
        col2.metric("Sector 2", f"{s2_delta:+.3f}s")
        col3.metric("Sector 3", f"{s3_delta:+.3f}s")

    # --- Tab 6: Race Pace ---
    with tab6:
        laps1 = session.laps.pick_driver(driver1).pick_quicklaps()
        laps2 = session.laps.pick_driver(driver2).pick_quicklaps()
        window = 3

        roll1 = laps1["LapTime"].dt.total_seconds().rolling(window, min_periods=1).mean()
        roll2 = laps2["LapTime"].dt.total_seconds().rolling(window, min_periods=1).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=laps1["LapNumber"], y=laps1["LapTime"].dt.total_seconds(),
                                  mode='markers', name=f'{driver1} (lap)',
                                  marker=dict(color='#3B82F6', opacity=0.4)))
        fig.add_trace(go.Scatter(x=laps2["LapNumber"], y=laps2["LapTime"].dt.total_seconds(),
                                  mode='markers', name=f'{driver2} (lap)',
                                  marker=dict(color='#F97316', opacity=0.4)))
        fig.add_trace(go.Scatter(x=laps1["LapNumber"], y=roll1, mode='lines',
                                  name=f'{driver1} (avg)', line=dict(color='#3B82F6', width=3)))
        fig.add_trace(go.Scatter(x=laps2["LapNumber"], y=roll2, mode='lines',
                                  name=f'{driver2} (avg)', line=dict(color='#F97316', width=3)))

        pit_laps1 = laps1[laps1["PitOutTime"].notna()]["LapNumber"]
        pit_laps2 = laps2[laps2["PitOutTime"].notna()]["LapNumber"]
        for lap_num in pit_laps1:
            fig.add_vline(x=lap_num, line_dash="dash", line_color="#3B82F6", opacity=0.4)
        for lap_num in pit_laps2:
            fig.add_vline(x=lap_num, line_dash="dash", line_color="#F97316", opacity=0.4)

        fig.update_layout(title='Race Pace', xaxis_title='Lap Number', yaxis_title='Lap Time (s)',
                           template='plotly_dark', height=550, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Dashed vertical lines mark pit stops. Solid lines show 3-lap rolling average pace.")

        st.subheader("Race Pace Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{driver1} avg lap", f"{laps1['LapTime'].dt.total_seconds().mean():.3f}s")
            st.metric(f"{driver1} consistency (std dev)", f"{laps1['LapTime'].dt.total_seconds().std():.3f}s")
        with col2:
            st.metric(f"{driver2} avg lap", f"{laps2['LapTime'].dt.total_seconds().mean():.3f}s")
            st.metric(f"{driver2} consistency (std dev)", f"{laps2['LapTime'].dt.total_seconds().std():.3f}s")