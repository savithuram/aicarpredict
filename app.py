# Fetch dynamic car listings from API Ninjas Cars API across all global makes & models
def fetch_cars_from_api(body_type: str, user_input: str = ""):
    api_key = "nPREL0WvyEN6gnpkLQtIydPlzpw5F8kPUO1MimRC"
    url = "https://api.api-ninjas.com/v1/cars"
    headers = {"X-Api-Key": api_key}

    clean_input = user_input.strip().lower()

    if clean_input:
        # 1. Try searching by MAKE
        try:
            res = requests.get(
                url, headers=headers, params={"make": clean_input}
            )
            if res.status_code == 200 and res.json():
                return res.json()
            elif res.status_code != 200:
                st.error(f"API Error ({res.status_code}): {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

        # 2. Try searching by MODEL
        try:
            res = requests.get(
                url, headers=headers, params={"model": clean_input}
            )
            if res.status_code == 200 and res.json():
                return res.json()
        except Exception:
            pass

    # Fallback brand pool
    brand_pool = {
        "SUV": [
            "toyota", "honda", "ford", "chevrolet", "jeep", "nissan", "hyundai",
            "kia", "subaru", "mazda", "bmw", "mercedes-benz", "audi", "porsche",
            "land rover", "volvo", "lexus", "acura", "infiniti", "cadillac",
            "gmc", "lincoln", "dodge", "maruti", "tata", "mahindra",
            "lamborghini", "ferrari", "bentley", "aston martin", "maserati",
            "volkswagen", "alfa romeo", "mitsubishi"
        ],
        "EV": [
            "tesla", "porsche", "bmw", "audi", "mercedes-benz", "hyundai", "kia",
            "nissan", "volkswagen", "polestar", "lucid", "rivian", "byd", "ford",
            "chevrolet", "volvo", "cadillac", "jaguar", "genesis", "fiat", "tata"
        ],
        "Sedan": [
            "toyota", "honda", "nissan", "hyundai", "kia", "bmw",
            "mercedes-benz", "audi", "lexus", "volkswagen", "subaru", "mazda",
            "volvo", "genesis", "cadillac", "jaguar", "alfa romeo", "porsche",
            "maserati", "bentley", "rolls-royce", "dodge", "chrysler", "maruti",
            "tata", "aston martin"
        ],
        "Hatchback": [
            "volkswagen", "mini", "honda", "toyota", "maruti", "hyundai", "kia",
            "ford", "audi", "bmw", "mercedes-benz", "peugeot", "renault",
            "fiat", "mazda", "nissan", "subaru", "suzuki", "seat", "skoda"
        ]
    }

    sampled_makes = brand_pool.get(
        body_type, ["bmw", "audi", "porsche", "mercedes-benz"]
    )
    random.shuffle(sampled_makes)

    for make_name in sampled_makes:
        try:
            res = requests.get(
                url, headers=headers, params={"make": make_name}
            )
            if res.status_code == 200 and res.json():
                return res.json()
        except Exception:
            continue

    return []
