import html
import uuid
from datetime import datetime

import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

WELCOME_MESSAGE = (
    "Hi! 🌿 I'm TravelEco, your sustainable travel assistant.\n\n"
    "I can help you plan greener trips, compare low-carbon transport, "
    "discover eco-friendly stays, estimate travel emissions, and build "
    "personalized itineraries.\n\n"
    "Where would you like to go?"
)

st.set_page_config(
    page_title="TravelEco",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# HELPERS
# ============================================================

def current_time():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


def create_sender_id():
    return f"travel_user_{uuid.uuid4().hex}"


def safe(value):
    return html.escape(
        "" if value is None else str(value)
    )


def leaf_svg():
    return (
        '<svg viewBox="0 0 48 48">'
        '<path d="M10 31 C11 18 20 12 32 10 '
        'C31 22 25 30 15 34"></path>'
        '<path d="M15 34 C20 26 25 20 32 14"></path>'
        '<path d="M16 35 C10 29 8 24 9 19 '
        'C16 20 21 25 22 31"></path>'
        '</svg>'
    )


def transport_label(mode):

    return {
        "rail": "🚆 Rail",
        "bus": "🚌 Bus",
        "car": "🚗 Car",
        "flight": "✈️ Flight",
    }.get(
        mode,
        str(mode).title(),
    )


# ============================================================
# SESSION STATE
# ============================================================

def fresh_trip_state(clear_messages=True):
    """Clear all frontend state and create a fresh Rasa tracker."""
    s = st.session_state
    s.sender_id = create_sender_id()
    s.resolved_transport_messages = {}
    s.selected_transport_mode = None
    s.pending_transport_payload = None
    s.pending_hotel_search = False
    s.resolved_hotel_messages = {}
    s.selected_hotel = None
    s.selected_trip_context = {}
    s.hotel_prompt_shown = False
    s.resolved_hotel_prompts = {}
    s.events_prompt_shown = False
    s.events_stage_complete = False
    s.event_choice = None
    s.events_found = []
    s.trip_summary_added = False
    s.flow_complete = False
    if clear_messages:
        s.messages = [{
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "timestamp": current_time(),
            "type": "text",
        }]


def initialize_session_state():
    s = st.session_state
    if "sender_id" not in s:
        fresh_trip_state()
    if "messages" not in s:
        s.messages = [{
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "timestamp": current_time(),
            "type": "text",
        }]
    defaults = {
        "resolved_transport_messages": {},
        "selected_transport_mode": None,
        "pending_transport_payload": None,
        "pending_hotel_search": False,
        "resolved_hotel_messages": {},
        "selected_hotel": None,
        "selected_trip_context": {},
        "hotel_prompt_shown": False,
        "resolved_hotel_prompts": {},
        "events_prompt_shown": False,
        "events_stage_complete": False,
        "event_choice": None,
        "events_found": [],
        "trip_summary_added": False,
        "flow_complete": False,
    }
    for key, value in defaults.items():
        if key not in s:
            s[key] = value


# ============================================================
# CSS
# ============================================================

def inject_css():

    st.markdown(
        """
<style>

#MainMenu,
footer,
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
.stDeployButton {
    display: none !important;
    visibility: hidden !important;
}

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    min-height: 100vh;
}

.stApp,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 2% 35%,
            rgba(226,236,218,.75),
            transparent 31%
        ),
        radial-gradient(
            circle at 98% 20%,
            rgba(230,238,222,.70),
            transparent 29%
        ),
        radial-gradient(
            circle at 76% 96%,
            rgba(244,235,212,.55),
            transparent 34%
        ),
        linear-gradient(
            135deg,
            #F7F6EE 0%,
            #FAF8F1 50%,
            #F2F5EC 100%
        ) !important;

    color: #174A32;
}

.block-container {
    width: 100% !important;
    max-width: 1050px !important;
    padding: 0 26px 135px !important;
    margin: 0 auto !important;
}


/* =========================================================
   HEADER
========================================================= */

.travel-brand {
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 20px 0 14px;
}

.brand-leaf,
.bot-avatar,
.composer-leaf {
    border-radius: 50%;
    background: #E8EFE1;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.brand-leaf {
    width: 52px;
    height: 52px;
}

.brand-leaf svg {
    width: 27px;
    height: 27px;
    stroke: #174A32;
    stroke-width: 1.8;
    fill: none;
}

.brand-title {
    color: #173F2B;
    font-size: 22px;
    font-weight: 700;
}

.brand-subtitle {
    color: #7A827C;
    font-size: 12px;
    margin-top: 3px;
}

.header-divider {
    height: 1px;
    background: #E7E8DF;
    margin: -7px 0 18px;
}

.st-key-new_chat_area button {
    min-height: 42px !important;
    padding: 8px 18px !important;
    border-radius: 999px !important;
    border: 1px solid #DCE3D6 !important;
    background: rgba(255,255,255,.42) !important;
    color: #174A32 !important;
    box-shadow: none !important;
    font-size: 13px !important;
    font-weight: 550 !important;
}

.st-key-new_chat_area button:hover {
    background: #174A32 !important;
    color: #FFFFFF !important;
    border-color: #174A32 !important;
}

.st-key-new_chat_area button:hover * {
    color: #FFFFFF !important;
}


/* =========================================================
   CHAT MESSAGES
========================================================= */

.message-row {
    width: 100%;
    display: flex;
    margin-bottom: 12px;
}

.message-row.user {
    justify-content: flex-end;
}

.message-row.assistant {
    justify-content: flex-start;
}

.user-message-wrapper {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    max-width: 70%;
}

.user-bubble {
    background:
        linear-gradient(
            135deg,
            #174A32,
            #255C43
        );

    color: #FFFFFF;

    border-radius:
        18px 18px 5px 18px;

    padding:
        13px 17px;

    font-size:
        14px;

    line-height:
        1.55;

    box-shadow:
        0 5px 18px
        rgba(28,70,47,.12);
}

.user-meta,
.assistant-meta {
    color: #7A827C;
    font-size: 11px;
    margin-top: 5px;
}

.assistant-row-inner {
    display: flex;
    align-items: flex-start;
    gap: 11px;
    max-width: 86%;
}

.bot-avatar {
    width: 46px;
    height: 46px;
}

.bot-avatar svg,
.composer-leaf svg {
    width: 24px;
    height: 24px;
    fill: none;
    stroke: #174A32;
    stroke-width: 1.8;
}

.assistant-content {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    min-width: 0;
}

.assistant-bubble {
    background:
        rgba(255,255,255,.90);

    color:
        #243D30;

    border:
        1px solid #E7E8DF;

    border-radius:
        18px 18px 18px 5px;

    padding:
        13px 16px;

    font-size:
        14px;

    line-height:
        1.55;

    box-shadow:
        0 4px 16px
        rgba(50,70,50,.045);
}


/* =========================================================
   RESULT CARDS
========================================================= */

.result-card,
.handover-card,
.trip-summary-card {

    width:
        min(700px, 100%);

    background:
        rgba(255,255,255,.95);

    color:
        #243D30;

    border:
        1px solid #E1E6DC;

    border-radius:
        20px 20px 20px 6px;

    overflow:
        hidden;

    box-shadow:
        0 8px 28px
        rgba(50,70,50,.07);
}

.result-card-header,
.trip-summary-header {

    padding:
        15px 18px 13px;

    background:
        linear-gradient(
            135deg,
            rgba(232,239,225,.90),
            rgba(248,248,242,.60)
        );

    border-bottom:
        1px solid #E5E9E1;

    color:
        #174A32;

    font-size:
        14px;

    font-weight:
        700;
}

.result-card-section {

    padding:
        13px 18px;

    border-top:
        1px solid #EEF0EA;

    color:
        #314A3B;

    font-size:
        13px;

    line-height:
        1.65;
}

.result-card-section:first-of-type {
    border-top: none;
}


/* =========================================================
   HOTEL CARDS
========================================================= */

.hotel-options-heading {

    color:
        #173F2B;

    font-size:
        15px;

    font-weight:
        700;

    margin:
        10px 0 3px 57px;
}

.hotel-options-sub {

    color:
        #728078;

    font-size:
        12px;

    margin:
        0 0 12px 57px;
}

.hotel-card {

    min-height:
        230px;

    padding:
        15px;

    border-radius:
        18px;

    background:
        rgba(255,255,255,.95);

    border:
        1px solid #E1E7DD;

    box-shadow:
        0 6px 20px
        rgba(50,70,50,.055);

    margin-bottom:
        8px;
}

.hotel-number {

    color:
        #68806F;

    font-size:
        11px;

    font-weight:
        700;

    text-transform:
        uppercase;
}

.hotel-name {

    color:
        #173F2B;

    font-size:
        15px;

    font-weight:
        700;

    line-height:
        1.35;

    margin:
        7px 0 9px;
}

.hotel-detail {

    color:
        #51645A;

    font-size:
        12px;

    line-height:
        1.6;
}

.hotel-amenities {

    color:
        #76827B;

    font-size:
        11px;

    line-height:
        1.5;

    margin-top:
        7px;
}

.hotel-selected-card {

    padding:
        14px 16px;

    border-radius:
        17px;

    background:
        #F1F6ED;

    border:
        1px solid #DDE8D8;

    color:
        #31513E;

    font-size:
        13px;

    line-height:
        1.6;
}


/* =========================================================
   HOTEL PROMPT / COMPLETION
========================================================= */

.hotel-prompt-card,
.completion-card {

    margin:
        8px 0 12px 57px;

    color:
        #31513E;

    font-size:
        13px;

    line-height:
        1.6;
}

.hotel-prompt-card b,
.completion-card b {

    color:
        #173F2B;
}


/* =========================================================
   HUMAN HANDOVER
========================================================= */

.handover-card {

    padding:
        15px 17px;
}

.handover-title {

    color:
        #173F2B;

    font-size:
        14px;

    font-weight:
        700;

    margin-bottom:
        4px;
}

.handover-subtitle {

    color:
        #66756C;

    font-size:
        12px;

    line-height:
        1.55;
}

.handover-context {

    margin-top:
        10px;

    padding:
        10px 12px;

    border-radius:
        12px;

    background:
        #EEF4EA;

    color:
        #31513E;

    font-size:
        12px;

    line-height:
        1.6;
}


/* =========================================================
   FINAL SUMMARY
========================================================= */

.trip-summary-body {

    padding:
        15px 18px;
}

.trip-summary-grid {

    display:
        grid;

    grid-template-columns:
        1fr 1fr;

    gap:
        8px 20px;
}

.trip-summary-item {

    font-size:
        12.5px;

    color:
        #40564A;

    line-height:
        1.55;
}

.trip-summary-item b {

    color:
        #234734;
}

.trip-summary-choice {

    margin-top:
        14px;

    padding:
        12px 14px;

    border-radius:
        13px;

    background:
        #EFF5EB;

    border:
        1px solid #DEE9D9;

    font-size:
        12.5px;

    color:
        #31513E;

    line-height:
        1.65;
}

.trip-summary-finish {

    margin-top:
        12px;

    padding-top:
        12px;

    border-top:
        1px solid #E7EBE3;

    color:
        #65746B;

    font-size:
        12px;

    line-height:
        1.55;
}


/* =========================================================
   ERRORS
========================================================= */

.backend-warning {

    margin:
        8px 0 15px 57px;

    padding:
        12px 15px;

    border-radius:
        14px;

    background:
        #FFF8E8;

    border:
        1px solid #EFE0B8;

    color:
        #66572F;

    font-size:
        12px;
}


/* =========================================================
   QUICK ACTIONS
========================================================= */

.st-key-chat_quick_actions {

    margin-top:
        10px;

    margin-bottom:
        12px;
}

.st-key-chat_quick_actions
[data-testid="stBaseButton-secondary"] {

    width:
        100% !important;

    min-height:
        36px !important;

    border-radius:
        999px !important;

    background:
        rgba(235,241,228,.83) !important;

    border:
        1px solid transparent !important;

    color:
        #31513E !important;

    box-shadow:
        none !important;

    font-size:
        11px !important;
}

.st-key-chat_quick_actions
[data-testid="stBaseButton-secondary"]:hover {

    background:
        #174A32 !important;

    color:
        #FFFFFF !important;

    border-color:
        #174A32 !important;
}

.st-key-chat_quick_actions
[data-testid="stBaseButton-secondary"]:hover * {

    color:
        #FFFFFF !important;
}


/* =========================================================
   CHAT INPUT
========================================================= */

.st-key-chat_composer {

    position:
        sticky;

    bottom:
        15px;

    z-index:
        50;

    margin-top:
        15px;

    padding:
        8px 10px !important;

    border-radius:
        28px;

    background:
        rgba(255,255,255,.92);

    border:
        1px solid #E7E8DF;

    box-shadow:
        0 10px 35px
        rgba(46,68,47,.10);
}

.st-key-chat_composer
[data-testid="stForm"] {

    border:
        none !important;

    background:
        transparent !important;
}

.composer-leaf {

    width:
        44px;

    height:
        44px;

    margin:
        auto;
}

.st-key-chat_composer
div[data-testid="stTextInput"] > div,

.st-key-chat_composer
div[data-testid="stTextInput"] > div > div,

.st-key-chat_composer
div[data-baseweb="input"],

.st-key-chat_composer
div[data-baseweb="base-input"] {

    background:
        transparent !important;

    border:
        none !important;

    box-shadow:
        none !important;
}

.st-key-chat_composer
input {

    height:
        50px !important;

    background:
        transparent !important;

    color:
        #294638 !important;

    -webkit-text-fill-color:
        #294638 !important;

    caret-color:
        #294638 !important;

    border:
        none !important;

    outline:
        none !important;

    box-shadow:
        none !important;

    font-size:
        15px !important;
}

.st-key-chat_composer
input::placeholder {

    color:
        #83908A !important;

    -webkit-text-fill-color:
        #83908A !important;

    opacity:
        1 !important;
}

.st-key-chat_composer
div[data-testid="stFormSubmitButton"]
button {

    width:
        52px !important;

    height:
        52px !important;

    min-width:
        52px !important;

    min-height:
        52px !important;

    border:
        none !important;

    border-radius:
        50% !important;

    padding:
        0 !important;

    background:
        #174A32 !important;

    color:
        #FFFFFF !important;

    box-shadow:
        0 8px 20px
        rgba(23,74,50,.18) !important;
}

.st-key-chat_composer
div[data-testid="stFormSubmitButton"]
button p {

    font-size:
        0 !important;

    margin:
        0 !important;
}

.st-key-chat_composer
div[data-testid="stFormSubmitButton"]
button p::before {

    content:
        "↑";

    font-size:
        24px;

    color:
        #FFFFFF;
}


/* =========================================================
   TRANSPORT POPUP
========================================================= */

div[role="dialog"] {

    border-radius:
        24px !important;
}

.transport-route-card {

    padding:
        15px 17px;

    border-radius:
        16px;

    background:
        #F4F7F0;

    border:
        1px solid #E0E8DB;

    margin:
        4px 0 12px;
}

.transport-route-title {

    color:
        #174A32;

    font-size:
        15px;

    font-weight:
        700;
}

.transport-option-card {

    min-height:
        150px;

    padding:
        16px;

    border-radius:
        18px;

    background:
        #FFFFFF;

    border:
        1px solid #E2E8DE;

    margin-bottom:
        8px;
}

.transport-option-name {

    color:
        #173F2B;

    font-size:
        17px;

    font-weight:
        700;

    margin-bottom:
        8px;
}

.transport-badge {

    display:
        inline-block;

    padding:
        4px 9px;

    border-radius:
        999px;

    background:
        #EAF2E5;

    color:
        #31513E;

    font-size:
        10px;

    margin-bottom:
        8px;
}

.transport-description {

    color:
        #66756C;

    font-size:
        12px;

    line-height:
        1.5;
}

div[role="dialog"] button {

    border-radius:
        999px !important;

    background:
        #F7F6EE !important;

    color:
        #174A32 !important;

    border:
        1px solid #9FB8A5 !important;

    box-shadow:
        none !important;
}

div[role="dialog"] button:hover {

    background:
        #174A32 !important;

    color:
        #FFFFFF !important;

    border-color:
        #174A32 !important;
}

div[role="dialog"] button:hover * {

    color:
        #FFFFFF !important;
}


/* =========================================================
   ALL CHOICE BUTTONS
========================================================= */

[class*="st-key-hotel_choice_box_"] button,
.st-key-continue_trip_button button,
.st-key-new_trip_button button,
[class*="st-key-hotel_prompt_yes_"] button,
[class*="st-key-hotel_prompt_no_"] button {

    width:
        100% !important;

    min-height:
        48px !important;

    background:
        #F7F6EE !important;

    color:
        #174A32 !important;

    border:
        1px solid #9FB8A5 !important;

    border-radius:
        12px !important;

    box-shadow:
        none !important;

    font-size:
        13px !important;

    font-weight:
        600 !important;

    transition:
        background .18s ease,
        color .18s ease,
        border-color .18s ease,
        transform .18s ease !important;
}

[class*="st-key-hotel_choice_box_"] button *,
.st-key-continue_trip_button button *,
.st-key-new_trip_button button *,
[class*="st-key-hotel_prompt_yes_"] button *,
[class*="st-key-hotel_prompt_no_"] button * {

    color:
        #174A32 !important;
}

[class*="st-key-hotel_choice_box_"] button:hover,
.st-key-continue_trip_button button:hover,
.st-key-new_trip_button button:hover,
[class*="st-key-hotel_prompt_yes_"] button:hover,
[class*="st-key-hotel_prompt_no_"] button:hover {

    background:
        #174A32 !important;

    color:
        #FFFFFF !important;

    border-color:
        #174A32 !important;

    transform:
        translateY(-1px);
}

[class*="st-key-hotel_choice_box_"] button:hover *,
.st-key-continue_trip_button button:hover *,
.st-key-new_trip_button button:hover *,
[class*="st-key-hotel_prompt_yes_"] button:hover *,
[class*="st-key-hotel_prompt_no_"] button:hover * {

    color:
        #FFFFFF !important;
}


/* =========================================================
   MOBILE
========================================================= */

@media(max-width:760px) {

    .block-container {

        padding:
            0 14px 120px !important;
    }

    .user-message-wrapper {

        max-width:
            88%;
    }

    .assistant-row-inner {

        max-width:
            94%;
    }

    .trip-summary-grid {

        grid-template-columns:
            1fr;
    }

    .hotel-options-heading,
    .hotel-options-sub,
    .hotel-prompt-card,
    .completion-card {

        margin-left:
            0;
    }
}


/* Additional styling for events and Streamlit's nested input wrappers */
.cultural-event-card {
    margin: 9px 0 5px 57px; padding: 15px 18px;
    border-radius: 17px; max-width: 735px;
    background: rgba(255,255,255,.95); border: 1px solid #E1E7DD;
    box-shadow: 0 6px 20px rgba(50,70,50,.055);
}
[class*="st-key-event_yes_box_"] button,
[class*="st-key-event_no_box_"] button {
    width: 100% !important; min-height: 48px !important;
    background: #F7F6EE !important; color: #174A32 !important;
    border: 1px solid #9FB8A5 !important; border-radius: 12px !important;
}
[class*="st-key-event_yes_box_"] button:hover,
[class*="st-key-event_no_box_"] button:hover {
    background: #174A32 !important; color: #FFFFFF !important;
}
[class*="st-key-event_yes_box_"] button:hover *,
[class*="st-key-event_no_box_"] button:hover * { color: #FFFFFF !important; }
.st-key-chat_composer [data-testid="stTextInput"],
.st-key-chat_composer [data-testid="stTextInput"] > div,
.st-key-chat_composer [data-testid="stTextInput"] > div > div,
.st-key-chat_composer [data-testid="stTextInputRootElement"],
.st-key-chat_composer [data-baseweb="input"],
.st-key-chat_composer [data-baseweb="base-input"],
.st-key-chat_composer [data-baseweb="input"] > div,
.st-key-chat_composer input, .st-key-chat_composer input:focus {
    background: #FFFFFF !important; background-color: #FFFFFF !important;
    border: none !important; box-shadow: none !important;
}
.st-key-chat_composer input {
    color: #294638 !important; -webkit-text-fill-color: #294638 !important;
    caret-color: #174A32 !important;
}
.st-key-chat_composer input::placeholder {
    color: #83908A !important; -webkit-text-fill-color: #83908A !important;
}
@media(max-width:760px) { .cultural-event-card { margin-left: 0; } }
</style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# RASA CONNECTION
# ============================================================

def get_bot_response(
    user_message,
    allow_empty=False,
):

    payload = {
        "sender":
            st.session_state.sender_id,

        "message":
            user_message,
    }

    try:

        response = requests.post(
            RASA_URL,
            json=payload,
            timeout=90,
        )

        response.raise_for_status()

        rasa_messages = (
            response.json()
        )

        if not rasa_messages:

            if allow_empty:
                return []

            return [
                {
                    "role":
                        "assistant",

                    "content":
                        (
                            "I understood your message, "
                            "but I do not have a response "
                            "for that yet."
                        ),

                    "timestamp":
                        current_time(),

                    "type":
                        "text",
                }
            ]

        formatted_messages = []

        pending_texts = []

        def flush_text_group():

            nonlocal pending_texts

            if not pending_texts:
                return

            if len(pending_texts) == 1:

                formatted_messages.append(
                    {
                        "role":
                            "assistant",

                        "content":
                            pending_texts[0],

                        "timestamp":
                            current_time(),

                        "type":
                            "text",
                    }
                )

            else:

                formatted_messages.append(
                    {
                        "role":
                            "assistant",

                        "sections":
                            pending_texts.copy(),

                        "timestamp":
                            current_time(),

                        "type":
                            "result_card",
                    }
                )

            pending_texts = []

        for rasa_message in rasa_messages:

            text_value = (
                rasa_message.get(
                    "text"
                )
            )

            if text_value:

                pending_texts.append(
                    text_value
                )

            buttons = (
                rasa_message.get(
                    "buttons"
                )
            )

            if buttons:

                flush_text_group()

                formatted_messages.append(
                    {
                        "role":
                            "assistant",

                        "timestamp":
                            current_time(),

                        "type":
                            "buttons",

                        "buttons":
                            buttons,
                    }
                )

            custom = (
                rasa_message.get(
                    "custom"
                )
            )

            if custom:

                flush_text_group()

                formatted_messages.append(
                    {
                        "role":
                            "assistant",

                        "timestamp":
                            current_time(),

                        "type":
                            "custom",

                        "custom":
                            custom,
                    }
                )

        flush_text_group()

        return formatted_messages


    except requests.exceptions.ConnectionError:

        return [
            {
                "role":
                    "assistant",

                "content":
                    (
                        "I cannot reach the TravelEco backend "
                        "right now. Please make sure Rasa "
                        "is running on port 5005."
                    ),

                "timestamp":
                    current_time(),

                "type":
                    "error",
            }
        ]


    except requests.exceptions.Timeout:

        return [
            {
                "role":
                    "assistant",

                "content":
                    (
                        "TravelEco is taking longer than "
                        "expected to respond. Please try again."
                    ),

                "timestamp":
                    current_time(),

                "type":
                    "error",
            }
        ]


    except (
        requests.exceptions.RequestException,
        ValueError,
    ) as error:

        return [
            {
                "role":
                    "assistant",

                "content":
                    (
                        f"TravelEco encountered a "
                        f"backend problem: {error}"
                    ),

                "timestamp":
                    current_time(),

                "type":
                    "error",
            }
        ]


# ============================================================
# FINAL SUMMARY STATE
# ============================================================

def maybe_add_trip_summary():
    """A summary must be added only AFTER the cultural-events decision."""
    s = st.session_state
    if s.trip_summary_added:
        return
    if not s.selected_transport_mode or not s.selected_hotel:
        return
    if not s.events_stage_complete:
        return
    s.messages.append({
        "role": "assistant",
        "type": "trip_summary",
        "timestamp": current_time(),
        "transport": s.selected_transport_mode,
        "hotel": s.selected_hotel,
        "context": s.selected_trip_context,
        "events_choice": s.event_choice,
        "events_count": len(s.events_found),
    })
    s.trip_summary_added = True
    s.flow_complete = True


# ============================================================
# NORMAL USER MESSAGE
# ============================================================

def process_message(user_message):
    """Handle typed events choices and human handover, preserving visible user text."""
    user_message = str(user_message or "").strip()
    if not user_message:
        return
    normalized = user_message.lower().strip(" !?.")

    # The user may answer the events prompt using the keyboard.
    if st.session_state.events_prompt_shown and not st.session_state.events_stage_complete:
        yes_words = {"yes", "yes please", "sure", "okay", "ok", "show events", "yes show events"}
        no_words = {"no", "no thanks", "no thank you", "skip", "not now", "not this time"}
        if normalized in yes_words or normalized in no_words:
            st.session_state.messages.append({
                "role": "user", "content": user_message,
                "timestamp": current_time(), "type": "text",
            })
            finish_events_choice(normalized in yes_words, show_user_message=False)
            return

    # Send a Rasa intent instead of relying on NLU recognition of every wording.
    human_words = (
        "human", "advisor", "agent", "speak to someone", "talk to someone",
        "speak to a person", "talk to a person", "human assistance",
        "connect me with someone", "support person",
    )
    rasa_message = "/request_human" if any(
        phrase in normalized for phrase in human_words
    ) else user_message

    st.session_state.messages.append({
        "role": "user", "content": user_message,
        "timestamp": current_time(), "type": "text",
    })
    st.session_state.messages.extend(get_bot_response(rasa_message))
    st.rerun()

    # ========================================================
    # DIRECT HUMAN HANDOVER DETECTION
    # ========================================================


# ============================================================
# DIRECT BUTTON MESSAGE
# ============================================================

def process_direct_message(
    display_text,
    rasa_payload,
):

    st.session_state.messages.append(
        {
            "role":
                "user",

            "content":
                display_text,

            "timestamp":
                current_time(),

            "type":
                "text",
        }
    )

    bot_messages = (
        get_bot_response(
            rasa_payload
        )
    )

    st.session_state.messages.extend(
        bot_messages
    )

    st.rerun()


# ============================================================
# TRANSPORT
# ============================================================

def process_transport_choice(
    mode,
    label,
    icon,
    message_index,
):

    # Resolve popup BEFORE slow API call.

    st.session_state.resolved_transport_messages[
        str(message_index)
    ] = mode

    st.session_state.selected_transport_mode = (
        mode
    )

    st.session_state.messages.append(
        {
            "role":
                "user",

            "content":
                f"{icon} {label}",

            "timestamp":
                current_time(),

            "type":
                "text",
        }
    )

    st.session_state.pending_transport_payload = (
        f'/provide_transport_mode'
        f'{{"transport_mode":"{mode}"}}'
    )

    st.rerun()


def process_pending_transport_response():
    """Close transport modal, calculate emissions, then fetch stays automatically."""
    s = st.session_state
    payload = s.pending_transport_payload
    if not payload:
        return
    s.pending_transport_payload = None
    with st.spinner("Calculating your selected transport…"):
        responses = get_bot_response(payload, allow_empty=True)
    s.messages.extend(responses)
    s.pending_hotel_search = True
    st.rerun()


def process_pending_hotel_search():
    """No additional prompt: hotels are loaded as soon as transport completes."""
    s = st.session_state
    if not s.pending_hotel_search:
        return
    s.pending_hotel_search = False
    with st.spinner("Searching for accommodation at your destination…"):
        responses = get_bot_response("/ask_accommodation", allow_empty=True)
    s.messages.extend(responses)
    has_hotels = any(
        m.get("type") == "custom"
        and (m.get("custom") or {}).get("type") == "hotel_options"
        and (m.get("custom") or {}).get("hotels")
        for m in responses
    )
    if not has_hotels:
        s.messages.append({
            "role": "assistant",
            "type": "hotel_unavailable",
            "timestamp": current_time(),
        })
    st.rerun()


def get_pending_transport_options():

    for index in range(
        len(st.session_state.messages) - 1,
        -1,
        -1,
    ):

        message = (
            st.session_state
            .messages[index]
        )

        if (
            message.get("type")
            != "custom"
        ):
            continue

        custom = (
            message.get(
                "custom",
                {}
            )
            or {}
        )

        if (
            custom.get("type")
            != "transport_options"
        ):
            continue

        if (
            str(index)
            in st.session_state
            .resolved_transport_messages
        ):
            continue

        return custom, index

    return None, None


@st.dialog(
    "Choose your preferred transport",
    width="large",
    dismissible=True,
)
def show_transport_dialog(
    custom,
    message_index,
):

    origin = custom.get(
        "origin",
        "Your origin",
    )

    destination = custom.get(
        "destination",
        "Your destination",
    )

    sustainability = custom.get(
        "sustainability_level",
        "medium",
    )

    st.markdown(
        (
            '<div class="transport-route-card">'

            '<div class="transport-route-title">'

            f'{safe(origin)} → '
            f'{safe(destination)}'

            '</div>'

            '<div>'

            '🌿 Sustainability: '

            f'{safe(sustainability)}'

            '</div>'

            '</div>'
        ),
        unsafe_allow_html=True,
    )

    options = custom.get(
        "options",
        []
    )

    if not options:

        st.warning(
            "No transport options were returned."
        )

        return

    for start in range(
        0,
        len(options),
        2,
    ):

        row = options[
            start:
            start + 2
        ]

        columns = st.columns(
            2,
            gap="medium",
        )

        for column_index, option in enumerate(
            row
        ):

            with columns[
                column_index
            ]:

                mode = option.get(
                    "mode",
                    ""
                )

                label = option.get(
                    "label",
                    mode.title(),
                )

                icon = option.get(
                    "icon",
                    "🌿",
                )

                badge = option.get(
                    "badge",
                    "",
                )

                description = (
                    option.get(
                        "description",
                        "",
                    )
                )

                st.markdown(
                    (
                        '<div class="transport-option-card">'

                        '<div class="transport-option-name">'

                        f'{safe(icon)} '
                        f'{safe(label)}'

                        '</div>'

                        '<span class="transport-badge">'

                        f'{safe(badge)}'

                        '</span>'

                        '<div class="transport-description">'

                        f'{safe(description)}'

                        '</div>'

                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )

                choose = st.button(
                    f"Choose {label}",
                    key=(
                        f"transport_choice_"
                        f"{message_index}_"
                        f"{mode}"
                    ),
                    use_container_width=True,
                    type="secondary",
                )

                if choose:

                    process_transport_choice(
                        mode,
                        label,
                        icon,
                        message_index,
                    )


# ============================================================
# HOTEL PROMPT
# ============================================================

def process_hotel_prompt_choice(
    choice,
    message_index,
):

    st.session_state.resolved_hotel_prompts[
        str(message_index)
    ] = choice

    if choice == "yes":

        st.session_state.messages.append(
            {
                "role":
                    "user",

                "content":
                    "🏨 Yes, show me stays",

                "timestamp":
                    current_time(),

                "type":
                    "text",
            }
        )

        with st.spinner(
            "Searching live accommodation…"
        ):

            bot_messages = (
                get_bot_response(
                    "/ask_accommodation"
                )
            )

        st.session_state.messages.extend(
            bot_messages
        )

    else:

        st.session_state.messages.extend(
            [
                {
                    "role":
                        "user",

                    "content":
                        "Not right now",

                    "timestamp":
                        current_time(),

                    "type":
                        "text",
                },

                {
                    "role":
                        "assistant",

                    "content":
                        (
                            "No problem 🌿 We can look "
                            "at accommodation later. "
                            "What else would you like "
                            "help with?"
                        ),

                    "timestamp":
                        current_time(),

                    "type":
                        "text",
                },
            ]
        )

    st.rerun()


def render_hotel_prompt(
    message,
    message_index,
):

    resolution = (
        st.session_state
        .resolved_hotel_prompts
        .get(
            str(message_index)
        )
    )

    st.markdown(
        (
            '<div class="hotel-prompt-card">'

            '<b>'
            '🏨 Would you like accommodation '
            'recommendations?'
            '</b>'

            '<br>'

            'I can search for eco-friendly stays '
            'that match your destination and dates.'

            '</div>'
        ),
        unsafe_allow_html=True,
    )

    if resolution == "yes":

        st.caption(
            "✓ Accommodation search requested"
        )

        return

    if resolution == "no":

        st.caption(
            "✓ Accommodation skipped for now"
        )

        return

    left, right = st.columns(
        2,
        gap="medium",
    )

    with left:

        with st.container(
            key=f"hotel_prompt_yes_{message_index}"
        ):

            yes_hotels = st.button(
                "🏨 Yes, show me stays",
                key=(
                    f"hotel_prompt_yes_button_"
                    f"{message_index}"
                ),
                use_container_width=True,
                type="secondary",
            )

    with right:

        with st.container(
            key=f"hotel_prompt_no_{message_index}"
        ):

            no_hotels = st.button(
                "Not right now",
                key=(
                    f"hotel_prompt_no_button_"
                    f"{message_index}"
                ),
                use_container_width=True,
                type="secondary",
            )

    if yes_hotels:

        process_hotel_prompt_choice(
            "yes",
            message_index,
        )

    if no_hotels:

        process_hotel_prompt_choice(
            "no",
            message_index,
        )


# ============================================================
# HOTEL SELECTION
# ============================================================


# ============================================================
# AUTOMATIC HOTEL RECOVERY AND CULTURAL EVENTS
# ============================================================

def render_hotel_unavailable(message, message_index):
    s = st.session_state
    if s.selected_hotel:
        return
    st.warning("Live accommodation results are unavailable for this trip.")
    if st.button(
        "Continue without accommodation",
        key=f"skip_hotel_{message_index}",
        use_container_width=False,
        type="secondary",
    ):
        s.selected_hotel = {"name": "Not selected", "rating": "—", "total": "—"}
        if not s.events_prompt_shown:
            s.events_prompt_shown = True
            s.messages.append({
                "role": "assistant", "type": "events_prompt",
                "timestamp": current_time(),
            })
        st.rerun()


def finish_events_choice(yes, show_user_message=True):
    """Yes: fetch live cultural events; No: go straight to final summary."""
    s = st.session_state
    if s.events_stage_complete or not s.events_prompt_shown:
        return
    s.event_choice = "yes" if yes else "no"
    if show_user_message:
        s.messages.append({
            "role": "user", "type": "text", "timestamp": current_time(),
            "content": "🎭 Yes, show cultural events" if yes else "No, thanks",
        })
    if yes:
        with st.spinner("Finding cultural events for your travel dates…"):
            responses = get_bot_response("/ask_events", allow_empty=True)
        s.messages.extend(responses)
        s.events_found = []
        for response in responses:
            custom = response.get("custom") or {}
            if response.get("type") == "custom" and custom.get("type") == "event_options":
                s.events_found = custom.get("events") or []
        if not responses:
            s.messages.append({
                "role": "assistant", "type": "text", "timestamp": current_time(),
                "content": "I could not retrieve cultural events right now. Your trip plan is still ready.",
            })
    else:
        s.messages.append({
            "role": "assistant", "type": "text", "timestamp": current_time(),
            "content": "No problem — we'll finish the trip without cultural events.",
        })
    s.events_stage_complete = True
    maybe_add_trip_summary()
    st.rerun()


def render_events_prompt(message, message_index):
    if st.session_state.events_stage_complete:
        return
    st.markdown(
        '<div class="hotel-prompt-card"><b>🎭 Would you like to explore cultural events '
        'during your trip?</b><br>Find exhibitions, festivals, performances and local '
        'experiences near your destination.</div>',
        unsafe_allow_html=True,
    )
    yes_col, no_col = st.columns(2, gap="medium")
    with yes_col:
        with st.container(key=f"event_yes_box_{message_index}"):
            yes = st.button("🎭 Yes, show events", key=f"events_yes_{message_index}",
                            use_container_width=True, type="secondary")
    with no_col:
        with st.container(key=f"event_no_box_{message_index}"):
            no = st.button("Not this time", key=f"events_no_{message_index}",
                           use_container_width=True, type="secondary")
    if yes:
        finish_events_choice(True)
    if no:
        finish_events_choice(False)


def render_event_options(message, message_index):
    custom = message.get("custom") or {}
    events = custom.get("events") or []
    destination = custom.get("destination") or "your destination"
    st.markdown(
        f'<div class="hotel-options-heading">🎭 Cultural events in {safe(destination)}</div>',
        unsafe_allow_html=True,
    )
    if not events:
        st.info("No matching cultural events could be confirmed for your dates. Check local calendars nearer the trip.")
        return
    for item_index, event in enumerate(events[:5]):
        st.markdown(
            '<div class="cultural-event-card">'
            f'<div class="hotel-number">Event {item_index + 1}</div>'
            f'<div class="hotel-name">{safe(event.get("title", "Cultural event"))}</div>'
            f'<div class="hotel-detail">📅 {safe(event.get("date", "Date not listed"))} '
            f'{safe(event.get("time", ""))}</div>'
            f'<div class="hotel-detail">📍 {safe(event.get("venue", "Venue not listed"))}</div>'
            f'<div class="hotel-amenities">{safe(event.get("category", "Cultural activity"))}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        link = str(event.get("link") or "")
        if link.startswith(("https://", "http://")):
            st.link_button("View event details ↗", link,
                           key=f"event_link_{message_index}_{item_index}")
    st.caption("Event availability and dates must be confirmed with organisers. No bookings were made.")

def process_hotel_choice(hotel, message_index, custom):
    s = st.session_state
    s.resolved_hotel_messages[str(message_index)] = hotel.get(
        "id", hotel.get("name", "hotel")
    )
    s.selected_hotel = hotel
    s.selected_trip_context = custom.get("trip_context", {}) or {}
    hotel_name = hotel.get("name", "Selected accommodation")
    s.messages.extend([
        {"role": "user", "type": "text", "timestamp": current_time(),
         "content": f"🏨 I choose {hotel_name}"},
        {"role": "assistant", "type": "text", "timestamp": current_time(),
         "content": f"Great — {hotel_name} is now included in your TravelEco trip plan."},
    ])
    # Do NOT end the trip here. Always offer the cultural-events choice first.
    if not s.events_prompt_shown and not s.events_stage_complete:
        s.events_prompt_shown = True
        s.messages.append({
            "role": "assistant", "type": "events_prompt", "timestamp": current_time(),
        })
    st.rerun()


def render_hotel_options(
    message,
    message_index,
):

    custom = (
        message.get(
            "custom",
            {},
        )
        or {}
    )

    hotels = custom.get(
        "hotels",
        []
    )

    destination = custom.get(
        "destination",
        "your destination",
    )

    selected_id = (
        st.session_state
        .resolved_hotel_messages
        .get(
            str(message_index)
        )
    )

    if selected_id:

        selected = next(
            (
                hotel
                for hotel in hotels
                if hotel.get("id")
                == selected_id
            ),
            st.session_state
            .selected_hotel,
        )

        if selected:

            st.markdown(
                (
                    '<div class="message-row assistant">'

                    '<div class="assistant-row-inner">'

                    f'<div class="bot-avatar">'
                    f'{leaf_svg()}'
                    '</div>'

                    '<div class="assistant-content">'

                    '<div class="hotel-selected-card">'

                    '🏨 <b>Selected stay:</b> '

                    f'{safe(selected.get("name"))}'

                    '<br>'

                    '<b>Total stay:</b> '

                    f'{safe(selected.get("total", "N/A"))}'

                    '</div>'

                    '</div>'

                    '</div>'

                    '</div>'
                ),
                unsafe_allow_html=True,
            )

        return

    st.markdown(
        (
            '<div class="hotel-options-heading">'

            f'🏨 Choose your stay in '
            f'{safe(destination)}'

            '</div>'

            '<div class="hotel-options-sub">'

            'Select one accommodation to include '
            'in your final TravelEco trip plan.'

            '</div>'
        ),
        unsafe_allow_html=True,
    )

    if not hotels:
        return

    columns = st.columns(
        len(hotels),
        gap="medium",
    )

    for index, hotel in enumerate(
        hotels
    ):

        with columns[index]:

            amenities = hotel.get(
                "amenities",
                [],
            )

            if (
                isinstance(
                    amenities,
                    list,
                )
                and
                amenities
            ):

                amenities_text = (
                    ", ".join(
                        amenities[:4]
                    )
                )

            else:

                amenities_text = str(
                    amenities
                    or "Not listed"
                )

            st.markdown(
                (
                    '<div class="hotel-card">'

                    '<div class="hotel-number">'

                    f'Option {index + 1}'

                    '</div>'

                    '<div class="hotel-name">'

                    f'{safe(hotel.get("name", "Stay"))}'

                    '</div>'

                    '<div class="hotel-detail">'

                    '⭐ Rating: '

                    f'{safe(hotel.get("rating", "N/A"))} '

                    '('

                    f'{safe(hotel.get("reviews", "N/A"))} '

                    'reviews)'

                    '</div>'

                    '<div class="hotel-detail">'

                    '🌙 Per night: '

                    f'{safe(hotel.get("nightly", "N/A"))}'

                    '</div>'

                    '<div class="hotel-detail">'

                    '💶 Total stay: '

                    f'{safe(hotel.get("total", "N/A"))}'

                    '</div>'

                    '<div class="hotel-amenities">'

                    'Amenities: '

                    f'{safe(amenities_text)}'

                    '</div>'

                    '</div>'
                ),
                unsafe_allow_html=True,
            )

            with st.container(
                key=(
                    f"hotel_choice_box_"
                    f"{message_index}_"
                    f"{index}"
                )
            ):

                choose_hotel = (
                    st.button(
                        f"Choose option {index + 1}",
                        key=(
                            f"hotel_choice_"
                            f"{message_index}_"
                            f"{index}"
                        ),
                        use_container_width=True,
                        type="secondary",
                    )
                )

            if choose_hotel:

                process_hotel_choice(
                    hotel,
                    message_index,
                    custom,
                )


# ============================================================
# HEADER
# ============================================================

def render_header():

    left_col, right_col = st.columns(
        [8, 2],
        vertical_alignment="center",
    )

    with left_col:

        st.markdown(
            (
                '<div class="travel-brand">'

                f'<div class="brand-leaf">'
                f'{leaf_svg()}'
                '</div>'

                '<div>'

                '<div class="brand-title">'
                'TravelEco'
                '</div>'

                '<div class="brand-subtitle">'
                'Sustainable AI Travel Companion'
                '</div>'

                '</div>'

                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with right_col:

        with st.container(
            key="new_chat_area"
        ):

            new_chat = st.button(
                "＋ New Chat",
                use_container_width=True,
                key="new_chat_button",
                type="secondary",
            )

    st.markdown(
        '<div class="header-divider"></div>',
        unsafe_allow_html=True,
    )

    if new_chat:

        fresh_trip_state(
            clear_messages=False
        )

        st.session_state.messages = [
            {
                "role":
                    "assistant",

                "content":
                    WELCOME_MESSAGE,

                "timestamp":
                    current_time(),

                "type":
                    "text",
            }
        ]

        st.rerun()


# ============================================================
# BASIC MESSAGE RENDERING
# ============================================================

def render_user_message(
    message,
):

    content = safe(
        message.get(
            "content",
            "",
        )
    ).replace(
        "\n",
        "<br>",
    )

    timestamp = safe(
        message.get(
            "timestamp",
            "",
        )
    )

    st.markdown(
        (
            '<div class="message-row user">'

            '<div class="user-message-wrapper">'

            f'<div class="user-bubble">'
            f'{content}'
            '</div>'

            f'<div class="user-meta">'
            f'{timestamp}'
            '</div>'

            '</div>'

            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_assistant_text(
    message,
):

    content = safe(
        message.get(
            "content",
            "",
        )
    ).replace(
        "\n",
        "<br>",
    )

    timestamp = safe(
        message.get(
            "timestamp",
            "",
        )
    )

    st.markdown(
        (
            '<div class="message-row assistant">'

            '<div class="assistant-row-inner">'

            f'<div class="bot-avatar">'
            f'{leaf_svg()}'
            '</div>'

            '<div class="assistant-content">'

            f'<div class="assistant-bubble">'
            f'{content}'
            '</div>'

            f'<div class="assistant-meta">'
            f'{timestamp}'
            '</div>'

            '</div>'

            '</div>'

            '</div>'
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# RESULT CARDS
# ============================================================

def infer_result_header(
    sections,
):

    combined = (
        " ".join(
            sections
        )
        .lower()
    )

    if (
        "carbon estimate"
        in combined
        or
        "estimated emissions"
        in combined
    ):

        return (
            "🌱 Carbon estimate"
        )

    if (
        "transport recommendation"
        in combined
        or
        "recommended transport"
        in combined
    ):

        return (
            "🌿 Transport recommendation"
        )

    if "flight" in combined:

        return (
            "✈️ Flight options"
        )

    if (
        "hotel" in combined
        or
        "accommodation" in combined
    ):

        return (
            "🏨 Eco-friendly stays"
        )

    return (
        "TravelEco result"
    )


def render_result_card(
    message,
):

    sections = [
        str(section).strip()

        for section
        in message.get(
            "sections",
            [],
        )

        if str(
            section
        ).strip()
    ]

    if not sections:
        return

    body = ""

    for section in sections:

        rendered = safe(
            section
        ).replace(
            "\n",
            "<br>",
        )

        body += (
            '<div class="result-card-section">'
            f'{rendered}'
            '</div>'
        )

    st.markdown(
        (
            '<div class="message-row assistant">'

            '<div class="assistant-row-inner">'

            f'<div class="bot-avatar">'
            f'{leaf_svg()}'
            '</div>'

            '<div class="assistant-content">'

            '<div class="result-card">'

            '<div class="result-card-header">'

            f'{safe(infer_result_header(sections))}'

            '</div>'

            f'{body}'

            '</div>'

            '<div class="assistant-meta">'

            f'{safe(message.get("timestamp", ""))}'

            '</div>'

            '</div>'

            '</div>'

            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_error_message(
    message,
):

    st.markdown(
        (
            '<div class="backend-warning">'

            '⚠️ '

            f'{safe(message.get("content", ""))}'

            '</div>'
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# RASA BUTTONS
# ============================================================

def render_rasa_buttons(
    message,
    message_index,
):

    buttons = message.get(
        "buttons",
        []
    )

    if not buttons:
        return

    columns = st.columns(
        min(
            len(buttons),
            4,
        )
    )

    for index, button in enumerate(
        buttons
    ):

        title = button.get(
            "title",
            "Option",
        )

        payload = button.get(
            "payload",
            title,
        )

        with columns[
            index % len(columns)
        ]:

            clicked = st.button(
                title,
                key=(
                    f"rasa_button_"
                    f"{message_index}_"
                    f"{index}"
                ),
                use_container_width=True,
            )

            if clicked:

                process_direct_message(
                    title,
                    payload,
                )


# ============================================================
# HUMAN HANDOVER CARD
# ============================================================

def render_handover_payload(
    custom,
    timestamp,
):

    context = (
        custom.get(
            "trip_context",
            {},
        )
        or {}
    )

    labels = {
        "origin":
            "From",

        "destination":
            "To",

        "start_date":
            "Departure",

        "end_date":
            "Return",

        "budget":
            "Budget",

        "sustainability_level":
            "Sustainability",

        "transport_mode":
            "Transport",
    }

    items = []

    for key, label in labels.items():

        value = context.get(
            key
        )

        if value in (
            None,
            "",
            "null",
        ):
            continue

        if key == "budget":

            value = (
                f"€{value}"
            )

        items.append(
            (
                f"<b>{safe(label)}:</b> "
                f"{safe(value)}"
            )
        )

    context_html = (
        "<br>".join(
            items
        )
    )

    st.markdown(
        (
            '<div class="message-row assistant">'

            '<div class="assistant-row-inner">'

            f'<div class="bot-avatar">'
            f'{leaf_svg()}'
            '</div>'

            '<div class="assistant-content">'

            '<div class="handover-card">'

            '<div class="handover-title">'

            '👤 Human support context prepared'

            '</div>'

            '<div class="handover-subtitle">'

            'Your trip details and recent conversation '
            'have been packaged for an advisor. '
            'This prototype demonstrates the handover '
            'flow and is not connected to a live '
            'support agent.'

            '</div>'

            '<div class="handover-context">'

            f'{context_html}'

            '</div>'

            '</div>'

            '<div class="assistant-meta">'

            f'{safe(timestamp)}'

            '</div>'

            '</div>'

            '</div>'

            '</div>'
        ),
        unsafe_allow_html=True,
    )


# ============================================================
# FINAL TRIP SUMMARY
# ============================================================

def render_trip_summary(message):
    context = message.get("context", {}) or {}
    hotel = message.get("hotel", {}) or {}
    mode = message.get("transport", "")
    events = "Yes" if message.get("events_choice") == "yes" else "No"
    if events == "Yes":
        events = f"Yes ({message.get('events_count', 0)} results shown)"
    st.markdown(
        f'<div class="message-row assistant"><div class="assistant-row-inner">'
        f'<div class="bot-avatar">{leaf_svg()}</div><div class="assistant-content">'
        f'<div class="trip-summary-card"><div class="trip-summary-header">'
        f'🌿 Your TravelEco trip plan is ready</div><div class="trip-summary-body">'
        f'<div class="trip-summary-grid">'
        f'<div class="trip-summary-item"><b>Route</b><br>{safe(context.get("origin", "—"))} '
        f'→ {safe(context.get("destination", "—"))}</div>'
        f'<div class="trip-summary-item"><b>Dates</b><br>{safe(context.get("start_date", "—"))} '
        f'→ {safe(context.get("end_date", "—"))}</div>'
        f'<div class="trip-summary-item"><b>Budget</b><br>€{safe(context.get("budget", "—"))}</div>'
        f'<div class="trip-summary-item"><b>Sustainability</b><br>'
        f'{safe(str(context.get("sustainability_level", "—")).title())}</div>'
        f'</div><div class="trip-summary-choice"><b>Transport:</b> '
        f'{safe(transport_label(mode))}<br><b>Accommodation:</b> 🏨 '
        f'{safe(hotel.get("name", "—"))}<br><b>Hotel rating:</b> '
        f'{safe(hotel.get("rating", "N/A"))} &nbsp; • &nbsp; <b>Total stay:</b> '
        f'{safe(hotel.get("total", "N/A"))}<br><b>Cultural events explored:</b> '
        f'{safe(events)}</div><div class="trip-summary-finish">'
        f'✅ Your TravelEco planning flow is complete.</div></div></div>'
        f'</div></div></div>', unsafe_allow_html=True,
    )


# ============================================================
# CUSTOM RASA PAYLOADS
# ============================================================

def render_custom_payload(message, message_index):
    custom = message.get("custom", {}) or {}
    custom_type = custom.get("type")
    if custom_type == "transport_options":
        origin = custom.get("origin", "your origin")
        destination = custom.get("destination", "your destination")
        selected = st.session_state.resolved_transport_messages.get(str(message_index))
        if selected:
            content = f"Transport selected for {origin} → {destination}: {transport_label(selected)}"
        else:
            content = f"I have prepared transport options for {origin} → {destination}."
        render_assistant_text({"content": content, "timestamp": message.get("timestamp", "")})
    elif custom_type == "hotel_options":
        render_hotel_options(message, message_index)
    elif custom_type == "event_options":
        render_event_options(message, message_index)
    elif custom_type == "human_handover":
        render_handover_payload(custom, message.get("timestamp", ""))
    elif custom.get("text"):
        render_assistant_text({"content": custom["text"], "timestamp": message.get("timestamp", "")})


# ============================================================
# CHAT HISTORY
# ============================================================

def render_chat_history():
    for index, message in enumerate(st.session_state.messages):
        if message.get("role") == "user":
            render_user_message(message)
            continue
        message_type = message.get("type", "text")
        if message_type == "text":
            render_assistant_text(message)
        elif message_type == "result_card":
            render_result_card(message)
        elif message_type == "error":
            render_error_message(message)
        elif message_type == "buttons":
            render_rasa_buttons(message, index)
        elif message_type == "custom":
            render_custom_payload(message, index)
        elif message_type == "hotel_prompt":
            # Backward compatibility for old messages; the new trip never adds one.
            render_hotel_prompt(message, index)
        elif message_type == "hotel_unavailable":
            render_hotel_unavailable(message, index)
        elif message_type == "events_prompt":
            render_events_prompt(message, index)
        elif message_type == "trip_summary":
            render_trip_summary(message)


# ============================================================
# COMPLETION ACTIONS
# ============================================================

def render_completion_actions():

    st.markdown(
        (
            '<div class="completion-card">'

            '<b>🌿 Have a great trip!</b>'

            '<br>'

            'Would you like to continue planning '
            'this trip or start a new one?'

            '</div>'
        ),
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        2,
        gap="medium",
    )

    with left:

        with st.container(
            key="continue_trip_button"
        ):

            continue_trip = st.button(
                "🌱 Continue this trip",
                key="continue_completed_trip",
                use_container_width=True,
                type="secondary",
            )

    with right:

        with st.container(
            key="new_trip_button"
        ):

            new_trip = st.button(
                "＋ Plan a new trip",
                key="start_new_completed_trip",
                use_container_width=True,
                type="secondary",
            )

    if continue_trip:

        st.session_state.flow_complete = False

        st.session_state.messages.append(
            {
                "role":
                    "assistant",

                "content":
                    (
                        "Of course 🌿 We can continue "
                        "with this trip. What else "
                        "would you like help with?"
                    ),

                "timestamp":
                    current_time(),

                "type":
                    "text",
            }
        )

        st.rerun()

    if new_trip:

        # New sender ID = completely new Rasa tracker.
        # Existing UI history can remain visible.

        fresh_trip_state(
            clear_messages=False
        )

        st.session_state.messages.append(
            {
                "role":
                    "assistant",

                "content":
                    "🌿 Let's plan another trip!",

                "timestamp":
                    current_time(),

                "type":
                    "text",
            }
        )

        # Start the form directly.
        bot_messages = (
            get_bot_response(
                "/plan_trip",
                allow_empty=True,
            )
        )

        if bot_messages:

            st.session_state.messages.extend(
                bot_messages
            )

        st.rerun()


# ============================================================
# QUICK ACTIONS
# ============================================================

def render_quick_actions():

    with st.container(
        key="chat_quick_actions"
    ):

        c1, c2, c3, c4, c5 = (
            st.columns(
                5,
                gap="small",
            )
        )

        with c1:

            best_route = st.button(
                "🌱 Best route",
                use_container_width=True,
                key="qa_route",
                type="secondary",
            )

        with c2:

            carbon = st.button(
                "♻ Carbon estimate",
                use_container_width=True,
                key="qa_carbon",
                type="secondary",
            )

        with c3:

            hotel = st.button(
                "🏨 Eco stays",
                use_container_width=True,
                key="qa_hotel",
                type="secondary",
            )

        with c4:

            flights = st.button(
                "✈️ Flights",
                use_container_width=True,
                key="qa_flights",
                type="secondary",
            )

        with c5:

            human = st.button(
                "👤 Human help",
                use_container_width=True,
                key="qa_human",
                type="secondary",
            )

    if best_route:

        process_direct_message(
            "Recommend the best transport "
            "option for my trip.",
            "/ask_transport",
        )

    if carbon:

        process_direct_message(
            "What are the carbon emissions "
            "for my trip?",
            "/ask_carbon",
        )

    if hotel:

        process_direct_message(
            "Show me eco-friendly accommodation.",
            "/ask_accommodation",
        )

    if flights:

        process_direct_message(
            "Show me flight options.",
            "/ask_flights",
        )

    if human:

        process_direct_message(
            "I need human help.",
            "/request_human",
        )


# ============================================================
# CHAT INPUT
# ============================================================

def submit_typed_chat_message():
    """Send typed text on Enter or arrow-click; clear before next rendering."""
    message = str(st.session_state.get("chat_text_input", "") or "").strip()
    if not message:
        return
    # This callback executes before Streamlit re-renders the widget.
    st.session_state["chat_text_input"] = ""
    process_message(message)


def render_chat_input():
    placeholder = (
        "Choose an option above, or type a message..."
        if st.session_state.flow_complete
        else "Ask anything about your trip..."
    )

    with st.container(key="chat_composer"):
        leaf_col, input_col, button_col = st.columns(
            [0.75, 10.6, 0.9],
            vertical_alignment="center",
            gap="small",
        )
        with leaf_col:
            st.markdown(
                f'<div class="composer-leaf">{leaf_svg()}</div>',
                unsafe_allow_html=True,
            )
        with input_col:
            st.text_input(
                "Message",
                placeholder=placeholder,
                label_visibility="collapsed",
                key="chat_text_input",
                on_change=submit_typed_chat_message,
            )
        with button_col:
            st.button(
                "↑",
                key="chat_send_button",
                type="primary",
                use_container_width=True,
                on_click=submit_typed_chat_message,
            )

    # Keep the original dark-green circular send-button styling without
    # retaining the form that could discard typed messages on submit.
    st.markdown(
        """
        <style>
        .st-key-chat_composer .st-key-chat_send_button button,
        .st-key-chat_composer [data-testid="stButton"] button[kind="primary"] {
            width: 52px !important;
            height: 52px !important;
            min-width: 52px !important;
            min-height: 52px !important;
            border: none !important;
            border-radius: 50% !important;
            padding: 0 !important;
            background: #174A32 !important;
            color: #FFFFFF !important;
            font-size: 24px !important;
            box-shadow: 0 8px 20px rgba(23,74,50,.18) !important;
        }
        .st-key-chat_composer .st-key-chat_send_button button:hover {
            background: #255C43 !important;
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN
# ============================================================

def main():
    initialize_session_state()
    inject_css()
    render_header()
    render_chat_history()

    # Execute jobs one at a time between reruns to avoid an open dialog
    # while the API request is in progress.
    if st.session_state.pending_transport_payload:
        process_pending_transport_response()
    if st.session_state.pending_hotel_search:
        process_pending_hotel_search()

    pending_transport, pending_index = get_pending_transport_options()
    if pending_transport is not None:
        show_transport_dialog(pending_transport, pending_index)

    if st.session_state.flow_complete:
        render_completion_actions()
    else:
        render_quick_actions()
    render_chat_input()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()