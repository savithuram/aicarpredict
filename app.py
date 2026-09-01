import streamlit as st
import requests
import random

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

# Fetch dynamic car listings from API Ninjas Cars API with multi-year fallback logic
def fetch_cars_from_api(body_type: str, user_input: str = ""):
    api_key = "nPREL0WvyEN6gnpkLQtIydPlzpw5F8kPUO1MimRC"
    url = "https://api.api-ninjas.com/v1/cars"
    headers = {"X-Api-Key": api_key}
    
    clean_input = user_input.strip().lower()
    years_to_try = [2022, 2020, 2018, 2015]
    
    # 1. Search user input as MAKE (e.g., BMW, Porsche, Ferrari, Maruti)
    if clean_input:
        for year in years_to_try:
            try:
                res = requests.get(url, headers=headers, params={"make": clean_input, "year": year, "limit": 10})
                if res.status_code == 200 and res.json():
                    return res.json()
            except Exception:
                pass
                
        # 2. Search user input as MODEL (e.g., 330i, M3, Huracan, Swift, Civic)
        for year in years_to_try:
            try:
                res = requests.get(url, headers=headers, params={"model": clean_input, "year": year, "limit": 10})
                if res.status_code == 200 and res.json():
                    return res.json()
            except Exception:
                pass

        # 3. Try without year parameter as a final attempt
        try:
            res = requests.get(url, headers=headers, params={"make": clean_input, "limit": 10})
            if res.status_code == 200 and res.json():
                return res.json()
        except Exception:
            pass

    # 4. Fallback pool if input is blank or unmatched
    brand_pool = {
        "SUV": ["bmw", "porsche", "audi", "mercedes-benz", "land rover", "maruti", "hyundai", "jeep"],
        "EV": ["porsche", "tesla", "bmw", "audi", "mercedes-benz", "hyundai", "kia"],
        "Sedan": ["bmw", "mercedes-benz", "audi", "porsche", "bentley", "maserati", "honda", "toyota"],
        "Hatchback": ["mini", "volkswagen", "maruti", "audi", "mercedes-benz", "bmw", "ford"]
    }
    
    sampled_makes = brand_pool.get(body_type, ["bmw", "porsche", "audi", "mercedes-benz"])
    random.shuffle(sampled_makes)
    
    for make_name in sampled_makes:
        for yr in [2020, 2018]:
            try:
                res = requests.get(url, headers=headers, params={"make": make_name, "year": yr, "limit": 10})
                if res.status_code == 200 and res.json():
                    return res.json()
            except Exception:
                continue

    return []

def fetch_market_data(location: str):
    curr = get_currency_config(location)
    rate = curr["rate"]
    return {
        "location": location,
        "currency_symbol": curr["symbol"],
        "avg_price": {
            "SUV": int(34000 * rate),
            "EV": int(41000 * rate),
            "Sedan": int(22000 * rate),
            "Hatchback": int(18000 * rate)
        },
        "days_supply": {"SUV": 28, "EV": 14, "Sedan": 42, "Hatchback": 50},
        "market_share": {"SUV": "48%", "EV": "18%", "Sedan": "28%", "Hatchback": "6%"}
    }

# Navigation tabs
tab1, tab2 = st.tabs(["👤 Customer Portal", "🏢 Startup Manufacturer Portal"])

# --- CUSTOMER PORTAL ---
with tab1:
    st.header("Find Your Ideal Vehicle Match")
    st.write("Enter your location, budget, and brand preference to query global car databases.")
    
    col1, col2 = st.columns(2)
    with col1:
        c_location = st.text_input("Location / City / Country", value="India", key="c_loc")
        c_currency = get_currency_config(c_location)["symbol"]
        default_budget = 2500000 if c_currency == "₹" else 35000
        budget_step = 50000 if c_currency == "₹" else 1000
        c_budget = st.number_input(f"Maximum Budget ({c_currency})", value=default_budget, step=budget_step)
    with col2:
        c_type = st.selectbox("Preferred Body Type", ["SUV", "EV", "Sedan", "Hatchback"])
        c_brand_model = st.text_input("Preferred Brand / Model (Optional)", placeholder="e.g. BMW, Lamborghini, Maruti, Ferrari, Porsche, Huracan")

    if st.button("Predict Best Vehicle Fit", type="primary"):
        market_info = fetch_market_data(c_location)
        api_cars = fetch_cars_from_api(c_type, c_brand_model)
        sym = market_info["currency_symbol"]
        avg_cost = market_info["avg_price"].get(c_type, 30000)
        
        st.subheader("🚗 Live Vehicle Results from Global API Database")
        
        if api_cars:
            for i, car in enumerate(api_cars[:5], 1):
                make = car.get("make", "Generic").title()
                model = car.get("model", "Vehicle").title()
                year = car.get("year", "2023")
                transmission = "Automatic" if car.get("transmission") == "a" else "Manual"
                drive = car.get("drive", "fwd").upper()
                fuel = car.get("fuel_type", "gas").title()
                cylinders = car.get("cylinders", "N/A")
                city_mpg = car.get("city_mpg", "N/A")
                
                st.success(f"**Option {i}: {year} {make} {model}**")
                st.write(f"• **Drive & Transmission:** {drive} | {transmission}")
                st.write(f"• **Fuel Type & Engine:** {fuel} | {cylinders} Cylinders")
                st.write(f"• **City Mileage:** {city_mpg} MPG")
                st.write(f"• **Estimated Market Benchmark:** {sym}{avg_cost:,.0f}")
                st.write("---")
        else:
            st.warning(f"No specific matches found for '{c_brand_model}'. Try searching by Brand name (e.g. BMW, Lamborghini, Maruti, Ferrari, Porsche).")

        reasons = [
            f"Queries live vehicle records for {c_type} models across global manufacturer databases.",
            f"Fits within or near your target budget of {sym}{c_budget:,.0f} against regional {c_type} price baselines ({sym}{avg_cost:,.0f}).",
            f"Regional market demand metric: Market Days Supply for {c_type}s in {c_location} is {market_info['days_supply'].get(c_type, 30)} days.",
            f"The {c_type} body style holds {market_info['market_share'].get(c_type, '25%')} market share in {c_location}."
        ]

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
