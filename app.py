import streamlit as st
import requests

st.set_page_config(page_title="AutoPulse Analytics", page_icon="🚗", layout="wide")

st.title("🚗 AutoPulse: Real-Time Auto Intelligence")
st.caption("API-Driven Automotive Recommendation Engine")

# Auto-detect local currency symbol and rate modifier based on location
def get_currency_config(location: str):
    loc = location.lower().strip()
    if any(k in loc for k in ["india", "mumbai", "delhi", "bangalore", "chennai", "hyderabad", "pune", "kolkata"]):
        return {"symbol": "₹", "rate": 83.0}
    elif any(k in loc for k in ["uk", "london", "manchester", "gb", "england", "united kingdom"]):
        return {"symbol": "£", "rate": 0.79}
    elif any(k in loc for k in ["europe", "germany", "france", "berlin", "paris", "spain", "italy", "eu"]):
        return {"symbol": "€", "rate": 0.92}
    else:
        return {"symbol": "$", "rate": 1.0}

# Fetch market data (Integration point for real-time APIs like MarketCheck or CarAPI)
def fetch_market_data(location: str):
    curr = get_currency_config(location)
    rate = curr["rate"]
    loc = location.lower().strip()
    
    # Scale base price benchmarks to local currency
    base_prices = {"SUV": 34000, "Sedan": 22000, "EV": 41000, "Hatchback": 18000}
    local_prices = {k: int(v * rate) for k, v in base_prices.items()}
    
    return {
        "location": location,
        "currency_symbol": curr["symbol"],
        "available_units": 1850 if any(term in loc for term in ["york", "ny", "london", "mumbai", "delhi"]) else 920,
        "avg_price": local_prices,
        "days_supply": {"SUV": 28, "Sedan": 42, "EV": 14, "Hatchback": 50},
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
        c_location = st.text_input("Location / City / Country", value="India", key="c_loc")
        c_currency = get_currency_config(c_location)["symbol"]
        default_budget = 2500000 if c_currency == "₹" else 35000
        budget_step = 50000 if c_currency == "₹" else 1000
        c_budget = st.number_input(f"Maximum Budget ({c_currency})", value=default_budget, step=budget_step)
    with col2:
        c_type = st.selectbox("Preferred Body Type", ["SUV", "EV", "Sedan", "Hatchback"])
        c_model = st.text_input("Preferred Model (Optional)", placeholder="e.g. RAV4, Model Y, Nexon")

    if st.button("Predict Best Vehicle Fit", type="primary"):
        data = fetch_market_data(c_location)
        sym = data["currency_symbol"]
        avg_cost = data["avg_price"].get(c_type, 30000)
        
        # Recommendation logic consuming currency-scaled parameters
        if c_type == "EV" and c_budget >= (30000 * get_currency_config(c_location)["rate"]):
            rec_car = "Tesla Model Y / Hyundai Ioniq 5 / Tata Nexon EV"
            match_score = "95%"
            reasons = [
                f"High demand turnover in {c_location}: Market Days Supply is down to {data['days_supply']['EV']} days.",
                f"Your budget ({sym}{c_budget:,.0f}) comfortably covers regional EV price averages ({sym}{avg_cost:,.0f}).",
                "High density of local public charging infrastructure in your region."
            ]
        elif c_type == "SUV" and c_budget >= (22000 * get_currency_config(c_location)["rate"]):
            rec_car = "Toyota RAV4 / Mazda CX-5 / Hyundai Creta"
            match_score = "92%"
            reasons = [
                f"SUVs command {data['market_share']['SUV']} of active buyer market share in {c_location}.",
                f"Fits within regional price average ({sym}{avg_cost:,.0f}) with strong dealer inventory.",
                "High liquidity for resale and optimal local road compatibility."
            ]
        else:
            rec_car = "Honda Civic / Toyota Corolla / Maruti Swift"
            match_score = "89%"
            reasons = [
                f"Optimal utility-to-cost ratio for your {sym}{c_budget:,.0f} budget limit.",
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
    
    s_location = st.text_input("Target Region / City", value="India", key="s_loc")
    
    if st.button("Analyze Market Opportunities", type="primary"):
        s_data = fetch_market_data(s_location)
        s_sym = s_data["currency_symbol"]
        avg_ev = s_data["avg_price"]["EV"]
        
        target_sub_price = int(32000 * get_currency_config(s_location)["rate"])
        rec_segment = f"Compact Electric SUV (Sub-{s_sym}{target_sub_price:,.0f})"
        success_rate = "88%"
        reasons = [
            f"**High Supply Deficit:** EV Market Days Supply in {s_location} is low ({s_data['days_supply']['EV']} days), meaning consumer purchases outpace dealer stock.",
            f"**Price Vacuum:** Regional average EV price is high ({s_sym}{avg_ev:,.0f}), leaving a wide opening for an affordable entry competitor.",
            f"**Body Style Dominance:** SUV body styles lead sales with {s_data['market_share']['SUV']} share, making a Compact EV SUV the highest probability entry model."
        ]

        st.info(f"**Recommended Launch Vehicle:** {rec_segment}")
        st.metric(label="Projected Success Rate", value=success_rate)
        
        st.subheader("📊 Strategic Rationale")
        for r in reasons:
            st.markdown(f"- {r}")
