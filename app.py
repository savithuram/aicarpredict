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

VEHDB_API_KEY = st.secrets.get(
    "VEHDB_API_KEY",
    os.getenv("VEHDB_API_KEY")
)

CARS_API = "https://api.vehdb.com/v1/cars"


# ============================================================
# VEHICLE API
# ============================================================

def get_cars(body_type, fuel_type, brand=""):
    """
    Fetch modern vehicles from VehDB.
    """

    if not VEHDB_API_KEY:
        return None, "VehDB API key not configured."

    headers = {
        "Authorization": f"Bearer {VEHDB_API_KEY}",
        "Accept": "application/json"
    }

    # VehDB requires at least one base filter.
    # We use year_min so that we get modern vehicles.
    params = {
    "year_min": 2023,
    "per_page": 10
    }

# VehDB requires a base filter.
# If the user entered a brand, use it.
if brand.strip():
    params["make"] = brand.strip()

# Otherwise use a broad search term.
else:
    params["q"] = "car"

    # Body type
    if body_type and body_type != "Any":
        params["body"] = body_type

    # Fuel type
    if fuel_type and fuel_type != "Any":
        if fuel_type == "Gas":
            params["fuel_type"] = "GASOLINE"

        elif fuel_type == "Diesel":
            params["fuel_type"] = "DIESEL"

        elif fuel_type == "Electric":
            params["fuel_type"] = "BATTERY ELECTRIC"

        elif fuel_type == "Hybrid":
            params["fuel_type"] = "HYBRID"

    # Brand/model
    

    try:

        response = requests.get(
            CARS_API,
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code == 200:

            result = response.json()

            # VehDB returns:
            # {
            #     "data": [...]
            # }

            cars = result.get("data", [])

            if isinstance(cars, list):
                return cars, None

            return [], None

        # API error
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

    year = car.get("year")

    try:
        return int(year)

    except (ValueError, TypeError):
        return 0


def clean_car_list(cars):

    if not cars:
        return []

    current_year = 2026

    cleaned = []

    seen = set()

    for car in cars:

        year = get_car_year(car)

        # Ignore old/invalid records
        if year < 2023:
            continue

        make = str(
            car.get("make", "")
        ).strip()

        model = str(
            car.get("model", "")
        ).strip()

        trim = str(
            car.get("trim", "")
        ).strip()

        identifier = (
            make.lower(),
            model.lower(),
            trim.lower(),
            year
        )

        if identifier in seen:
            continue

        seen.add(identifier)

        car["_year"] = year
        car["_age"] = current_year - year

        cleaned.append(car)

    # Newest first
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

    The score uses actual vehicle information
    returned by VehDB.
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

        reasons.append(
            "Very recent model"
        )

    elif year == 2025:

        score += 25

        reasons.append(
            "Recent model"
        )

    elif year == 2024:

        score += 20

        reasons.append(
            "Modern model"
        )

    elif year == 2023:

        score += 15

        reasons.append(
            "Recent production data"
        )


    # --------------------------------------------------------
    # BRAND MATCH
    # --------------------------------------------------------

    if preferred_brand.strip():

        preferred = preferred_brand.lower()

        if preferred in make:

            score += 30

            reasons.append(
                "Matches preferred brand"
            )

        elif preferred in model:

            score += 20

            reasons.append(
                "Matches preferred model"
            )

    else:

        score += 10

        reasons.append(
            "No brand restriction"
        )


    # --------------------------------------------------------
    # FUEL ECONOMY
    # --------------------------------------------------------

    mpg = car.get("mpg_combined")

    if mpg:

        score += 10

        reasons.append(
            "EPA fuel economy data available"
        )


    # --------------------------------------------------------
    # ELECTRIC RANGE
    # --------------------------------------------------------

    electric_range = car.get(
        "epa_range_miles"
    )

    if electric_range:

        score += 10

        reasons.append(
            "Electric driving range available"
        )


    # --------------------------------------------------------
    # DRIVE TYPE
    # --------------------------------------------------------

    drive = str(
        car.get("drive_type", "")
    ).upper()

    if drive in ["AWD", "4WD"]:

        score += 10

        reasons.append(
            "All-wheel/four-wheel drive"
        )


    # --------------------------------------------------------
    # ENGINE DATA
    # --------------------------------------------------------

    cylinders = car.get(
        "engine_cylinders"
    )

    if cylinders:

        score += 5

        reasons.append(
            "Engine specification available"
        )


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

    trim = str(
        car.get("trim", "")
    ).strip()

    year = get_car_year(car)

    body = car.get(
        "body",
        "N/A"
    )

    fuel = car.get(
        "fuel_type_name",
        "N/A"
    )

    drive = car.get(
        "drive_type",
        "N/A"
    )

    transmission = car.get(
        "transmission",
        "N/A"
    )

    cylinders = car.get(
        "engine_cylinders",
        "N/A"
    )

    mpg = car.get(
        "mpg_combined",
        "N/A"
    )

    electric_range = car.get(
        "epa_range_miles",
        "N/A"
    )

    annual_cost = car.get(
        "annual_fuel_cost",
        "N/A"
    )


    score, reasons = calculate_vehicle_score(
        car,
        preferred_brand,
        budget
    )


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    title = f"### 🏆 #{rank} — {year} {make} {model}"

    if trim:
        title += f" {trim}"

    st.markdown(title)


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

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
            "Body",
            body
        )


    with col4:

        st.metric(
            "Drive",
            drive
        )


    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.write(
            f"**Fuel:** {fuel}"
        )

        st.write(
            f"**Transmission:** {transmission}"
        )


    with col2:

        st.write(
            f"**Engine:** {cylinders} cylinders"
        )

        st.write(
            f"**Combined Mileage:** {mpg} MPG"
        )


    with col3:

        if electric_range != "N/A":

            st.write(
                f"**Electric Range:** "
                f"{electric_range} miles"
            )

        else:

            st.write(
                "**Electric Range:** N/A"
            )

        if annual_cost != "N/A":

            st.write(
                f"**Annual Fuel Cost:** "
                f"${annual_cost}"
            )

        else:

            st.write(
                "**Annual Fuel Cost:** N/A"
            )


    # --------------------------------------------------------
    # REASONS
    # --------------------------------------------------------

    st.write(
        "**Why this vehicle?**"
    )

    for reason in reasons[:4]:

        st.write(
            f"✓ {reason}"
        )

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
        "Data source:"
    )

    st.write(
        "🚗 VehDB Vehicle Database"
    )

    st.divider()

    st.info(
        "Vehicle recommendations are generated "
        "from real vehicle specifications returned "
        "by VehDB and transparent scoring rules."
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
            "💰 Maximum Budget (₹)",
            min_value=0,
            value=2500000,
            step=50000
        )


        body_type = st.selectbox(
            "🚗 Body Type",
            [
                "Any",
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
                "Diesel",
                "Electric",
                "Hybrid"
            ]
        )


        preferred_brand = st.text_input(
            "🏷️ Preferred Brand / Model",
            placeholder="BMW, Toyota, Honda..."
        )


        st.write("")

        st.caption(
            "Vehicle specifications are retrieved "
            "from VehDB."
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
            "Fetching vehicle data..."
        ):

            cars, error = get_cars(
                body_type,
                fuel_type,
                preferred_brand
            )


        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        if location.strip():

            st.success(
                f"📍 Target location: {location}"
            )


        # ----------------------------------------------------
        # API ERROR
        # ----------------------------------------------------

        if error:

            st.error(error)

            st.info(
                "Check that your VehDB API key is "
                "configured correctly in Streamlit Secrets."
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
                    "were retrieved and ranked using "
                    "vehicle specifications."
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
        "Explore the current vehicle landscape "
        "for a selected vehicle segment."
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
            "Collecting vehicle data..."
        ):

            segment_cars, error = get_cars(
                company_segment,
                "Any"
            )


        # ----------------------------------------------------
        # TARGET MARKET
        # ----------------------------------------------------

        st.subheader(
            "🌍 Target Market"
        )

        st.info(
            f"Analysis location: {company_location}"
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


            if segment_cars:

                st.subheader(
                    "📈 Current Vehicle Landscape"
                )


                # ------------------------------------------------
                # BASIC ANALYSIS
                # ------------------------------------------------

                total = len(segment_cars)

                brands = set()

                years = []

                fuel_types = set()

                drive_types = set()


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


                    fuel = car.get(
                        "fuel_type_name"
                    )

                    if fuel:

                        fuel_types.add(
                            str(fuel)
                        )


                    drive = car.get(
                        "drive_type"
                    )

                    if drive:

                        drive_types.add(
                            str(drive)
                        )


                newest_year = (
                    max(years)
                    if years
                    else "N/A"
                )


                # ------------------------------------------------
                # METRICS
                # ------------------------------------------------

                a, b, c, d = st.columns(4)


                with a:

                    st.metric(
                        "Vehicles Found",
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


                with d:

                    st.metric(
                        "Drive Types",
                        len(drive_types)
                    )


                # ------------------------------------------------
                # MANUFACTURERS
                # ------------------------------------------------

                st.write(
                    "**Manufacturers represented:**"
                )

                st.write(
                    ", ".join(
                        sorted(brands)
                    )
                )


                # ------------------------------------------------
                # FUEL TYPES
                # ------------------------------------------------

                st.write(
                    "**Fuel types represented:**"
                )

                st.write(
                    ", ".join(
                        sorted(fuel_types)
                    )
                )


                # ------------------------------------------------
                # EXAMPLE VEHICLES
                # ------------------------------------------------

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


                    trim = str(
                        car.get(
                            "trim",
                            ""
                        )
                    ).strip()


                    if trim:

                        st.write(
                            f"• **{year} {make} "
                            f"{model} {trim}**"
                        )

                    else:

                        st.write(
                            f"• **{year} {make} "
                            f"{model}**"
                        )


                # ------------------------------------------------
                # STRATEGIC INTERPRETATION
                # ------------------------------------------------

                st.subheader(
                    "💡 Strategic Interpretation"
                )


                st.write(
                    f"The database returned "
                    f"{total} modern {company_segment} "
                    f"records across "
                    f"{len(brands)} manufacturers."
                )


                st.write(
                    "This analysis describes the vehicle "
                    "landscape represented in the database. "
                    "It is not official sales or market-share data."
                )


                # ------------------------------------------------
                # OPPORTUNITY
                # ------------------------------------------------

                if len(brands) >= 10:

                    st.success(
                        f"💡 The {company_segment} segment "
                        f"has strong manufacturer representation. "
                        f"A new entrant should focus on "
                        f"differentiation in specifications, "
                        f"efficiency, technology or pricing."
                    )

                elif len(brands) >= 5:

                    st.success(
                        f"💡 The {company_segment} segment "
                        f"has moderate competition. "
                        f"There may be opportunities for "
                        f"a differentiated product."
                    )

                else:

                    st.success(
                        f"💡 The {company_segment} segment "
                        f"has relatively fewer manufacturers "
                        f"in the retrieved dataset."
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
    "AutoPulse uses VehDB vehicle data. "
    "Recommendations are data-driven scoring results "
    "and should not be treated as guaranteed predictions."
)
