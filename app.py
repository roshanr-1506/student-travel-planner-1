import streamlit as st
import random

st.set_page_config(page_title="Wayfare Travel Planner", layout="wide")

# ---------------------------
# DESTINATION DATA (same)
# ---------------------------
DESTINATIONS = {
    "goa": {
        "label": "Goa",
        "stay": 900,
        "food": 200,
        "transport": 200,
        "activities": [
            {"name": "Beach visit", "cost": 0},
            {"name": "Parasailing", "cost": 1200},
            {"name": "Market visit", "cost": 200}
        ]
    },
    "manali": {
        "label": "Manali",
        "stay": 800,
        "food": 180,
        "transport": 300,
        "activities": [
            {"name": "Temple visit", "cost": 0},
            {"name": "Paragliding", "cost": 2200},
            {"name": "Cafe hopping", "cost": 300}
        ]
    }
}

def get_destination(name):
    name = name.lower()
    for key in DESTINATIONS:
        if key in name:
            return DESTINATIONS[key]
    return DESTINATIONS["goa"]

# ---------------------------
# UI
# ---------------------------
st.title("✈️ Wayfare — Student Travel Planner")

col1, col2 = st.columns(2)

with col1:
    destination = st.text_input("Destination", "Goa")
    origin = st.text_input("Traveling from", "Delhi")
    days = st.slider("Trip length (days)", 1, 14, 4)

with col2:
    travelers = st.slider("Number of travelers", 1, 10, 2)
    budget = st.number_input("Total Budget (₹)", min_value=500, value=10000)

generate = st.button("Generate Itinerary")

# ---------------------------
# GENERATE LOGIC
# ---------------------------
if generate:
    dest = get_destination(destination)

    st.subheader(f"{origin} → {dest['label']}")

    for d in range(1, days + 1):
        st.markdown(f"### Day {d}")

        total_cost = 0

        for time in ["Morning", "Afternoon", "Evening"]:
            act = random.choice(dest["activities"])
            st.write(f"**{time}:** {act['name']} (₹{act['cost']})")
            total_cost += act["cost"]

        total_cost += dest["stay"] + dest["food"] * 2 + dest["transport"]

        st.info(f"Estimated cost: ₹{total_cost * travelers}")
        st.divider()
