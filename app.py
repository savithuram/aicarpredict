import streamlit as st
import requests

st.set_page_config(page_title="AutoPulse Analytics", page_icon="🚗", layout="wide")

st.title("🚗 AutoPulse: Real-Time Auto Intelligence")
st.caption("API-Driven Automotive Recommendation Engine")

# Fetch market data from external API endpoint
def fetch_market_data(location: str):
    # API Integration Point: Replace mock dict with MarketCheck or CarAPI request:
    # response = requests.get(f"https://api.marketcheck.com/v2/search/car/active?zip={location}&api_key=YOUR_KEY")
    # return response.json()
    
    loc = location.lower().strip()
    return {
        "location": location,
        "available_units": 1850 if "york" in loc or "ny" in loc else 920,
        "avg_price": {"SUV": 34000, "Sedan": 22000, "EV": 41000, "Hatchback": 18000},
        "days_supply": {"SUV": 28, "Sedan": 42, "EV": 14, "Hatchback": 50},  # Lower = Higher demand
        "market_share": {"SUV": "48%", "Sedan": "28%", "EV": "18%", "Hatchback": "6%"}
    }

# Navigation tabs
tab1, tab2 = st.tabs(["👤 Customer Portal", "🏢 Startup Manufacturer Portal"])

# --- CUSTOMER PORTAL ---
with tab1:
    st.header("Find Your Ideal Vehicle Match")
    st.write("Enter your location and target budget to query real-time market inventory.")
    
    col1, col2 = st.columns(2)
    with col1:
        c_location = st.text_input("Location / ZIP Code", value="New York, NY", key="c_loc")
        c_budget = st.number_input("Maximum Budget ($)", value=35000, step=1000)
    with col2:
        c_type = st.selectbox("Preferred Body Type", ["SUV", "EV", "Sedan", "Hatchback"])
        c_model = st.text_input("Preferred Model (Optional)", placeholder="e.g. RAV4, Model Y")

    if st.button("Predict Best Vehicle Fit", type="primary"):
        data = fetch_market_data(c_location)
        avg_cost = data["avg_price"].get(c_type, 30000)
        
        # Rule-based logic consuming API metrics
        if c_type == "EV" and c_budget >= 35000:
            rec_car = "Tesla Model Y / Hyundai Ioniq 5"
            match_score = "95%"
            reasons = [
                f"High demand turnover in {c_location}: Market Days Supply is down to {data['days_supply']['EV']} days.",
                f"Your budget (\${c_budget:,.0f}) comfortably covers regional EV price averages (${avg_cost:,.0f}).",
                "High density of local public charging infrastructure in your city."
            ]
        elif c_type == "SUV" and c_budget >= 28000:
            rec_car = "Toyota RAV4 / Mazda CX-5"
            match_score = "92%"
            reasons = [
                f"SUVs command {data['market_share']['SUV']} of active buyer market share in {c_location}.",
                f"Fits within regional price average (${avg_cost:,.0f}) with strong dealer inventory.",
                "High liquidity for resale and optimal local road compatibility."
            ]
        else:
            rec_car = "Honda Civic / Toyota Corolla"
            match_score = "89%"
            reasons = [
                f"Optimal utility-to-cost ratio for your ${c_budget:,.0f} budget limit.",
                "Strong dealer availability ensures competitive pricing and immediate delivery.",
                "Low average operational and maintenance costs in this region."
            ]

        st.success(f"**Recommended Vehicle:** {rec_car}")
        st.metric(label="Match Confidence", value=match_score)
        
        st.subheader("💡 Why This Was Predicted")
        for r in reasons:
            st.markdown(f"- {r}")

# --- STARTUP CAR COMPANY PORTAL ---
with tab2:
    st.header("Regional Opportunity & Market Gap Analyzer")
    st.write("Analyze target locations to identify underserved automotive market segments.")
    
    s_location = st.text_input("Target Region / City", value="Chicago, IL", key="s_loc")
    
    if st.button("Analyze Market Opportunities", type="primary"):
        s_data = fetch_market_data(s_location)
        
        rec_segment = "Compact Electric SUV (Sub-$32,000)"
        success_rate = "88%"
        reasons = [
            f"**High Supply Deficit:** EV Market Days Supply in {s_location} is low ({s_data['days_supply']['EV']} days), meaning consumer purchases outpace dealer stock.",
            f"**Price Vacuum:** Regional average EV price is high (\${s_data['avg_price']['EV']:,.0f}), leaving a wide opening for an affordable sub-$32k competitor.",
            f"**Body Style Dominance:** SUV body styles lead sales with {s_data['market_share']['SUV']} share, making a Compact EV SUV the highest probability entry model."
        ]

        st.info(f"**Recommended Launch Vehicle:** {rec_segment}")
        st.metric(label="Projected Success Rate", value=success_rate)
        
        st.subheader("📊 Strategic Rationale")
        for r in reasons:
            st.markdown(f"- {r}")
