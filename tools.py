import os
import json
import requests

from dotenv import load_dotenv


# =========================
# ENVIRONMENT
# =========================

load_dotenv()


# =========================
# RAILWAY API CONFIG
# =========================

RAILWAY_API_URL = os.getenv(
    "RAILWAY_API_URL",
    ""
)

RAILWAY_API_KEY = os.getenv(
    "RAILWAY_API_KEY",
    ""
)


# =========================
# HELPER
# =========================

def railway_request(
    endpoint,
    params=None
):
    """
    Make a request to the configured
    authorized railway API.
    """

    if not RAILWAY_API_URL:
        return {
            "success": False,
            "error": (
                "Railway API is not configured. "
                "Set RAILWAY_API_URL in .env."
            )
        }

    headers = {}

    if RAILWAY_API_KEY:
        headers["Authorization"] = (
            f"Bearer {RAILWAY_API_KEY}"
        )

    try:

        response = requests.get(
            f"{RAILWAY_API_URL.rstrip('/')}/{endpoint.lstrip('/')}",
            params=params or {},
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        return {
            "success": True,
            "data": response.json()
        }

    except requests.RequestException as error:

        return {
            "success": False,
            "error": str(error)
        }

    except ValueError:

        return {
            "success": False,
            "error": "Railway API returned invalid JSON."
        }


# =========================
# TRAIN SEARCH
# =========================

def train_search(
    source,
    destination,
    journey_date
):
    """
    Search trains between two stations
    for a specific journey date.
    """

    result = railway_request(
        "/trains/search",
        {
            "source": source,
            "destination": destination,
            "date": journey_date
        }
    )

    if not result["success"]:

        return json.dumps(
            {
                "success": False,
                "message": result["error"]
            },
            ensure_ascii=False
        )

    return json.dumps(
        {
            "success": True,
            "source": source,
            "destination": destination,
            "journey_date": journey_date,
            "results": result["data"]
        },
        ensure_ascii=False
    )


# =========================
# AVAILABILITY CHECK
# =========================

def availability_check(
    train_number,
    journey_date,
    travel_class
):
    """
    Check live availability for a train,
    date and class.
    """

    result = railway_request(
        "/trains/availability",
        {
            "train_number": train_number,
            "date": journey_date,
            "class": travel_class
        }
    )

    if not result["success"]:

        return json.dumps(
            {
                "success": False,
                "message": result["error"]
            },
            ensure_ascii=False
        )

    return json.dumps(
        {
            "success": True,
            "train_number": train_number,
            "journey_date": journey_date,
            "travel_class": travel_class,
            "availability": result["data"]
        },
        ensure_ascii=False
    )


# =========================
# FARE CHECK
# =========================

def fare_check(
    train_number,
    journey_date,
    travel_class
):
    """
    Check the current fare for a
    selected train and class.
    """

    result = railway_request(
        "/trains/fare",
        {
            "train_number": train_number,
            "date": journey_date,
            "class": travel_class
        }
    )

    if not result["success"]:

        return json.dumps(
            {
                "success": False,
                "message": result["error"]
            },
            ensure_ascii=False
        )

    return json.dumps(
        {
            "success": True,
            "train_number": train_number,
            "journey_date": journey_date,
            "travel_class": travel_class,
            "fare": result["data"]
        },
        ensure_ascii=False
    )


# =========================
# BOOKING STATUS
# =========================

def booking_status(
    booking_reference
):
    """
    Check the status of an existing
    reservation using its reference.
    """

    result = railway_request(
        "/booking/status",
        {
            "booking_reference":
                booking_reference
        }
    )

    if not result["success"]:

        return json.dumps(
            {
                "success": False,
                "message": result["error"]
            },
            ensure_ascii=False
        )

    return json.dumps(
        {
            "success": True,
            "booking_reference":
                booking_reference,
            "status": result["data"]
        },
        ensure_ascii=False
)
