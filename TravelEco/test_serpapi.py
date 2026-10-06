import os

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

SERPAPI_API_KEY = os.getenv(
    "SERPAPI_API_KEY"
)

SERPAPI_URL = (
    "https://serpapi.com/search.json"
)


# ============================================================
# FLIGHT SEARCH
# ============================================================

def test_flights():

    print()
    print("=" * 70)
    print("FLIGHT TEST")
    print("=" * 70)

    params = {
        "engine":
            "google_flights",

        "departure_id":
            "BER",

        "arrival_id":
            "CDG",

        "outbound_date":
            "2026-10-20",

        "return_date":
            "2026-10-25",

        "currency":
            "EUR",

        "hl":
            "en",

        "type":
            "1",

        "api_key":
            SERPAPI_API_KEY,
    }


    response = requests.get(
        SERPAPI_URL,
        params=params,
        timeout=30,
    )


    response.raise_for_status()


    data = response.json()


    flights = (
        data.get(
            "best_flights",
            []
        )
        or
        data.get(
            "other_flights",
            []
        )
    )


    if not flights:

        print(
            "No flight results found."
        )

        return


    for index, option in enumerate(
        flights[:3],
        start=1,
    ):

        legs = option.get(
            "flights",
            []
        )


        airlines = []

        for leg in legs:

            airline = leg.get(
                "airline"
            )

            if (
                airline
                and airline
                not in airlines
            ):

                airlines.append(
                    airline
                )


        airline_text = (
            ", ".join(airlines)
            if airlines
            else "Unknown airline"
        )


        price = option.get(
            "price",
            "N/A"
        )


        duration = option.get(
            "total_duration"
        )


        carbon = option.get(
            "carbon_emissions",
            {}
        )


        carbon_grams = carbon.get(
            "this_flight"
        )


        carbon_kg = None


        if carbon_grams is not None:

            carbon_kg = round(
                carbon_grams / 1000,
                1,
            )


        print()
        print(
            f"OPTION {index}"
        )

        print(
            "Airline:",
            airline_text
        )

        print(
            "Price:",
            f"€{price}"
        )


        if duration:

            hours = (
                duration // 60
            )

            minutes = (
                duration % 60
            )

            print(
                "Duration:",
                f"{hours}h {minutes}m"
            )


        if carbon_kg is not None:

            print(
                "Google Flights carbon estimate:",
                f"{carbon_kg} kg CO2e"
            )


        if legs:

            first_leg = legs[0]

            last_leg = legs[-1]


            departure = (
                first_leg
                .get(
                    "departure_airport",
                    {}
                )
            )


            arrival = (
                last_leg
                .get(
                    "arrival_airport",
                    {}
                )
            )


            print(
                "Departure:",
                departure.get(
                    "name"
                ),
                departure.get(
                    "time"
                )
            )

            print(
                "Arrival:",
                arrival.get(
                    "name"
                ),
                arrival.get(
                    "time"
                )
            )


# ============================================================
# HOTEL SEARCH
# ============================================================

def test_hotels():

    print()
    print("=" * 70)
    print("HOTEL TEST")
    print("=" * 70)

    params = {
        "engine":
            "google_hotels",

        "q":
            "Paris eco friendly hotels",

        "check_in_date":
            "2026-10-20",

        "check_out_date":
            "2026-10-25",

        "adults":
            "1",

        "currency":
            "EUR",

        "hl":
            "en",

        "gl":
            "fr",

        "api_key":
            SERPAPI_API_KEY,
    }


    response = requests.get(
        SERPAPI_URL,
        params=params,
        timeout=30,
    )


    response.raise_for_status()


    data = response.json()


    properties = data.get(
        "properties",
        []
    )


    if not properties:

        print(
            "No hotel results found."
        )

        return


    for index, hotel in enumerate(
        properties[:3],
        start=1,
    ):

        print()
        print(
            f"HOTEL {index}"
        )


        print(
            "Name:",
            hotel.get(
                "name",
                "Unknown"
            )
        )


        print(
            "Rating:",
            hotel.get(
                "overall_rating",
                "N/A"
            )
        )


        print(
            "Reviews:",
            hotel.get(
                "reviews",
                "N/A"
            )
        )


        rate = hotel.get(
            "rate_per_night",
            {}
        )


        lowest = (
            hotel.get(
                "total_rate",
                {}
            )
        )


        if rate:

            print(
                "Rate per night:",
                rate.get(
                    "lowest",
                    "N/A"
                )
            )


        if lowest:

            print(
                "Total stay:",
                lowest.get(
                    "lowest",
                    "N/A"
                )
            )


        amenities = hotel.get(
            "amenities",
            []
        )


        if amenities:

            print(
                "Amenities:",
                ", ".join(
                    amenities[:5]
                )
            )


# ============================================================
# MAIN
# ============================================================

def main():

    if not SERPAPI_API_KEY:

        print(
            "ERROR: SERPAPI_API_KEY "
            "was not found in .env"
        )

        return


    print(
        "TravelEco SerpApi Test"
    )


    try:

        test_flights()

        test_hotels()


    except requests.exceptions.HTTPError as error:

        print()
        print(
            "HTTP ERROR"
        )


        if error.response is not None:

            print(
                error.response.text
            )


    except Exception as error:

        print()
        print(
            "ERROR:",
            error
        )


if __name__ == "__main__":

    main()