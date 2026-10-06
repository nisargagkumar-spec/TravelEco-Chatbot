import os

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

API_KEY = os.getenv("CLIMATIQ_API_KEY")

BASE_URL = "https://api.climatiq.io/data/v1"

DATA_VERSION = "^37"

DISTANCE_KM = 650


headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


# ============================================================
# SEARCH EMISSION FACTOR
# ============================================================

def search_factor(query):

    response = requests.get(
        f"{BASE_URL}/search",
        headers=headers,
        params={
            "query": query,
            "data_version": DATA_VERSION,
            "access_type": "public",
            "results_per_page": 5,
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    results = data.get(
        "results",
        []
    )

    if not results:
        return None

    return results[0]


# ============================================================
# CALCULATE EMISSIONS
# ============================================================

def calculate_emissions(
    factor,
    distance_km,
):

    unit_type = factor.get(
        "unit_type"
    )


    # Train and flight
    if unit_type == "PassengerOverDistance":

        parameters = {
            "passengers": 1,
            "distance": distance_km,
            "distance_unit": "km",
        }


    # Car
    elif unit_type == "Distance":

        parameters = {
            "distance": distance_km,
            "distance_unit": "km",
        }


    else:

        raise ValueError(
            f"Unsupported unit type: {unit_type}"
        )


    payload = {
        "emission_factor": {
            "id": factor["id"]
        },
        "parameters": parameters,
    }


    response = requests.post(
        f"{BASE_URL}/estimate",
        headers=headers,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# TEST TRANSPORT MODE
# ============================================================

def test_mode(
    title,
    query,
):

    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


    factor = search_factor(
        query
    )


    if not factor:

        print(
            "No public factor found."
        )

        return


    print(
        "Selected factor:",
        factor.get("name")
    )

    print(
        "Region:",
        factor.get("region_name")
    )

    print(
        "Source:",
        factor.get("source")
    )

    print(
        "Year:",
        factor.get("year")
    )

    print(
        "Unit type:",
        factor.get("unit_type")
    )


    result = calculate_emissions(
        factor,
        DISTANCE_KM,
    )


    print()
    print(
        f"Distance: {DISTANCE_KM} km"
    )

    print(
        "CO2e:",
        round(
            result.get(
                "co2e",
                0
            ),
            2
        ),
        result.get(
            "co2e_unit"
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    if not API_KEY:

        print(
            "ERROR: API key missing."
        )

        return


    print()
    print(
        "TravelEco Carbon Test"
    )

    print(
        "Berlin → Amsterdam"
    )

    print(
        f"Estimated distance: {DISTANCE_KM} km"
    )


    test_mode(
        "TRAIN",
        "passenger train",
    )


    test_mode(
        "CAR",
        "passenger car",
    )


    test_mode(
        "FLIGHT",
        "passenger flight",
    )


if __name__ == "__main__":
    main()