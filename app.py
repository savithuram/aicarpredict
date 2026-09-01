import os
import requests
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AutoPulse",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 AutoPulse")
st.caption("Smart Automotive Recommendation & Market Analysis")


# ============================================================
# API CONFIGURATION
# ============================================================

API_KEY = st.secrets.get(
    "API_NINJAS_KEY",
    os.getenv("API_NINJAS_KEY")
)

CARS_API = "https://api.api-ninjas.com/v1/cars"
COUNTRIES_API = "https://api.restcountries.com/countries/v5"


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_country_data(location):
    location = location.strip()

    if not location:
        return None

    try:
        response = requests.get(
            f"{COUNTRIES_API}/names.common/{location}",
            timeout=10
        )

        if response.status_code != 200:
            return None

        result = response.json()

        data = result.get("data", {})

        countries = data.get("objects", [])

        if not countries:
            return None

        country = countries[0]

        names = country.get("names", {})
        name = names.get(
            "common",
            location.title()
        )

        population = country.get(
            "population",
            0
        )

        region = country.get(
            "region",
            "Unknown"
        )

        currencies = country.get(
            "currencies",
            []
        )

        currency_code = "USD"
        currency_symbol = "$"

        if currencies:
            currency = currencies[0]

            currency_code = currency.get(
                "code",
                "USD"
            )

            currency_symbol = currency.get(
                "symbol",
                currency_code
            )

        return {
            "name": name,
            "population": population,
            "region": region,
            "currency_code": currency_code,
            "currency_symbol": currency_symbol
        }

    except Exception:
        return None
# ============================================================
# CAR API
# ============================================================

