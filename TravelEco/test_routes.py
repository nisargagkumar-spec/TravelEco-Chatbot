import os
from datetime import datetime, timezone

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
# DATE / TIME
# ============================================================

def departure_timestamp():

    departure = datetime(
        2026,
        10,
        20,
        9,
        0,
        tzinfo=timezone.utc,
    )

    return int(
        departure.timestamp()
    )


# ============================================================
# PRINT ROUTE
# ============================================================

def print_route(
    title,
    data,
):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    directions = data.get(
        "directions",
        []
    )

    if not directions:

        print(
            "No route found."
        )

        return

    for index, route in enumerate(
        directions[:3],
        start=1,
    ):

        print()
        print(
            f"OPTION {index}"
        )

        print(
            "Travel mode:",
            route.get(
                "travel_mode",
                "N/A",
            )
        )

        print(
            "Route:",
            route.get(
                "via",
                "N/A",
            )
        )

        print(
            "Distance:",
            route.get(
                "formatted_distance",
                "N/A",
            )
        )

        print(
            "Duration:",
            route.get(
                "formatted_duration",
                "N/A",
            )
        )

        if route.get(
            "start_time"
        ):

            print(
                "Departure:",
                route.get(
                    "start_time"
                )
            )

        if route.get(
            "end_time"
        ):

            print(
                "Arrival:",
                route.get(
                    "end_time"
                )
            )

        if route.get(
            "cost"
        ) is not None:

            print(
                "Cost:",
                route.get(
                    "cost"
                ),
                route.get(
                    "currency",
                    "",
                )
            )

        trips = route.get(
            "trips",
            []
        )

        if trips:

            print(
                "Journey details:"
            )

            for trip in trips:

                travel_mode = trip.get(
                    "travel_mode"
                )

                title_text = trip.get(
                    "title"
                )

                duration = trip.get(
                    "formatted_duration"
                )

                service = (
                    trip.get(
                        "service_run_by",
                        {}
                    )
                )

                operator = service.get(
                    "name"
                )

                if travel_mode:

                    print(
                        "  - Mode:",
                        travel_mode
                    )

                if title_text:

                    print(
                        "    Route:",
                        title_text
                    )

                if duration:

                    print(
                        "    Duration:",
                        duration
                    )

                if operator:

                    print(
                        "    Operator:",
                        operator
                    )


# ============================================================
# TRAIN
# ============================================================

def test_train():

    params = {
        "engine":
            "google_maps_directions",

        "start_addr":
            "Berlin, Germany",

        "end_addr":
            "Paris, France",

        "travel_mode":
            "3",

        "prefer":
            "train",

        "distance_unit":
            "0",

        "time":
            (
                "depart_at:"
                f"{departure_timestamp()}"
            ),

        "hl":
            "en",

        "api_key":
            SERPAPI_API_KEY,
    }

    response = requests.get(
        SERPAPI_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    print_route(
        "TRAIN / RAIL TEST",
        response.json(),
    )


# ============================================================
# BUS
# ============================================================

def test_bus():

    params = {
        "engine":
            "google_maps_directions",

        "start_addr":
            "Berlin, Germany",

        "end_addr":
            "Paris, France",

        "travel_mode":
            "3",

        "prefer":
            "bus",

        "distance_unit":
            "0",

        "time":
            (
                "depart_at:"
                f"{departure_timestamp()}"
            ),

        "hl":
            "en",

        "api_key":
            SERPAPI_API_KEY,
    }

    response = requests.get(
        SERPAPI_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    print_route(
        "BUS TEST",
        response.json(),
    )


# ============================================================
# CAR
# ============================================================

def test_car():

    params = {
        "engine":
            "google_maps_directions",

        "start_addr":
            "Berlin, Germany",

        "end_addr":
            "Paris, France",

        "travel_mode":
            "0",

        "distance_unit":
            "0",

        "hl":
            "en",

        "api_key":
            SERPAPI_API_KEY,
    }

    response = requests.get(
        SERPAPI_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    print_route(
        "CAR / DRIVING TEST",
        response.json(),
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
        "TravelEco Route Search Test"
    )

    try:

        test_train()
        test_bus()
        test_car()

    except requests.exceptions.HTTPError as error:

        print()
        print(
            "HTTP ERROR"
        )

        if error.response is not None:

            print(
                error.response.text
            )

    except requests.exceptions.RequestException as error:

        print()
        print(
            "CONNECTION ERROR:",
            error
        )

    except Exception as error:

        print()
        print(
            "ERROR:",
            error
        )


if __name__ == "__main__":

    main()