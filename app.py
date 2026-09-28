import sys
import asyncio
from pathlib import Path
import os
import re
import json
import time

# 1. Windows Asyncio loop fix (must run before any async/network calls)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 2. Add project root to module lookup
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_folium import st_folium
from google import genai
from google.genai.errors import APIError, ClientError, ServerError

# Tool Imports
from tools.packing_generator import generate_packing_checklist
from tools.pdf_exporter import generate_pdf_itinerary
from tools.map_builder import render_trail_map
from tools.weather import get_himalayan_weather
from tools.altitude import check_altitude_safety
from tools.permits import get_nepal_trek_permit
from tools.budget import calculate_teahouse_budget

load_dotenv()

st.set_page_config(
    page_title="Nepal Trek AI Planner",
    page_icon="🏔️",
    layout="wide"
)

# Initialize Session State
if "itinerary_response" not in st.session_state:
    st.session_state["itinerary_response"] = None

st.title("🏔️ Nepal Himalayan Trekking AI Agent")
st.caption("Autonomous trekking assistant with real-time permit checks, altitude safety validation, and elevation telemetry.")

# Sidebar Configuration
with st.sidebar:
    st.header("Trek Configuration")
    selected_region = st.selectbox(
        "Choose Trekking Region",
        ["Annapurna", "Everest", "Langtang", "Manaslu"]
    )
    trek_days = st.slider(
        "Trip Duration (Days)",
        min_value=3, max_value=21, value=8
    )
    fitness_level = st.select_slider(
        "Fitness Level",
        options=["Beginner", "Moderate", "Experienced", "High Altitude Veteran"]
    )
    trekking_style = st.selectbox(
        "Trekking Budget Style",
        ["Standard", "Budget", "Comfort"]
    )
    hire_guide = st.checkbox(
        "Hire Licensed Guide (~$30/day)",
        value=True,
        help="Mandatory for foreign trekkers in ACAP, Langtang, and Manaslu."
    )
    hire_porter = st.checkbox(
        "Hire Porter (~$22/day)",
        value=False,
        help="Carries up to 18-20 kg of luggage."
    )
    generate_btn = st.button("Generate Safe Itinerary", type="primary", width="stretch")