def get_cars(body_type, fuel_type, brand=""):
    """
    Fetch modern vehicles from API Ninjas.
    """

    if not API_KEY:
        return None, "API key not configured."

    headers = {
        "X-Api-Key": API_KEY
    }

    # IMPORTANT:
    # The v1 API uses these parameter names.
    params = {
        "min_year": 2023,
    }

    # Brand/model search
    if brand.strip():
        params["make"] = brand.strip().lower()

    try:

        response = requests.get(
            CARS_API,
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code == 200:

            cars = response.json()

            if isinstance(cars, list):
                return cars, None

            return [], None

        # Show the actual API error
        try:
            error_data = response.json()
            return None, (
                f"API error {response.status_code}: "
                f"{error_data}"
            )
        except ValueError:
            return None, (
                f"API error {response.status_code}: "
                f"{response.text}"
            )

    except requests.RequestException as error:

        return None, f"Network error: {error}"
# ============================================================
# CLEAN CAR DATA
# ============================================================

def get_car_year(car):
    """
    Safely gets the vehicle year.
    """

    year = car.get("year")

    try:
        return int(year)
    except (ValueError, TypeError):
        return 0


def clean_car_list(cars):
    """
    Removes duplicate/old vehicles and sorts newest first.
    """

    if not cars:
        return []

    current_year = 2026

    cleaned = []

    seen = set()

    for car in cars:

        year = get_car_year(car)

        # Ignore obviously old / invalid records
        if year < 2023:
            continue

        make = str(car.get("make", "")).strip()
        model = str(car.get("model", "")).strip()

        identifier = (
            make.lower(),
            model.lower(),
            year
        )

        if identifier in seen:
            continue

        seen.add(identifier)

        car["_year"] = year
        car["_age"] = current_year - year

        cleaned.append(car)

    cleaned.sort(
        key=lambda x: x["_year"],
        reverse=True
    )

    return cleaned


# ============================================================
# VEHICLE SCORING
# ============================================================

def calculate_vehicle_score(
    car,
    preferred_brand,
    budget
):
    """
    Transparent recommendation score.

    This is NOT fake AI.
    The score is based on actual vehicle data.
    """

    score = 0
    reasons = []

    year = get_car_year(car)

    make = str(
        car.get("make", "")
    ).lower()

    model = str(
        car.get("model", "")
    ).lower()

    # --------------------------------------------------------
    # RECENCY
    # --------------------------------------------------------

    if year >= 2026:
        score += 30
        reasons.append("Very recent model")

    elif year == 2025:
        score += 25
        reasons.append("Recent model")

    elif year == 2024:
        score += 20
        reasons.append("Modern model")

    elif year == 2023:
        score += 15
        reasons.append("Recent production data")

    # --------------------------------------------------------
    # BRAND MATCH
    # --------------------------------------------------------

    if preferred_brand.strip():

        if preferred_brand.lower() in make:

            score += 30
            reasons.append("Matches preferred brand")

        elif preferred_brand.lower() in model:

            score += 20
            reasons.append("Matches preferred model")

    else:

        score += 10
        reasons.append("No brand restriction")

    # --------------------------------------------------------
    # SPECIFICATION BONUS
    # --------------------------------------------------------

    if car.get("transmission") == "a":
        score += 10
        reasons.append("Automatic transmission")

    if car.get("drive") in ["awd", "4wd"]:
        score += 10
        reasons.append("All-wheel/four-wheel drive")

    if car.get("fuel_type"):
        score += 5
        reasons.append("Fuel specification available")

    if car.get("city_mpg"):
        score += 5
        reasons.append("Mileage data available")

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

    score = min(score, 100)

    return score, reasons


# ============================================================
# DISPLAY VEHICLE
# ============================================================

def display_vehicle(
    car,
    rank,
    preferred_brand,
    budget
):

    make = str(
        car.get("make", "Unknown")
    ).title()

    model = str(
        car.get("model", "Unknown")
    ).title()

    year = get_car_year(car)

    transmission = car.get(
        "transmission",
        "N/A"
    )

    if transmission == "a":
        transmission = "Automatic"

    elif transmission == "m":
        transmission = "Manual"

    else:
        transmission = str(
            transmission
        ).upper()

    drive = str(
        car.get("drive", "N/A")
    ).upper()

    fuel = str(
        car.get("fuel_type", "N/A")
    ).title()

    cylinders = car.get(
        "cylinders",
        "N/A"
    )

    city_mpg = car.get(
        "city_mpg",
        "N/A"
    )

    score, reasons = calculate_vehicle_score(
        car,
        preferred_brand,
        budget
    )

    st.markdown(
        f"### 🏆 #{rank} — {year} {make} {model}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Recommendation Score",
            f"{score}/100"
        )

    with col2:
        st.metric(
            "Year",
            year
        )

    with col3:
        st.metric(
            "Fuel",
            fuel
        )

    with col4:
        st.metric(
            "Drive",
            drive
        )

    st.write(
        f"**Transmission:** {transmission}"
    )

    st.write(
        f"**Engine:** {cylinders} cylinders"
    )

    st.write(
        f"**City Mileage:** {city_mpg} MPG"
    )

    st.write("**Why this vehicle?**")

    for reason in reasons[:4]:
        st.write(f"✓ {reason}")

    st.divider()


# ============================================================
# CUSTOMER RECOMMENDATION
# ============================================================

def customer_recommendation(
    cars,
    preferred_brand,
    budget
):

    scored_cars = []

    for car in cars:

        score, reasons = calculate_vehicle_score(
            car,
            preferred_brand,
            budget
        )

        car["_score"] = score
        car["_reasons"] = reasons

        scored_cars.append(car)

    scored_cars.sort(
        key=lambda x: (
            x["_score"],
            x["_year"]
        ),
        reverse=True
    )

    return scored_cars


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ AutoPulse")

    st.write(
        "Data sources:"
    )

    st.write(
        "🌍 REST Countries"
    )

    st.write(
        "🚗 API Ninjas"
    )

    st.divider()

    st.info(
        "Vehicle recommendations are generated "
        "from retrieved vehicle specifications "
        "and transparent scoring rules."
    )


# ============================================================
# TABS
# ============================================================

customer_tab, company_tab = st.tabs(
    [
        "👤 Customer Portal",
        "🏢 Manufacturer Portal"
    ]
)


# ============================================================
# CUSTOMER PORTAL
# ============================================================

with customer_tab:

    st.header(
        "Find Your Ideal Vehicle"
    )

    st.write(
        "Enter your preferences and AutoPulse "
        "will retrieve modern vehicles and rank "
        "them using their actual specifications."
    )

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # LEFT
    # --------------------------------------------------------

    with col1:

        location = st.text_input(
            "🌍 Country",
            value="India"
        )

        budget = st.number_input(
            "💰 Maximum Budget",
            min_value=0,
            value=2500000,
            step=50000
        )

        body_type = st.selectbox(
            "🚗 Body Type",
            [
                "SUV",
                "Sedan",
                "Hatchback",
                "Coupe"
            ]
        )

    # --------------------------------------------------------
    # RIGHT
    # --------------------------------------------------------

    with col2:

        fuel_type = st.selectbox(
            "⛽ Fuel Type",
            [
                "Any",
                "Gas",
                "Diesel"
            ]
        )

        preferred_brand = st.text_input(
            "🏷️ Preferred Brand / Model",
            placeholder="BMW, Toyota, Honda..."
        )

        st.write("")

        st.caption(
            "The vehicle database determines "
            "which models are available."
        )

    # --------------------------------------------------------
    # BUTTON
    # --------------------------------------------------------

    if st.button(
        "🔍 Find Best Vehicles",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Fetching current vehicle data..."
        ):

            location_data = get_country_data(
                location
            )

            cars, error = get_cars(
                body_type,
                fuel_type,
                preferred_brand
            )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        if location_data:

            st.success(
                f"Location detected: "
                f"{location_data['name']}"
            )

            a, b, c = st.columns(3)

            with a:
                st.metric(
                    "Population",
                    f"{location_data['population']:,}"
                )

            with b:
                st.metric(
                    "Region",
                    location_data["region"]
                )

            with c:
                st.metric(
                    "Currency",
                    location_data["currency_code"]
                )

        else:

            st.warning(
                "Could not find this country. "
                "Vehicle search will still continue."
            )

        # ----------------------------------------------------
        # API ERROR
        # ----------------------------------------------------

        if error:

            st.error(error)

            st.info(
                "Check that your API key is configured "
                "correctly."
            )

        # ----------------------------------------------------
        # VEHICLES
        # ----------------------------------------------------

        elif cars:

            cars = clean_car_list(cars)

            if not cars:

                st.warning(
                    "The API returned vehicles, but "
                    "none matched our modern-vehicle filter."
                )

            else:

                ranked_cars = customer_recommendation(
                    cars,
                    preferred_brand,
                    budget
                )

                st.subheader(
                    "🚗 Recommended Vehicles"
                )

                st.caption(
                    f"{len(ranked_cars)} modern vehicles "
                    "were retrieved and ranked."
                )

                for i, car in enumerate(
                    ranked_cars[:5],
                    start=1
                ):

                    display_vehicle(
                        car,
                        i,
                        preferred_brand,
                        budget
                    )

        else:

            st.warning(
                "No matching vehicles were found."
            )

            st.write(
                "Try removing the brand/model filter "
                "or selecting another body type."
            )


# ============================================================
# MANUFACTURER PORTAL
# ============================================================

with company_tab:

    st.header(
        "🏢 Manufacturer Opportunity Analyzer"
    )

    st.write(
        "Use current vehicle data to explore "
        "which vehicle segment has the strongest "
        "available product coverage."
    )

    col1, col2 = st.columns(2)

    with col1:

        company_location = st.text_input(
            "🌍 Target Country",
            value="Germany",
            key="company_location"
        )

    with col2:

        company_segment = st.selectbox(
            "🚗 Target Vehicle Segment",
            [
                "SUV",
                "Sedan",
                "Hatchback",
                "Coupe"
            ],
            key="company_segment"
        )

    if st.button(
        "📊 Analyze Opportunity",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Collecting market and vehicle data..."
        ):

            country_data = get_country_data(
                company_location
            )

            segment_cars, error = get_cars(
                company_segment,
                "Any"
            )

        # ----------------------------------------------------
        # COUNTRY INFORMATION
        # ----------------------------------------------------

        if country_data:

            st.subheader(
                "🌍 Target Market"
            )

            a, b, c = st.columns(3)

            with a:

                st.metric(
                    "Country",
                    country_data["name"]
                )

            with b:

                st.metric(
                    "Population",
                    f"{country_data['population']:,}"
                )

            with c:

                st.metric(
                    "Region",
                    country_data["region"]
                )

        # ----------------------------------------------------
        # API ERROR
        # ----------------------------------------------------

        if error:

            st.error(error)

        elif segment_cars:

            segment_cars = clean_car_list(
                segment_cars
            )

            st.subheader(
                "📈 Current Vehicle Landscape"
            )

            if segment_cars:

                # ------------------------------------------------
                # BASIC ANALYSIS
                # ------------------------------------------------

                total = len(segment_cars)

                brands = set()

                years = []

                for car in segment_cars:

                    make = car.get(
                        "make"
                    )

                    if make:
                        brands.add(
                            str(make).title()
                        )

                    year = get_car_year(
                        car
                    )

                    if year:
                        years.append(
                            year
                        )

                newest_year = (
                    max(years)
                    if years
                    else "N/A"
                )

                # ------------------------------------------------
                # METRICS
                # ------------------------------------------------

                a, b, c = st.columns(3)

                with a:

                    st.metric(
                        "Modern Vehicles Found",
                        total
                    )

                with b:

                    st.metric(
                        "Manufacturers",
                        len(brands)
                    )

                with c:

                    st.metric(
                        "Newest Model Year",
                        newest_year
                    )

                # ------------------------------------------------
                # BRAND LIST
                # ------------------------------------------------

                st.write(
                    "**Manufacturers represented:**"
                )

                st.write(
                    ", ".join(
                        sorted(brands)
                    )
                )

                st.subheader(
                    "🔎 Example Vehicles"
                )

                for car in segment_cars[:5]:

                    make = str(
                        car.get(
                            "make",
                            "Unknown"
                        )
                    ).title()

                    model = str(
                        car.get(
                            "model",
                            "Unknown"
                        )
                    ).title()

                    year = get_car_year(
                        car
                    )

                    st.write(
                        f"• **{year} {make} {model}**"
                    )

                # ------------------------------------------------
                # OPPORTUNITY EXPLANATION
                # ------------------------------------------------

                st.subheader(
                    "💡 Strategic Interpretation"
                )

                st.write(
                    f"The API returned {total} "
                    f"modern {company_segment} records "
                    f"across {len(brands)} manufacturers."
                )

                st.write(
                    "This does not claim to be official "
                    "sales-market-share data. Instead, "
                    "it describes the current vehicle "
                    "landscape available through the API."
                )

                st.success(
                    f"Potential research direction: "
                    f"investigate differentiation opportunities "
                    f"within the {company_segment} segment."
                )

            else:

                st.warning(
                    "No modern vehicles were found "
                    "for this segment."
                )

        else:

            st.warning(
                "No vehicle data was returned."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AutoPulse uses external APIs for vehicle and "
    "country information. Recommendations are "
    "data-driven scoring results, not guaranteed predictions."
)
