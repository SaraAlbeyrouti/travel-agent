import streamlit as st
from agent import plan_trip

st.set_page_config(page_title="✈️ Travel Planner Agent", layout="centered")

st.title("✈️ Travel Planner Agent")
st.markdown("Tell me where you want to go and I'll build your perfect itinerary.")

with st.form("travel_form"):
    destination  = st.text_input("Destination", placeholder="e.g. Lisbon, Portugal")
    num_days     = st.slider("Number of days", 2, 14, 5)
    budget_level = st.selectbox("Budget level", ["budget", "mid", "luxury"])
    vibe         = st.text_input("Travel vibe", placeholder="e.g. relaxing beach, cultural, adventure")
    submitted    = st.form_submit_button("Plan my trip 🗺️")

if submitted:
    if not destination:
        st.warning("Please enter a destination!")
    else:
        with st.spinner("Your agent is planning your trip..."):
            result = plan_trip(destination, num_days, budget_level, vibe)
        st.success("Here's your itinerary!")
        st.markdown(result)