# ----------------- EXECUTION CONTROLLER -----------------
if generate_btn:
    with st.spinner("Autonomous agent analyzing routes, permits, and elevation safety..."):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]

        if not api_key:
            st.error("GEMINI_API_KEY not found in environment or secrets.toml.")
            st.stop()

        prompt = (
            f"Plan a realistic {trek_days}-day trekking itinerary for the {selected_region} region in Nepal "
            f"for a trekker with '{fitness_level}' fitness level and '{trekking_style}' budget style.\n"
            f"Staff configuration: Licensed Guide: {hire_guide}, Porter: {hire_porter}.\n"
            f"You MUST use your custom tools:\n"
            f"1. 'get_nepal_trek_permit' to check regional permits and checkpoint requirements.\n"
            f"2. 'check_altitude_safety' to verify safe altitude increments and acclimatization days.\n"
            f"3. 'get_himalayan_weather' to inspect real-time weather at the key hubs.\n"
            f"4. 'generate_packing_checklist' to create a comprehensive, temperature-aware gear checklist.\n"
            f"5. 'calculate_teahouse_budget' passing hire_guide={hire_guide} and hire_porter={hire_porter} "
            f"to provide an itemized daily cost breakdown including staff wages (in NPR & USD) and cash reserve.\n\n"
            f"Provide the complete itinerary in markdown format with permit breakdown, live weather summary, "
            f"budget estimation breakdown, and an organized packing checklist with checkboxes (- [ ] Item).\n\n"
            f"IMPORTANT: At the very end of your response, output a raw JSON block enclosed in ```json ``` "
            f"containing an array of objects for the elevation graph with keys: "
            f"'day_label' (e.g. 'Day 1: Pokhara to Hile') and 'elevation_m' (integer sleeping altitude in meters)."
        )

        client = genai.Client(api_key=api_key)
        candidate_models = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
        generated_text = None

        for model_name in candidate_models:
            try:
                chat = client.chats.create(
                    model=model_name,
                    config={
                        "tools": [
                            get_nepal_trek_permit,
                            check_altitude_safety,
                            get_himalayan_weather,
                            generate_packing_checklist,
                            calculate_teahouse_budget
                        ]
                    }
                )

                retry_delay = 5
                for attempt in range(3):
                    try:
                        response = chat.send_message(prompt)
                        generated_text = response.text
                        break
                    except Exception as api_err:
                        err_str = str(api_err)
                        if ("503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str) and attempt < 2:
                            st.warning(f"Google server load spike ({model_name}). Pausing {retry_delay}s... (Attempt {attempt + 1}/3)")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                        raise

                if generated_text:
                    break
            except (ServerError, APIError, ClientError):
                continue
            except Exception as err:
                st.error(f"Error during generation: {err}")
                break

        if generated_text:
            # Save into session state so it persists across widget interactions!
            st.session_state["itinerary_response"] = generated_text
        else:
            st.error("Could not obtain itinerary due to server limits. Please try again shortly.")

# ----------------- DISPLAY WORKSPACE -----------------
# Render independently from button state so interactions never wipe the page
if st.session_state["itinerary_response"]:
    response_text = st.session_state["itinerary_response"]

    # Extract structured elevation points for Plotly
    elevation_data = []
    json_match = re.search(r"```json\s*(\[\s*\{.*?\}\s*\])\s*```", response_text, re.DOTALL)
    if json_match:
        try:
            elevation_data = json.loads(json_match.group(1))
        except Exception:
            elevation_data = []

    # Strip raw JSON from display text
    markdown_body = re.sub(r"```json\s*(\[\s*\{.*?\}\s*\])\s*```", "", response_text, flags=re.DOTALL).strip()

    st.success("Trek Itinerary & Logistics Prepared Successfully")

    # Metrics Summary Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Region", value=selected_region)
    with col2:
        st.metric(label="Duration", value=f"{trek_days} Days")
    with col3:
        staff_label = []
        if hire_guide:
            staff_label.append("Guide")
        if hire_porter:
            staff_label.append("Porter")
        st.metric(label="Support Staff", value=", ".join(staff_label) if staff_label else "Self-Guided")
    with col4:
        pdf_bytes = generate_pdf_itinerary(
            f"{selected_region} {trek_days}-Day Trek Itinerary",
            markdown_body
        )
        st.download_button(
            label="📄 Download PDF",
            data=pdf_bytes,
            file_name=f"{selected_region.lower()}_{trek_days}day_itinerary.pdf",
            mime="application/pdf",
            width="stretch"
        )

    st.divider()

    # Tabbed Interface
    tab_plan, tab_telemetry, tab_packing = st.tabs([
        "📋 Detailed Plan & Logistics",
        "📊 Trail Telemetry & Route Map",
        "🎒 Gear & Safety Checklist"
    ])

    with tab_plan:
        st.markdown(markdown_body)

    with tab_telemetry:
        st.subheader("High-Altitude Safety & Elevation Profile")
        if elevation_data:
            df_elevation = pd.DataFrame(elevation_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_elevation['day_label'],
                y=df_elevation['elevation_m'],
                mode='lines+markers',
                name='Sleeping Elevation',
                line=dict(color='#2E5B88', width=3),
                marker=dict(size=8, color='#1B4D3E')
            ))
            fig.add_hline(
                y=3000,
                line_dash="dash",
                line_color="red",
                annotation_text="3,000m AMS Risk Threshold",
                annotation_position="bottom right"
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                yaxis_title="Elevation (meters)",
                xaxis_tickangle=-45,
                height=420
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Elevation profile data unavailable for this route.")

        st.subheader("Interactive Trail Waypoints")
        trail_map = render_trail_map(selected_region)
        st_folium(trail_map, width=700, height=450)

    with tab_packing:
        st.info("Check items off as you prepare your rucksack.")
        checklist_items = [
            line.replace("- [ ]", "").replace("*", "").strip()
            for line in markdown_body.split("\n")
            if line.strip().startswith("- [ ]") or (line.strip().startswith("* ") and ("x" in line or "1x" in line or "2x" in line))
        ]

        if checklist_items:
            cols = st.columns(2)
            for i, item in enumerate(checklist_items):
                cols[i % 2].checkbox(item, key=f"pack_item_{i}")
        else:
            st.write("Full gear recommendations are listed in the Detailed Plan tab.")