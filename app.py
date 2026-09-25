import os
import time
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
st.caption("Autonomous trekking assistant with real-time permit checks and altitude safety validation.")

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

# Main Output
if generate_btn:
    with st.spinner("Agent is consulting permit fees, verifying route safety, and drafting itinerary..."):
        prompt = (
            f"Plan a realistic {trek_days}-day trekking itinerary for the {selected_region} region in Nepal "
            f"for a person with '{fitness_level}' fitness level. "
            f"You MUST use your custom tools: 'get_nepal_trek_permit' to check the exact permit fees, "
            f"and 'check_altitude_safety' to verify that no single day's elevation gain exceeds safe limits above 3,000m. "
            f"Provide the final itinerary in a clean table format with daily distances, starting altitude, "
            f"ending altitude, and permit fee breakdown in NPR."
        )

        # Primary and backup model pool to handle 503 capacity spikes
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
                break  # Successful response obtained
            except ServerError as e:
                # If Google's server is busy, wait briefly and try next model
                time.sleep(1)
                continue
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                break

        if response_text:
            st.success("Itinerary Generated Successfully!")
            st.markdown(response_text)
        else:
            st.warning("Google's servers are experiencing peak global traffic. Click 'Generate Safe Itinerary' again in 5 seconds.")