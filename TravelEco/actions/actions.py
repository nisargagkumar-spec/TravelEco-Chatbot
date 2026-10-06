import math
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Text

import requests
from dotenv import load_dotenv

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

CLIMATIQ_BASE_URL = "https://api.climatiq.io/data/v1"
CLIMATIQ_DATA_VERSION = "^37"

SERPAPI_URL = "https://serpapi.com/search.json"


# ============================================================
# TRIP FORM VALIDATION
# ============================================================

class ValidateTripForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_trip_form"

    # ========================================================
    # DATE PARSER
    # ========================================================

    def parse_strict_date(
        self,
        raw_value: str,
        reference_date: Optional[datetime] = None,
    ) -> Optional[datetime]:

        value = raw_value.lower().strip()

        # Remove ordinal suffixes:
        # 7th November -> 7 November
        value = re.sub(
            r"(\d{1,2})(st|nd|rd|th)\b",
            r"\1",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        patterns = [
            "%d %B %Y",
            "%d %b %Y",
            "%d %B",
            "%d %b",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%Y",
            "%d/%m",
            "%d-%m",
            "%d.%m",
        ]

        parsed_date = None

        year_was_given = bool(
            re.search(
                r"\b20\d{2}\b",
                value,
            )
        )

        for pattern in patterns:

            try:

                parsed_date = datetime.strptime(
                    value,
                    pattern,
                )

                break

            except ValueError:
                continue

        if parsed_date is None:
            return None

        if year_was_given:
            return parsed_date

        if reference_date is None:
            reference_date = datetime.today()

        parsed_date = parsed_date.replace(
            year=reference_date.year
        )

        if (
            parsed_date.date()
            < reference_date.date()
        ):

            parsed_date = parsed_date.replace(
                year=reference_date.year + 1
            )

        return parsed_date

    # ========================================================
    # INVALID LOCATION CHECK
    # ========================================================

    def invalid_location_value(
        self,
        value: str,
    ) -> bool:

        value_lower = value.lower().strip()

        time_words = {
            "today",
            "tomorrow",
            "yesterday",
            "next week",
            "next month",
            "this week",
            "this month",
        }

        if value_lower in time_words:
            return True

        if re.fullmatch(
            r"[\d\s.,€$£]+",
            value_lower,
        ):
            return True

        if (
            self.parse_strict_date(
                value_lower
            )
            is not None
        ):
            return True

        return False

    # ========================================================
    # CLEAN LOCATION
    # ========================================================

    def clean_location(
        self,
        value: str,
    ) -> str:

        value = value.strip()

        prefixes = [
            "from ",
            "to ",
            "in ",
            "at ",
        ]

        value_lower = value.lower()

        for prefix in prefixes:

            if value_lower.startswith(
                prefix
            ):

                value = value[
                    len(prefix):
                ].strip()

                break

        return value.title()

    # ========================================================
    # ORIGIN
    # ========================================================

    def validate_origin(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        value = str(
            slot_value
        ).strip()

        if (
            not value
            or self.invalid_location_value(
                value
            )
        ):

            dispatcher.utter_message(
                text=(
                    "Please enter a valid departure city, "
                    "for example Berlin."
                )
            )

            return {
                "origin": None
            }

        return {
            "origin":
                self.clean_location(
                    value
                )
        }

    # ========================================================
    # DESTINATION
    # ========================================================

    def validate_destination(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        value = str(
            slot_value
        ).strip()

        if (
            not value
            or self.invalid_location_value(
                value
            )
        ):

            dispatcher.utter_message(
                text=(
                    "Please enter a valid destination city, "
                    "for example Paris."
                )
            )

            return {
                "destination": None
            }

        return {
            "destination":
                self.clean_location(
                    value
                )
        }

    # ========================================================
    # START DATE
    # ========================================================

    def validate_start_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        raw_value = str(
            slot_value
        ).strip()

        parsed_date = (
            self.parse_strict_date(
                raw_value
            )
        )

        if parsed_date is None:

            dispatcher.utter_message(
                text=(
                    "I could not understand that departure date. "
                    "Try something like '7 November 2026'."
                )
            )

            return {
                "start_date": None
            }

        if (
            parsed_date.date()
            < datetime.today().date()
        ):

            dispatcher.utter_message(
                text=(
                    "That departure date is in the past."
                )
            )

            return {
                "start_date": None
            }

        return {
            "start_date":
                parsed_date.strftime(
                    "%d %B %Y"
                )
        }

    # ========================================================
    # END DATE
    # ========================================================

    def validate_end_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        raw_value = str(
            slot_value
        ).strip()

        start_value = tracker.get_slot(
            "start_date"
        )

        if not start_value:

            dispatcher.utter_message(
                text=(
                    "I need the departure date before "
                    "validating the return date."
                )
            )

            return {
                "end_date": None
            }

        try:

            start_date = datetime.strptime(
                start_value,
                "%d %B %Y",
            )

        except ValueError:

            return {
                "end_date": None
            }

        parsed_date = (
            self.parse_strict_date(
                raw_value,
                reference_date=start_date,
            )
        )

        if parsed_date is None:

            dispatcher.utter_message(
                text=(
                    "I could not understand that return date."
                )
            )

            return {
                "end_date": None
            }

        if (
            parsed_date.date()
            <= start_date.date()
        ):

            dispatcher.utter_message(
                text=(
                    "Your return date must be after "
                    "your departure date."
                )
            )

            return {
                "end_date": None
            }

        return {
            "end_date":
                parsed_date.strftime(
                    "%d %B %Y"
                )
        }

    # ========================================================
    # BUDGET
    # ========================================================

    def validate_budget(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        raw_value = str(
            slot_value
        ).strip()

        number_match = re.search(
            r"\d+(?:[.,]\d+)?",
            raw_value,
        )

        if not number_match:

            dispatcher.utter_message(
                text=(
                    "Please enter your budget as a number."
                )
            )

            return {
                "budget": None
            }

        try:

            value = float(
                number_match.group()
                .replace(
                    ",",
                    ".",
                )
            )

        except ValueError:

            return {
                "budget": None
            }

        if (
            value <= 0
            or value > 100000
        ):

            dispatcher.utter_message(
                text=(
                    "Please enter a realistic positive budget."
                )
            )

            return {
                "budget": None
            }

        if value.is_integer():
            value = int(value)

        return {
            "budget": value
        }

    # ========================================================
    # SUSTAINABILITY
    # ========================================================

    def validate_sustainability_level(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:

        value = (
            str(slot_value)
            .lower()
            .strip()
        )

        high_values = [
            "very important",
            "high",
            "high importance",
            "important",
            "a lot",
            "very high",
            "eco friendly",
            "eco-friendly",
        ]

        medium_values = [
            "balanced",
            "medium",
            "moderately important",
            "somewhat important",
            "somewhat",
            "moderate",
        ]

        low_values = [
            "low",
            "low priority",
            "not very important",
            "not important",
            "price",
            "cheapest",
            "cheap",
            "budget first",
        ]

        if value in high_values:

            return {
                "sustainability_level":
                    "high"
            }

        if value in medium_values:

            return {
                "sustainability_level":
                    "medium"
            }

        if value in low_values:

            return {
                "sustainability_level":
                    "low"
            }

        dispatcher.utter_message(
            text=(
                "Please choose 'very important', "
                "'balanced', or 'low priority'."
            )
        )

        return {
            "sustainability_level":
                None
        }


# ============================================================
# GEOCODING
# ============================================================

def geocode_location(
    location: str,
):

    url = (
        "https://nominatim."
        "openstreetmap.org/search"
    )

    params = {
        "q":
            location,

        "format":
            "json",

        "limit":
            1,
    }

    headers = {
        "User-Agent":
            "TravelEco-Student-Project/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    return (
        float(
            results[0]["lat"]
        ),
        float(
            results[0]["lon"]
        ),
    )


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_distance(
    coordinate_1,
    coordinate_2,
):

    lat1, lon1 = coordinate_1
    lat2, lon2 = coordinate_2

    radius_km = 6371.0

    phi1 = math.radians(
        lat1
    )

    phi2 = math.radians(
        lat2
    )

    delta_phi = math.radians(
        lat2 - lat1
    )

    delta_lambda = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(
            delta_phi / 2
        ) ** 2

        +

        math.cos(
            phi1
        )

        * math.cos(
            phi2
        )

        * math.sin(
            delta_lambda / 2
        ) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    return radius_km * c


# ============================================================
# FALLBACK APPROXIMATE DISTANCE
# ============================================================

def estimate_travel_distance(
    origin,
    destination,
    mode,
):

    origin_coordinates = (
        geocode_location(
            origin
        )
    )

    destination_coordinates = (
        geocode_location(
            destination
        )
    )

    if (
        origin_coordinates is None
        or destination_coordinates is None
    ):

        return None

    direct_distance = (
        haversine_distance(
            origin_coordinates,
            destination_coordinates,
        )
    )

    multipliers = {
        "flight": 1.00,
        "rail": 1.15,
        "bus": 1.20,
        "car": 1.20,
    }

    multiplier = multipliers.get(
        mode,
        1.0,
    )

    return round(
        direct_distance
        * multiplier,
        1,
    )


# ============================================================
# TRANSPORT MODE NORMALISATION
# ============================================================

def normalize_transport_mode(
    value,
):

    if not value:
        return None

    value = (
        str(value)
        .lower()
        .strip()
    )

    mapping = {

        "train":
            "rail",

        "rail":
            "rail",

        "railway":
            "rail",

        "bus":
            "bus",

        "coach":
            "bus",

        "car":
            "car",

        "drive":
            "car",

        "driving":
            "car",

        "flight":
            "flight",

        "plane":
            "flight",

        "airplane":
            "flight",

        "aeroplane":
            "flight",

        "fly":
            "flight",

        "flying":
            "flight",
    }

    return mapping.get(
        value
    )


# ============================================================
# ROUTE DEPARTURE TIMESTAMP
# ============================================================

def route_departure_timestamp(
    rasa_date,
):

    if not rasa_date:
        return None

    try:

        parsed = datetime.strptime(
            rasa_date,
            "%d %B %Y",
        )

        departure = datetime(
            parsed.year,
            parsed.month,
            parsed.day,
            9,
            0,
            tzinfo=timezone.utc,
        )

        return int(
            departure.timestamp()
        )

    except ValueError:

        return None


# ============================================================
# PARSE ROUTE DISTANCE
# ============================================================

def parse_distance_to_km(
    formatted_distance,
):

    if not formatted_distance:
        return None

    value = (
        str(formatted_distance)
        .lower()
        .strip()
    )

    match = re.search(
        r"([\d,.]+)\s*(km|m|mi)",
        value,
    )

    if not match:
        return None

    number_text = (
        match.group(1)
        .replace(",", "")
    )

    try:

        number = float(
            number_text
        )

    except ValueError:

        return None

    unit = match.group(2)

    if unit == "km":

        return round(
            number,
            1,
        )

    if unit == "m":

        return round(
            number / 1000,
            1,
        )

    if unit == "mi":

        return round(
            number * 1.60934,
            1,
        )

    return None


# ============================================================
# SERPAPI GROUND ROUTE SEARCH
# ============================================================

def search_ground_route(
    origin,
    destination,
    mode,
    start_date=None,
):

    if not SERPAPI_API_KEY:
        return None

    if mode not in [
        "rail",
        "bus",
        "car",
    ]:
        return None

    params = {

        "engine":
            "google_maps_directions",

        "start_addr":
            origin,

        "end_addr":
            destination,

        "distance_unit":
            "0",

        "hl":
            "en",

        "api_key":
            SERPAPI_API_KEY,
    }

    # ========================================================
    # RAIL / BUS
    # ========================================================

    if mode in [
        "rail",
        "bus",
    ]:

        params[
            "travel_mode"
        ] = "3"

        if mode == "rail":

            params[
                "prefer"
            ] = "train"

        else:

            params[
                "prefer"
            ] = "bus"

        timestamp = (
            route_departure_timestamp(
                start_date
            )
        )

        if timestamp:

            params[
                "time"
            ] = (
                f"depart_at:"
                f"{timestamp}"
            )

    # ========================================================
    # CAR
    # ========================================================

    elif mode == "car":

        params[
            "travel_mode"
        ] = "0"

    response = requests.get(
        SERPAPI_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    directions = data.get(
        "directions",
        []
    )

    if not directions:
        return None

    route = directions[0]

    distance_text = route.get(
        "formatted_distance"
    )

    distance_km = (
        parse_distance_to_km(
            distance_text
        )
    )

    duration = route.get(
        "formatted_duration"
    )

    start_time = route.get(
        "start_time"
    )

    end_time = route.get(
        "end_time"
    )

    via = route.get(
        "via"
    )

    trips = route.get(
        "trips",
        []
    )

    operators = []

    services = []

    for trip in trips:

        travel_mode = (
            trip.get(
                "travel_mode"
            )
        )

        title = trip.get(
            "title"
        )

        trip_duration = (
            trip.get(
                "formatted_duration"
            )
        )

        service_data = (
            trip.get(
                "service_run_by",
                {}
            )
        )

        operator = None

        if isinstance(
            service_data,
            dict,
        ):

            operator = (
                service_data.get(
                    "name"
                )
            )

        if (
            operator
            and operator
            not in operators
        ):

            operators.append(
                operator
            )

        if (
            title
            and travel_mode == "Transit"
        ):

            services.append(
                {
                    "title":
                        title,

                    "duration":
                        trip_duration,

                    "operator":
                        operator,
                }
            )

    return {

        "distance_km":
            distance_km,

        "distance_text":
            distance_text,

        "duration":
            duration,

        "start_time":
            start_time,

        "end_time":
            end_time,

        "via":
            via,

        "operators":
            operators,

        "services":
            services,

        "source":
            "SerpApi Google Maps Directions",
    }


# ============================================================
# CLIMATIQ EMISSION FACTOR SEARCH
# ============================================================

def search_climatiq_factor(
    transport_mode,
):

    if not CLIMATIQ_API_KEY:
        return None

    headers = {
        "Authorization":
            f"Bearer {CLIMATIQ_API_KEY}",
    }

    # ========================================================
    # BUS
    #
    # Public bus factor:
    # Netherlands
    # 0.086 kg CO2e / passenger-km
    # PassengerOverDistance
    #
    # We use a known compatible public factor because the
    # generic "passenger bus" search did not reliably return
    # a PassengerOverDistance factor near the top.
    # ========================================================

    if transport_mode == "bus":

        params = {

            "id":
                "883fa405-6f3d-4f36-88e2-4a91ecd21a03",

            "data_version":
                CLIMATIQ_DATA_VERSION,

            "access_type":
                "public",

            "results_per_page":
                10,
        }

    # ========================================================
    # RAIL / CAR / FLIGHT
    # ========================================================

    else:

        queries = {

            "rail":
                "passenger train",

            "car":
                "passenger car",

            "flight":
                "passenger flight",
        }

        query = queries.get(
            transport_mode
        )

        if not query:
            return None

        params = {

            "query":
                query,

            "data_version":
                CLIMATIQ_DATA_VERSION,

            "access_type":
                "public",

            "results_per_page":
                25,
        }

    response = requests.get(
        (
            f"{CLIMATIQ_BASE_URL}"
            "/search"
        ),
        headers=headers,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    results = (
        response.json()
        .get(
            "results",
            [],
        )
    )

    for factor in results:

        unit_type = (
            factor.get(
                "unit_type"
            )
        )

        # ====================================================
        # CAR
        # ====================================================

        if transport_mode == "car":

            if unit_type == "Distance":

                return factor

        # ====================================================
        # RAIL / BUS / FLIGHT
        # ====================================================

        else:

            if (
                unit_type
                == "PassengerOverDistance"
            ):

                return factor

    return None


# ============================================================
# CLIMATIQ ESTIMATE
# ============================================================

def calculate_climatiq_emissions(
    factor,
    transport_mode,
    distance_km,
):

    if transport_mode == "car":

        parameters = {

            "distance":
                distance_km,

            "distance_unit":
                "km",
        }

    else:

        parameters = {

            "passengers":
                1,

            "distance":
                distance_km,

            "distance_unit":
                "km",
        }

    payload = {

        "emission_factor": {

            "id":
                factor["id"]
        },

        "parameters":
            parameters,
    }

    headers = {

        "Authorization":
            f"Bearer {CLIMATIQ_API_KEY}",

        "Content-Type":
            "application/json",
    }

    response = requests.post(
        (
            f"{CLIMATIQ_BASE_URL}"
            "/estimate"
        ),
        headers=headers,
        json=payload,
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# SUSTAINABILITY FEEDBACK
# ============================================================

def sustainability_feedback(
    mode,
    level,
):

    if level == "high":

        if mode in [
            "rail",
            "bus",
        ]:

            return (
                "🌿 This transport mode is a strong "
                "match for your high sustainability "
                "preference."
            )

        if mode == "flight":

            return (
                "⚠️ Flying usually has a higher carbon "
                "impact. Because sustainability is very "
                "important to you, consider rail or bus "
                "when they are practical."
            )

        if mode == "car":

            return (
                "🌿 Car travel offers flexibility, "
                "but shared rail or bus travel may "
                "produce lower emissions."
            )

    if level == "medium":

        return (
            "🌱 You selected a balanced sustainability "
            "preference. TravelEco considers both "
            "practicality and carbon impact."
        )

    return (
        "ℹ️ Sustainability has a lower priority for this "
        "trip, but TravelEco still shows the carbon "
        "impact so you can make an informed choice."
    )


# ============================================================
# ROUTE SUMMARY TEXT
# ============================================================

def route_summary_text(
    mode,
    route,
):

    if not route:
        return ""

    icons = {

        "rail":
            "🚆",

        "bus":
            "🚌",

        "car":
            "🚗",
    }

    icon = icons.get(
        mode,
        "🗺️",
    )

    lines = [
        f"{icon} Live route information"
    ]

    if route.get(
        "distance_text"
    ):

        lines.append(
            (
                f"Route distance: "
                f"{route['distance_text']}"
            )
        )

    if route.get(
        "duration"
    ):

        lines.append(
            (
                f"Estimated duration: "
                f"{route['duration']}"
            )
        )

    if route.get(
        "start_time"
    ):

        lines.append(
            (
                f"Departure: "
                f"{route['start_time']}"
            )
        )

    if route.get(
        "end_time"
    ):

        lines.append(
            (
                f"Arrival: "
                f"{route['end_time']}"
            )
        )

    if route.get(
        "via"
    ):

        lines.append(
            (
                f"Route: "
                f"{route['via']}"
            )
        )

    operators = route.get(
        "operators",
        []
    )

    if operators:

        lines.append(
            (
                "Operators: "
                + ", ".join(
                    operators
                )
            )
        )

    services = route.get(
        "services",
        []
    )

    if services:

        lines.append(
            "\nJourney:"
        )

        for service in services[:4]:

            text = (
                f"• "
                f"{service['title']}"
            )

            if service.get(
                "duration"
            ):

                text += (
                    f" — "
                    f"{service['duration']}"
                )

            if service.get(
                "operator"
            ):

                text += (
                    f" ({service['operator']})"
                )

            lines.append(
                text
            )

    return "\n".join(
        lines
    )


# ============================================================
# CARBON + LIVE ROUTE ACTION
# ============================================================

class ActionCalculateCarbon(Action):

    def name(self) -> Text:
        return "action_calculate_carbon"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        origin = tracker.get_slot(
            "origin"
        )

        destination = tracker.get_slot(
            "destination"
        )

        start_date = tracker.get_slot(
            "start_date"
        )

        sustainability = (
            tracker.get_slot(
                "sustainability_level"
            )
            or "medium"
        )

        mode = normalize_transport_mode(
            tracker.get_slot(
                "transport_mode"
            )
        )

        # ====================================================
        # FALLBACK MODE DETECTION FROM LATEST MESSAGE
        # ====================================================

        if not mode:

            latest_text = (
                tracker.latest_message
                .get(
                    "text",
                    "",
                )
            )

            words = (
                latest_text
                .lower()
                .split()
            )

            for word in words:

                mode = (
                    normalize_transport_mode(
                        word
                    )
                )

                if mode:
                    break

        # ====================================================
        # REQUIRED DATA
        # ====================================================

        if (
            not origin
            or not destination
        ):

            dispatcher.utter_message(
                text=(
                    "I need your origin and destination "
                    "before calculating emissions."
                )
            )

            return []

        if not mode:

            dispatcher.utter_message(
                text=(
                    "Please choose a transport mode: "
                    "train, bus, car, or flight."
                )
            )

            return []

        if not CLIMATIQ_API_KEY:

            dispatcher.utter_message(
                text=(
                    "The Climatiq API key "
                    "is not available."
                )
            )

            return []

        try:

            route = None

            route_is_live = False

            # =================================================
            # RAIL / BUS / CAR
            # =================================================

            if mode in [
                "rail",
                "bus",
                "car",
            ]:

                dispatcher.utter_message(
                    text=(
                        f"Searching for a live "
                        f"{mode} route from "
                        f"{origin} to "
                        f"{destination}..."
                    )
                )

                try:

                    route = (
                        search_ground_route(
                            origin,
                            destination,
                            mode,
                            start_date,
                        )
                    )

                except requests.exceptions.RequestException:

                    route = None

                if (
                    route
                    and route.get(
                        "distance_km"
                    )
                ):

                    distance_km = (
                        route[
                            "distance_km"
                        ]
                    )

                    route_is_live = True

                    dispatcher.utter_message(
                        text=(
                            route_summary_text(
                                mode,
                                route,
                            )
                        )
                    )

                else:

                    distance_km = (
                        estimate_travel_distance(
                            origin,
                            destination,
                            mode,
                        )
                    )

                    dispatcher.utter_message(
                        text=(
                            "Live route information "
                            "was unavailable, so I am "
                            "using an approximate "
                            "distance for the carbon "
                            "calculation."
                        )
                    )

            # =================================================
            # FLIGHT
            # =================================================

            else:

                dispatcher.utter_message(
                    text=(
                        f"Calculating the carbon "
                        f"impact of travelling "
                        f"from {origin} to "
                        f"{destination} by flight..."
                    )
                )

                distance_km = (
                    estimate_travel_distance(
                        origin,
                        destination,
                        "flight",
                    )
                )

            # =================================================
            # DISTANCE CHECK
            # =================================================

            if distance_km is None:

                dispatcher.utter_message(
                    text=(
                        "I could not determine the "
                        "distance for this journey."
                    )
                )

                return []

            # =================================================
            # CLIMATIQ FACTOR
            # =================================================

            factor = (
                search_climatiq_factor(
                    mode
                )
            )

            if factor is None:

                dispatcher.utter_message(
                    text=(
                        "I could not find a suitable "
                        "public Climatiq emission "
                        f"factor for {mode}."
                    )
                )

                return []

            # =================================================
            # CLIMATIQ CALCULATION
            # =================================================

            result = (
                calculate_climatiq_emissions(
                    factor,
                    mode,
                    distance_km,
                )
            )

            co2e = round(
                result.get(
                    "co2e",
                    0,
                ),
                2,
            )

            unit = result.get(
                "co2e_unit",
                "kg",
            )

            mode_icons = {

                "rail":
                    "🚆",

                "bus":
                    "🚌",

                "car":
                    "🚗",

                "flight":
                    "✈️",
            }

            icon = mode_icons.get(
                mode,
                "🌍",
            )

            factor_name = (
                factor.get(
                    "name",
                    "Climatiq emission factor",
                )
            )

            source = (
                factor.get(
                    "source",
                    "Climatiq",
                )
            )

            year = (
                factor.get(
                    "year",
                    "N/A",
                )
            )

            region = (
                factor.get(
                    "region_name",
                    "N/A",
                )
            )

            feedback = (
                sustainability_feedback(
                    mode,
                    sustainability,
                )
            )

            if route_is_live:

                distance_label = (
                    "Live route distance"
                )

            else:

                distance_label = (
                    "Estimated travel distance"
                )

            dispatcher.utter_message(
                text=(
                    f"{icon} Carbon estimate\n\n"
                    f"Route: {origin} → "
                    f"{destination}\n"
                    f"Transport: "
                    f"{mode.title()}\n"
                    f"{distance_label}: "
                    f"{distance_km} km\n\n"
                    f"Estimated emissions: "
                    f"{co2e} {unit} CO₂e\n\n"
                    f"Emission factor: "
                    f"{factor_name}\n"
                    f"Source: "
                    f"{source} ({year})\n"
                    f"Region: "
                    f"{region}\n\n"
                    f"{feedback}\n\n"
                    f"Carbon estimates are "
                    f"calculated for one traveller."
                )
            )

        except requests.exceptions.HTTPError as error:

            response_text = ""

            if error.response is not None:

                response_text = (
                    error.response.text
                )

            dispatcher.utter_message(
                text=(
                    "I could not complete the "
                    "carbon calculation.\n\n"
                    f"API response: "
                    f"{response_text}"
                )
            )

        except requests.exceptions.RequestException:

            dispatcher.utter_message(
                text=(
                    "I could not connect to one "
                    "of the travel services. "
                    "Please try again."
                )
            )

        except Exception as error:

            dispatcher.utter_message(
                text=(
                    "Something went wrong while "
                    "calculating this journey: "
                    f"{error}"
                )
            )

        return []


# ============================================================
# TRANSPORT OPTIONS
# ============================================================

class ActionShowTransportOptions(Action):

    def name(self) -> Text:
        return "action_show_transport_options"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        origin = tracker.get_slot(
            "origin"
        )

        destination = tracker.get_slot(
            "destination"
        )

        sustainability = (
            tracker.get_slot(
                "sustainability_level"
            )
            or "medium"
        )

        # ====================================================
        # HIGH SUSTAINABILITY
        # ====================================================

        if sustainability == "high":

            options = [

                {
                    "mode":
                        "rail",

                    "label":
                        "Rail",

                    "icon":
                        "🚆",

                    "badge":
                        "Recommended",

                    "description":
                        (
                            "Usually one of the "
                            "lowest-carbon choices."
                        ),
                },

                {
                    "mode":
                        "bus",

                    "label":
                        "Bus",

                    "icon":
                        "🚌",

                    "badge":
                        "Low carbon",

                    "description":
                        (
                            "Shared road transport "
                            "with relatively low emissions."
                        ),
                },

                {
                    "mode":
                        "car",

                    "label":
                        "Car",

                    "icon":
                        "🚗",

                    "badge":
                        "Higher carbon",

                    "description":
                        (
                            "Flexible but usually "
                            "higher-carbon than shared "
                            "transport."
                        ),
                },

                {
                    "mode":
                        "flight",

                    "label":
                        "Flight",

                    "icon":
                        "✈️",

                    "badge":
                        "High carbon",

                    "description":
                        (
                            "Often the highest-carbon "
                            "option for shorter trips."
                        ),
                },
            ]

            subtitle = (
                "Your sustainability preference "
                "is high, so lower-carbon "
                "transport is prioritised."
            )

        # ====================================================
        # LOW SUSTAINABILITY
        # ====================================================

        elif sustainability == "low":

            options = [

                {
                    "mode":
                        "flight",

                    "label":
                        "Flight",

                    "icon":
                        "✈️",

                    "badge":
                        "Convenient",

                    "description":
                        (
                            "Useful for longer journeys."
                        ),
                },

                {
                    "mode":
                        "car",

                    "label":
                        "Car",

                    "icon":
                        "🚗",

                    "badge":
                        "Flexible",

                    "description":
                        (
                            "Provides flexible timing "
                            "and routing."
                        ),
                },

                {
                    "mode":
                        "bus",

                    "label":
                        "Bus",

                    "icon":
                        "🚌",

                    "badge":
                        "Affordable",

                    "description":
                        (
                            "Can provide lower prices "
                            "and lower emissions."
                        ),
                },

                {
                    "mode":
                        "rail",

                    "label":
                        "Rail",

                    "icon":
                        "🚆",

                    "badge":
                        "Lower carbon",

                    "description":
                        (
                            "A lower-carbon option "
                            "where practical."
                        ),
                },
            ]

            subtitle = (
                "Convenience and price receive "
                "more weight, while carbon impact "
                "is still shown."
            )

        # ====================================================
        # BALANCED
        # ====================================================

        else:

            options = [

                {
                    "mode":
                        "rail",

                    "label":
                        "Rail",

                    "icon":
                        "🚆",

                    "badge":
                        "Balanced choice",

                    "description":
                        (
                            "A strong balance between "
                            "sustainability and practicality."
                        ),
                },

                {
                    "mode":
                        "bus",

                    "label":
                        "Bus",

                    "icon":
                        "🚌",

                    "badge":
                        "Lower carbon",

                    "description":
                        (
                            "Shared transport with "
                            "relatively low emissions."
                        ),
                },

                {
                    "mode":
                        "car",

                    "label":
                        "Car",

                    "icon":
                        "🚗",

                    "badge":
                        "Flexible",

                    "description":
                        (
                            "Useful when route "
                            "flexibility matters."
                        ),
                },

                {
                    "mode":
                        "flight",

                    "label":
                        "Flight",

                    "icon":
                        "✈️",

                    "badge":
                        "Fast",

                    "description":
                        (
                            "Useful for long-distance "
                            "travel but higher-carbon."
                        ),
                },
            ]

            subtitle = (
                "Both practical and lower-carbon "
                "choices are considered."
            )

        dispatcher.utter_message(
            json_message={

                "type":
                    "transport_options",

                "title":
                    "Choose your preferred transport",

                "subtitle":
                    subtitle,

                "origin":
                    origin,

                "destination":
                    destination,

                "sustainability_level":
                    sustainability,

                "options":
                    options,
            }
        )

        return []


# ============================================================
# DATE CONVERSION
# ============================================================

def convert_rasa_date_to_iso(
    date_value,
):

    if not date_value:
        return None

    try:

        parsed = datetime.strptime(
            date_value,
            "%d %B %Y",
        )

        return parsed.strftime(
            "%Y-%m-%d"
        )

    except ValueError:

        return None


# ============================================================
# CITY → AIRPORT CODE
# ============================================================

CITY_TO_IATA = {

    "berlin":
        "BER",

    "paris":
        "CDG",

    "london":
        "LHR",

    "amsterdam":
        "AMS",

    "rome":
        "FCO",

    "milan":
        "MXP",

    "munich":
        "MUC",

    "hamburg":
        "HAM",

    "frankfurt":
        "FRA",

    "cologne":
        "CGN",

    "dusseldorf":
        "DUS",

    "vienna":
        "VIE",

    "prague":
        "PRG",

    "budapest":
        "BUD",

    "brussels":
        "BRU",

    "barcelona":
        "BCN",

    "madrid":
        "MAD",

    "lisbon":
        "LIS",

    "zurich":
        "ZRH",

    "geneva":
        "GVA",

    "copenhagen":
        "CPH",

    "stockholm":
        "ARN",

    "oslo":
        "OSL",

    "helsinki":
        "HEL",

    "dublin":
        "DUB",

    "bengaluru":
        "BLR",

    "bangalore":
        "BLR",

    "delhi":
        "DEL",

    "new delhi":
        "DEL",

    "mumbai":
        "BOM",

    "chennai":
        "MAA",

    "hyderabad":
        "HYD",

    "casablanca":
        "CMN",

    "marrakesh":
        "RAK",

    "marrakech":
        "RAK",
}


def get_airport_code(
    location,
):

    if not location:
        return None

    cleaned = (
        str(location)
        .lower()
        .strip()
    )

    if "," in cleaned:

        cleaned = (
            cleaned
            .split(",")[0]
            .strip()
        )

    return CITY_TO_IATA.get(
        cleaned
    )


# ============================================================
# LIVE FLIGHT SEARCH
# ============================================================

class ActionSearchFlights(Action):

    def name(self) -> Text:
        return "action_search_flights"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        origin = tracker.get_slot(
            "origin"
        )

        destination = tracker.get_slot(
            "destination"
        )

        start_date = tracker.get_slot(
            "start_date"
        )

        end_date = tracker.get_slot(
            "end_date"
        )

        budget = tracker.get_slot(
            "budget"
        )

        if not SERPAPI_API_KEY:

            dispatcher.utter_message(
                text=(
                    "The SerpApi key is missing."
                )
            )

            return []

        departure_code = (
            get_airport_code(
                origin
            )
        )

        arrival_code = (
            get_airport_code(
                destination
            )
        )

        if not departure_code:

            dispatcher.utter_message(
                text=(
                    f"I cannot identify an airport "
                    f"for '{origin}'. Please provide "
                    f"a specific city."
                )
            )

            return []

        if not arrival_code:

            dispatcher.utter_message(
                text=(
                    f"I cannot identify an airport "
                    f"for '{destination}'. Please "
                    f"provide a specific city."
                )
            )

            return []

        outbound_date = (
            convert_rasa_date_to_iso(
                start_date
            )
        )

        return_date = (
            convert_rasa_date_to_iso(
                end_date
            )
        )

        if (
            not outbound_date
            or not return_date
        ):

            dispatcher.utter_message(
                text=(
                    "I need valid travel dates "
                    "before searching for flights."
                )
            )

            return []

        params = {

            "engine":
                "google_flights",

            "departure_id":
                departure_code,

            "arrival_id":
                arrival_code,

            "outbound_date":
                outbound_date,

            "return_date":
                return_date,

            "currency":
                "EUR",

            "hl":
                "en",

            "type":
                "1",

            "api_key":
                SERPAPI_API_KEY,
        }

        try:

            dispatcher.utter_message(
                text=(
                    f"✈️ Searching live flights "
                    f"from {origin} to "
                    f"{destination}..."
                )
            )

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

                dispatcher.utter_message(
                    text=(
                        "I could not find live "
                        "flight options for "
                        "those dates."
                    )
                )

                return []

            output = [
                (
                    f"✈️ Live flight options\n\n"
                    f"{origin} → "
                    f"{destination}\n"
                    f"{start_date} – "
                    f"{end_date}\n"
                )
            ]

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

                    airline = (
                        leg.get(
                            "airline"
                        )
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
                    ", ".join(
                        airlines
                    )
                    if airlines
                    else "Unknown airline"
                )

                price = option.get(
                    "price",
                    "N/A",
                )

                duration = (
                    option.get(
                        "total_duration"
                    )
                )

                if duration:

                    hours = (
                        duration // 60
                    )

                    minutes = (
                        duration % 60
                    )

                    duration_text = (
                        f"{hours}h "
                        f"{minutes}m"
                    )

                else:

                    duration_text = "N/A"

                carbon_data = (
                    option.get(
                        "carbon_emissions",
                        {},
                    )
                )

                carbon_grams = (
                    carbon_data.get(
                        "this_flight"
                    )
                )

                if carbon_grams is not None:

                    flight_carbon = round(
                        carbon_grams / 1000,
                        1,
                    )

                    carbon_text = (
                        f"{flight_carbon} "
                        f"kg CO₂e"
                    )

                else:

                    carbon_text = "N/A"

                output.append(
                    (
                        f"\nOption {index}\n"
                        f"Airline: "
                        f"{airline_text}\n"
                        f"Price: €{price}\n"
                        f"Duration: "
                        f"{duration_text}\n"
                        f"Flight carbon indicator: "
                        f"{carbon_text}\n"
                    )
                )

            output.append(
                (
                    "\n🌿 TravelEco uses "
                    "Climatiq for its primary "
                    "sustainability carbon calculations."
                )
            )

            if budget:

                output.append(
                    (
                        f"\nYour stated trip "
                        f"budget: €{budget}"
                    )
                )

            dispatcher.utter_message(
                text="".join(
                    output
                )
            )

        except requests.exceptions.HTTPError as error:

            response_text = ""

            if error.response is not None:

                response_text = (
                    error.response.text
                )

            dispatcher.utter_message(
                text=(
                    "I could not retrieve "
                    "live flight data.\n\n"
                    f"API response: "
                    f"{response_text}"
                )
            )

        except requests.exceptions.RequestException as error:

            dispatcher.utter_message(
                text=(
                    "I could not retrieve "
                    "live flight data right now. "
                    f"Error: {error}"
                )
            )

        except Exception as error:

            dispatcher.utter_message(
                text=(
                    "Something went wrong "
                    "while searching flights: "
                    f"{error}"
                )
            )

        return []

# ============================================================
# LIVE HOTEL SEARCH
# ============================================================

class ActionSearchHotels(Action):

    def name(self) -> Text:
        return "action_search_hotels"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        origin = tracker.get_slot("origin")
        destination = tracker.get_slot("destination")
        start_date = tracker.get_slot("start_date")
        end_date = tracker.get_slot("end_date")
        budget = tracker.get_slot("budget")
        sustainability = tracker.get_slot(
            "sustainability_level"
        )

        if not SERPAPI_API_KEY:

            dispatcher.utter_message(
                text="The SerpApi key is missing."
            )

            return []

        if not destination:

            dispatcher.utter_message(
                text=(
                    "Please tell me your destination "
                    "before I search for accommodation."
                )
            )

            return []

        check_in = convert_rasa_date_to_iso(
            start_date
        )

        check_out = convert_rasa_date_to_iso(
            end_date
        )

        if not check_in or not check_out:

            dispatcher.utter_message(
                text=(
                    "I need valid trip dates before "
                    "searching for hotels."
                )
            )

            return []

        params = {

            "engine": "google_hotels",

            "q": (
                f"{destination} "
                f"eco friendly hotels"
            ),

            "check_in_date": check_in,

            "check_out_date": check_out,

            "adults": "1",

            "currency": "EUR",

            "hl": "en",

            "api_key": SERPAPI_API_KEY,
        }

        try:

            dispatcher.utter_message(
                text=(
                    f"🏨 Searching live accommodation "
                    f"in {destination}..."
                )
            )

            response = requests.get(
                SERPAPI_URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

            hotels = data.get(
                "properties",
                [],
            )

            if not hotels:

                dispatcher.utter_message(
                    text=(
                        "I could not find hotel results "
                        "for this trip."
                    )
                )

                return []

            hotel_options = []

            for index, hotel in enumerate(
                hotels[:3],
                start=1,
            ):

                name = hotel.get(
                    "name",
                    "Unknown hotel",
                )

                rating = hotel.get(
                    "overall_rating",
                    "N/A",
                )

                reviews = hotel.get(
                    "reviews",
                    "N/A",
                )

                nightly = (
                    hotel.get(
                        "rate_per_night",
                        {},
                    )
                    .get(
                        "lowest",
                        "N/A",
                    )
                )

                total = (
                    hotel.get(
                        "total_rate",
                        {},
                    )
                    .get(
                        "lowest",
                        "N/A",
                    )
                )

                amenities = hotel.get(
                    "amenities",
                    [],
                )

                hotel_options.append(
                    {
                        "id": f"hotel_{index}",
                        "number": index,
                        "name": name,
                        "rating": rating,
                        "reviews": reviews,
                        "nightly": nightly,
                        "total": total,
                        "amenities": amenities[:4],
                    }
                )

            dispatcher.utter_message(
                json_message={
                    "type": "hotel_options",

                    "destination":
                        destination,

                    "budget":
                        budget,

                    "hotels":
                        hotel_options,

                    "trip_context": {

                        "origin":
                            origin,

                        "destination":
                            destination,

                        "start_date":
                            start_date,

                        "end_date":
                            end_date,

                        "budget":
                            budget,

                        "sustainability_level":
                            sustainability,
                    },
                }
            )

        except requests.exceptions.HTTPError as error:

            response_text = ""

            if error.response is not None:

                response_text = (
                    error.response.text
                )

            dispatcher.utter_message(
                text=(
                    "I could not retrieve live hotel data.\n\n"
                    f"API response: {response_text}"
                )
            )

        except requests.exceptions.RequestException as error:

            dispatcher.utter_message(
                text=(
                    "I could not retrieve live hotel "
                    f"information. Error: {error}"
                )
            )

        except Exception as error:

            dispatcher.utter_message(
                text=(
                    "Something went wrong while "
                    f"searching hotels: {error}"
                )
            )

        return []
    

# ============================================================
# ADDITIONAL TRAVELECO ACTIONS
# Cultural events, recommendations, human help, fallback
# ============================================================

import os
import requests

from datetime import datetime
from dotenv import load_dotenv
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

load_dotenv()


# ============================================================
# CULTURAL EVENTS
# ============================================================

class ActionSearchEvents(Action):

    def name(self):
        return "action_search_events"

    def run(self, dispatcher, tracker, domain):

        destination = tracker.get_slot("destination")
        start_date = tracker.get_slot("start_date")
        end_date = tracker.get_slot("end_date")

        api_key = os.getenv("SERPAPI_API_KEY")

        def send_event_results(events, note=""):
            dispatcher.utter_message(
                json_message={
                    "type": "event_options",
                    "destination": destination or "",
                    "start_date": start_date,
                    "end_date": end_date,
                    "events": events,
                    "note": note,
                }
            )

        if not destination:
            dispatcher.utter_message(
                text=(
                    "Please tell me your destination "
                    "before searching for cultural events."
                )
            )
            send_event_results([])
            return []

        if not api_key:
            dispatcher.utter_message(
                text=(
                    "Cultural-event search is unavailable "
                    "because the SerpApi key is missing."
                )
            )
            send_event_results([])
            return []

        queries = [
            (
                f"cultural events exhibitions festivals "
                f"in {destination} {start_date or ''}"
            ),
            (
                f"concerts museums cultural activities "
                f"in {destination} {start_date or ''} "
                f"{end_date or ''}"
            ),
        ]

        events = []
        discovery_links = []
        seen = set()
        errors = []

        for query in queries:

            try:
                response = requests.get(
                    "https://serpapi.com/search.json",
                    params={
                        "engine": "google",
                        "q": query,
                        "hl": "en",
                        "num": 10,
                        "api_key": api_key,
                    },
                    timeout=25,
                )

                response.raise_for_status()
                data = response.json()

                if data.get("error"):
                    errors.append(str(data["error"]))
                    continue

            except (requests.RequestException, ValueError) as error:
                errors.append(str(error))
                continue

            # Structured Google event listings
            for item in data.get("events_results", []) or []:

                if not isinstance(item, dict):
                    continue

                title = item.get("title")

                if not title:
                    continue

                link = str(item.get("link") or "")
                unique_id = (link or str(title)).lower()

                if unique_id in seen:
                    continue

                seen.add(unique_id)

                date_info = item.get("date", "")

                if isinstance(date_info, dict):
                    date_text = (
                        date_info.get("when")
                        or date_info.get("start_date")
                        or "Check event date"
                    )
                else:
                    date_text = (
                        str(date_info)
                        if date_info
                        else "Check event date"
                    )

                venue = item.get("venue") or item.get("address") or ""

                if isinstance(venue, dict):
                    venue = (
                        venue.get("name")
                        or venue.get("address")
                        or ""
                    )

                if isinstance(venue, list):
                    venue = ", ".join(map(str, venue))

                events.append({
                    "title": str(title),
                    "date": str(date_text),
                    "time": str(item.get("time") or ""),
                    "venue": str(venue),
                    "category": "Cultural event",
                    "link": link,
                })

                if len(events) >= 5:
                    break

            # Organic search links are unverified event leads,
            # not confirmed events.
            for item in data.get("organic_results", []) or []:

                if not isinstance(item, dict):
                    continue

                title = item.get("title")
                link = str(item.get("link") or "")

                if not title or not link.startswith(
                    ("http://", "https://")
                ):
                    continue

                if link.lower() in seen:
                    continue

                seen.add(link.lower())

                discovery_links.append({
                    "title": str(title),
                    "date": "Date unverified — check organiser",
                    "time": "",
                    "venue": str(
                        item.get("source")
                        or "Event discovery website"
                    ),
                    "category": (
                        "Discovery link — not a confirmed event"
                    ),
                    "link": link,
                })

                if len(discovery_links) >= 5:
                    break

            if len(events) >= 5:
                break

        if events:

            dispatcher.utter_message(
                text=(
                    f"🎭 I found {len(events)} cultural-event "
                    f"listings for {destination}. "
                    "Please confirm dates and availability "
                    "before attending."
                )
            )

            send_event_results(
                events[:5],
                "Event listings require date verification.",
            )

        elif discovery_links:

            dispatcher.utter_message(
                text=(
                    f"🎭 I found cultural-event discovery "
                    f"links for {destination}. "
                    "I could not confirm individual events "
                    "during your exact travel dates."
                )
            )

            send_event_results(
                discovery_links[:5],
                "These are discovery links, not confirmed events.",
            )

        else:

            message = (
                "I could not connect to the event search service. "
                "Please check your SerpApi key and quota."
                if errors
                else (
                    f"No cultural events could be confirmed "
                    f"for {destination} during your trip."
                )
            )

            dispatcher.utter_message(text=message)
            send_event_results([])

        return []


# ============================================================
# TRANSPORT RECOMMENDATIONS
# ============================================================

class ActionRecommendTransport(Action):

    def name(self):
        return "action_recommend_transport"

    def run(self, dispatcher, tracker, domain):

        origin = tracker.get_slot("origin")
        destination = tracker.get_slot("destination")
        sustainability = (
            tracker.get_slot("sustainability_level")
            or "medium"
        )

        if not origin or not destination:

            dispatcher.utter_message(
                text=(
                    "Please complete your trip details "
                    "before requesting a transport recommendation."
                )
            )
            return []

        # This provides a qualitative recommendation.
        # Actual route availability must be verified.

        if sustainability == "high":

            recommendation = (
                "🚆 Start by checking rail connections. "
                "If rail is unavailable, compare coach buses. "
                "These often have lower emissions per passenger "
                "than flying or driving alone."
            )

        elif sustainability == "low":

            recommendation = (
                "🌍 Compare rail, bus, car, and flight based "
                "on travel time, cost, and convenience. "
                "Rail or bus may also reduce emissions."
            )

        else:

            recommendation = (
                "🌿 Rail is a good starting point for "
                "a balanced trip. Compare coach buses "
                "for affordability and check travel time "
                "before making your final decision."
            )

        dispatcher.utter_message(
            text=(
                "🌱 TravelEco transport recommendation\n\n"
                f"Route: {origin} → {destination}\n"
                f"Sustainability: {sustainability}\n\n"
                f"{recommendation}\n\n"
                "This is general guidance, not a verified "
                "live route or fare comparison."
            )
        )

        return []


# ============================================================
# HUMAN HELP
# ============================================================

class ActionHumanHandover(Action):

    def name(self):
        return "action_human_handover"

    def run(self, dispatcher, tracker, domain):

        fields = [
            "origin",
            "destination",
            "start_date",
            "end_date",
            "budget",
            "sustainability_level",
            "transport_mode",
        ]

        trip_context = {
            field: tracker.get_slot(field)
            for field in fields
        }

        recent_messages = []

        for event in tracker.events or []:

            if event.get("event") == "user":
                text = event.get("text")

                if text:
                    recent_messages.append(text)

        dispatcher.utter_message(
            text=(
                "👤 I have prepared your travel details "
                "for a human advisor. "
                "This prototype does not automatically "
                "connect you to a live advisor."
            )
        )

        dispatcher.utter_message(
            json_message={
                "type": "human_handover",
                "status": "prepared",
                "trip_context": trip_context,
                "recent_messages": recent_messages[-10:],
                "prototype_notice": (
                    "Live human support is not connected."
                ),
            }
        )

        return []


# ============================================================
# FALLBACK HANDLING
# ============================================================

class ActionHandleFallback(Action):

    def name(self):
        return "action_handle_fallback"

    def run(self, dispatcher, tracker, domain):

        user_events = [
            event
            for event in (tracker.events or [])
            if event.get("event") == "user"
        ]

        previous_intent = None

        if len(user_events) >= 2:

            previous_intent = (
                user_events[-2]
                .get("parse_data", {})
                .get("intent", {})
                .get("name")
            )

        if previous_intent in [
            "nlu_fallback",
            "out_of_scope",
        ]:

            dispatcher.utter_message(
                text=(
                    "I'm still having trouble understanding. "
                    "I'll prepare your details for human support."
                )
            )

            return ActionHumanHandover().run(
                dispatcher,
                tracker,
                domain,
            )

        dispatcher.utter_message(
            text=(
                "I'm sorry, I didn't understand that. "
                "Could you rephrase your question?"
            ),
            buttons=[
                {
                    "title": "🌿 Plan a trip",
                    "payload": "/plan_trip",
                },
                {
                    "title": "👤 Human help",
                    "payload": "/request_human",
                },
            ],
        )

        return []


# ============================================================
# DEFAULT FALLBACK
# ============================================================

class ActionDefaultFallback(Action):

    def name(self):
        return "action_default_fallback"

    def run(self, dispatcher, tracker, domain):

        return ActionHandleFallback().run(
            dispatcher,
            tracker,
            domain,
        )
