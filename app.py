import os
import re
import json
import time
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from tools.permits import get_nepal_trek_permit
from tools.altitude import check_altitude_safety

load_dotenv()

st.set_page_config(
    page_title="Nepal Trek AI Planner",
    page_icon="🏔️",
    layout="wide"
)

st.title("🏔️ Nepal Himalayan Trekking AI Agent")
st.caption("Autonomous trekking assistant with real-time permit checks, altitude safety validation, and elevation telemetry.")

# Initialize Gemini Client
@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

client = get_gemini_client()

# Sidebar Configuration
with st.sidebar:
    st.header("Trek Configuration")
    selected_region = st.selectbox(
        "Choose Trekking Region",
        ["Annapurna", "Everest", "Langtang", "Manaslu"]
    )
    trek_days = st.slider("Trip Duration (Days)", min_value=3, max_value=21, value=7)
    fitness_level = st.select_slider(
        "Fitness Level",
        options=["Beginner", "Moderate", "Experienced", "High Altitude Veteran"]
    )
    generate_btn = st.button("Generate Safe Itinerary", type="primary", use_container_width=True)


def plot_altitude_chart(profile_data):
    """Renders an interactive Plotly elevation profile with AMS safety thresholds."""
    df = pd.DataFrame(profile_data)
    
    fig = go.Figure()

    # Elevation trendline
    fig.add_trace(go.Scatter(
        x=df["day_label"],
        y=df["elevation_m"],
        mode="lines+markers+text",
        name="Daily Sleeping Elevation",
        line=dict(color="#2ca02c", width=3),
        marker=dict(size=10, color="#1f77b4"),
        text=df["elevation_m"].apply(lambda x: f"{x}m"),
        textposition="top center"
    ))

    # 3,000m AMS Threshold Line
    fig.add_hline(
        y=3000,
        line_dash="dash",
        line_color="#d62728",
        annotation_text="3,000m AMS Risk Threshold (Max +500m/day sleep rule applies)",
        annotation_position="bottom right"
    )

    fig.update_layout(
        title="Interactive Elevation Profile & AMS Monitoring",
        xaxis_title="Trek Schedule / Route",
        yaxis_title="Sleeping Elevation (Meters)",
        hovermode="x unified",
        template="plotly_white",
        height=420
    )
    return fig


# Main App Flow
if generate_btn:
    with st.spinner("Agent is consulting permit fees, verifying route safety, and calculating elevation curves..."):
        prompt = (
            f"Plan a realistic {trek_days}-day trekking itinerary for the {selected_region} region in Nepal "
            f"for a person with '{fitness_level}' fitness level.\n"
            f"You MUST use your custom tools: 'get_nepal_trek_permit' to check the exact permit fees, "
            f"and 'check_altitude_safety' to verify that no single day's elevation gain exceeds safe limits above 3,000m.\n"
            f"Provide the complete final itinerary in markdown format with permit breakdown.\n\n"
            f"IMPORTANT: At the very end of your response, output a raw JSON block enclosed in ```json ``` "
            f"containing an array of objects for the elevation graph with keys: "
            f"'day_label' (e.g. 'Day 1: Pokhara to Hile') and 'elevation_m' (integer sleeping altitude in meters)."
        )

        candidate_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
        response_text = None

        for model_name in candidate_models:
            try:
                chat = client.chats.create(
                    model=model_name,
                    config={
                        "tools": [get_nepal_trek_permit, check_altitude_safety]
                    }
                )
                response = chat.send_message(prompt)
                response_text = response.text
                break
            except ServerError:
                time.sleep(1)
                continue
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                break

        if response_text:
            # Extract JSON block for the altitude graph
            json_match = re.search(r"```json\s*(\[.*?\])\s*```", response_text, re.DOTALL)
            markdown_content = re.sub(r"```json\s*(\[.*?\])\s*```", "", response_text, flags=re.DOTALL)

            # Display Itinerary
            st.success("Itinerary Generated Successfully!")
            st.markdown(markdown_content)

            # Render Chart if JSON was extracted
            if json_match:
                try:
                    profile_data = json.loads(json_match.group(1))
                    st.divider()
                    st.subheader("📊 Elevation & High-Altitude Safety Profile")
                    fig = plot_altitude_chart(profile_data)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as err:
                    st.warning(f"Could not parse telemetry graph: {err}")
        else:
            st.warning("Google's servers are experiencing temporary peak traffic. Please click Generate again.")