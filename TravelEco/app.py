import html

import streamlit as st





# ============================================================

# PAGE CONFIGURATION

# ============================================================



st.set_page_config(

    page_title="TravelEco",

    page_icon="🌿",

    layout="wide",

    initial_sidebar_state="collapsed",

)





# ============================================================

# SESSION STATE

# ============================================================



if "page" not in st.session_state:

    st.session_state.page = "landing"



# ============================================================

# GLOBAL CSS

# ============================================================



def inject_css():



    st.markdown(

        """

<style>



/* =========================================================

   REMOVE DEFAULT STREAMLIT UI

========================================================= */



#MainMenu {

    visibility: hidden !important;

}



footer {

    visibility: hidden !important;

}



header[data-testid="stHeader"] {

    display: none !important;

}



[data-testid="stToolbar"] {

    display: none !important;

}



[data-testid="stDecoration"] {

    display: none !important;

}



.stDeployButton {

    display: none !important;

}





/* =========================================================

   PAGE

========================================================= */



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

            circle at 4% 35%,

            rgba(220, 233, 212, 0.92),

            transparent 34%

        ),



        radial-gradient(

            circle at 96% 20%,

            rgba(227, 237, 219, 0.85),

            transparent 32%

        ),



        radial-gradient(

            circle at 77% 97%,

            rgba(242, 232, 204, 0.74),

            transparent 38%

        ),



        linear-gradient(

            135deg,

            #F7F6EE 0%,

            #FAF8F0 48%,

            #F1F5EB 100%

        ) !important;



    color: #173F2B;

}





.block-container {



    max-width: 100% !important;



    padding:

        0 24px 60px 24px !important;

}





/* =========================================================

   LANDING HERO

========================================================= */



.hero-shell {



    width: 100%;



    text-align: center;



    padding-top: 10vh;



    margin-bottom: 38px;

}





.hero-eyebrow {



    color: #456B55;



    font-size: 13px;



    line-height: 1;



    font-weight: 600;



    text-transform: uppercase;



    letter-spacing: 6px;



    margin-bottom: 30px;

}





.hero-title {



    color: #173F2B;



    font-family:

        Inter,

        "Helvetica Neue",

        Helvetica,

        Arial,

        sans-serif;



    font-size:

        clamp(

            52px,

            5.6vw,

            82px

        );



    font-weight: 350;



    line-height: 0.99;



    letter-spacing: -0.055em;



    margin: 0 auto;



    max-width: 850px;

}





/* =========================================================

   LANDING CARD

========================================================= */



.st-key-hero_card {



    width:

        min(

            1000px,

            92vw

        ) !important;



    margin-left: auto !important;



    margin-right: auto !important;



    padding:

        21px 24px 20px 24px !important;



    background:

        rgba(

            255,

            255,

            255,

            0.82

        );



    border:

        1px solid

        rgba(

            255,

            255,

            255,

            0.92

        );



    border-radius: 32px;



    box-shadow:

        0 22px 60px

        rgba(

            58,

            76,

            54,

            0.09

        );



    backdrop-filter:

        blur(18px);

}





.st-key-hero_card

[data-testid="stForm"] {



    border: none !important;



    padding: 0 !important;



    background:

        transparent !important;

}





/* =========================================================

   LEAF ICON

========================================================= */



.leaf-orb {



    width: 58px;



    height: 58px;



    border-radius: 50%;



    background: #EEF3E9;



    display: flex;



    align-items: center;



    justify-content: center;



    margin: auto;

}





.leaf-orb svg {



    width: 31px;



    height: 31px;



    stroke: #5C8066;



    stroke-width: 1.7;



    fill: none;

}





/* =========================================================

   LANDING INPUT

========================================================= */



.st-key-hero_card

div[data-testid="stTextInput"] {



    margin: 0 !important;

}





.st-key-hero_card

div[data-testid="stTextInput"] > div,



.st-key-hero_card

div[data-testid="stTextInput"] > div > div,



.st-key-hero_card

div[data-baseweb="input"],



.st-key-hero_card

div[data-baseweb="base-input"] {



    background:

        transparent !important;



    background-color:

        transparent !important;



    border:

        none !important;



    box-shadow:

        none !important;

}





.st-key-hero_card input {



    height: 62px !important;



    background:

        transparent !important;



    background-color:

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

        20px !important;



    font-weight:

        400 !important;



    padding-left:

        8px !important;

}





.st-key-hero_card

input::placeholder {



    color:

        #7B817C !important;



    -webkit-text-fill-color:

        #7B817C !important;



    opacity:

        1 !important;

}





/* =========================================================

   LANDING SEND BUTTON

========================================================= */



.st-key-hero_card

div[data-testid="stFormSubmitButton"] {



    display: flex !important;



    justify-content: center !important;



    align-items: center !important;

}





.st-key-hero_card

div[data-testid="stFormSubmitButton"]

button {



    width:

        62px !important;



    height:

        62px !important;



    min-width:

        62px !important;



    min-height:

        62px !important;



    max-width:

        62px !important;



    max-height:

        62px !important;



    padding:

        0 !important;



    margin:

        0 auto !important;



    border:

        none !important;



    border-radius:

        50% !important;



    background:

        #285E3D !important;



    color:

        #FFFFFF !important;



    box-shadow:

        0 10px 24px

        rgba(

            35,

            78,

            49,

            0.20

        ) !important;

}





.st-key-hero_card

div[data-testid="stFormSubmitButton"]

button:hover {



    background:

        #214F34 !important;



    transform:

        translateY(-2px);



    box-shadow:

        0 14px 28px

        rgba(

            35,

            78,

            49,

            0.27

        ) !important;

}





/* Hide Streamlit Submit text */



.st-key-hero_card

div[data-testid="stFormSubmitButton"]

button p {



    font-size:

        0 !important;



    margin:

        0 !important;



    padding:

        0 !important;

}





/* Replace Submit with arrow */



.st-key-hero_card

div[data-testid="stFormSubmitButton"]

button p::before {



    content: "↑";



    font-size:

        28px !important;



    font-weight:

        300 !important;



    color:

        #FFFFFF !important;



    line-height:

        1 !important;

}





/* =========================================================

   LANDING DIVIDER

========================================================= */



.prompt-divider {



    width: 100%;



    height: 1px;



    background: #DFE5DA;



    margin:

        12px 0 18px 0;

}





/* =========================================================

   LANDING SUGGESTIONS

========================================================= */



.st-key-hero_card

[data-testid="stBaseButton-secondary"] {



    width:

        100% !important;



    min-height:

        43px !important;



    padding:

        8px 12px !important;



    border-radius:

        24px !important;



    border:

        1px solid

        #D6DED1 !important;



    background:

        rgba(

            250,

            250,

            245,

            0.66

        ) !important;



    color:

        #3D5C4B !important;



    font-size:

        13px !important;



    font-weight:

        500 !important;



    white-space:

        nowrap !important;



    box-shadow:

        none !important;

}





.st-key-hero_card

[data-testid="stBaseButton-secondary"]:hover {



    background:

        #EEF4E9 !important;



    border-color:

        #B7C9B4 !important;



    color:

        #244A33 !important;



    transform:

        translateY(-1px);

}





/* =========================================================

   CHAT PAGE HEADER

========================================================= */



.chat-header-wrapper {



    width:

        min(

            900px,

            92vw

        );



    margin:

        0 auto;



    padding-top:

        48px;



    margin-bottom:

        36px;

}





.chat-header {



    display: flex;



    justify-content:

        space-between;



    align-items:

        center;

}





.chat-brand-title {



    color:

        #173F2B;



    font-size:

        25px;



    font-weight:

        650;

}





.chat-brand-subtitle {



    color:

        #7B817C;



    font-size:

        13px;



    margin-top:

        4px;

}





.chat-status {



    padding:

        8px 13px;



    border-radius:

        999px;



    background:

        rgba(

            226,

            239,

            223,

            0.8

        );



    color:

        #2F6C44;



    font-size:

        12px;



    font-weight:

        600;

}





/* =========================================================

   CHAT MESSAGES

========================================================= */



.message-row {



    display: flex;



    width:

        min(

            900px,

            92vw

        );



    margin-left:

        auto;



    margin-right:

        auto;



    margin-bottom:

        15px;

}





.message-row.user {



    justify-content:

        flex-end;

}





.message-row.assistant {



    justify-content:

        flex-start;

}





.message {



    max-width:

        72%;



    padding:

        14px 18px;



    border-radius:

        22px;



    font-size:

        15px;



    line-height:

        1.6;



    box-shadow:

        0 5px 18px

        rgba(

            45,

            70,

            50,

            0.045

        );

}





.message-user {



    background:

        #234F36;



    color:

        white;



    border-bottom-right-radius:

        7px;

}





.message-assistant {



    background:

        rgba(

            255,

            255,

            255,

            0.86

        );



    border:

        1px solid

        rgba(

            219,

            227,

            216,

            0.95

        );



    color:

        #294537;



    border-bottom-left-radius:

        7px;

}





/* =========================================================

   ROUTE RESULT CARD

========================================================= */



.route-card {



    margin-top:

        15px;



    background:

        rgba(

            248,

            250,

            245,

            0.95

        );



    border:

        1px solid

        #D9E4D6;



    border-radius:

        18px;



    padding:

        17px;



    min-width:

        330px;

}





.route-path {



    color:

        #173F2B;



    font-size:

        15px;



    font-weight:

        650;



    margin-bottom:

        11px;

}





.route-badge {



    display:

        inline-block;



    background:

        #E2F0DF;



    color:

        #29633D;



    border-radius:

        999px;



    padding:

        5px 9px;



    font-size:

        11px;



    font-weight:

        600;



    margin-bottom:

        11px;

}





.route-main {



    color:

        #294A37;



    font-size:

        14px;



    font-weight:

        650;



    margin-bottom:

        7px;

}





.route-detail {



    color:

        #69776D;



    font-size:

        13px;



    margin-top:

        4px;

}





/* =========================================================

   CHAT QUICK ACTIONS

========================================================= */



.st-key-chat_actions {



    width:

        min(

            900px,

            92vw

        ) !important;



    margin-left:

        auto !important;



    margin-right:

        auto !important;



    margin-top:

        8px;



    margin-bottom:

        17px;

}





.st-key-chat_actions

[data-testid="stBaseButton-secondary"] {



    width:

        100% !important;



    border-radius:

        999px !important;



    background:

        rgba(

            255,

            255,

            255,

            0.70

        ) !important;



    border:

        1px solid

        #D4DED1 !important;



    color:

        #3B5A49 !important;



    font-size:

        12px !important;



    min-height:

        38px !important;



    box-shadow:

        none !important;

}





.st-key-chat_actions

[data-testid="stBaseButton-secondary"]:hover {



    background:

        #EDF4E9 !important;



    border-color:

        #B9CAB5 !important;

}





/* =========================================================

   CHAT COMPOSER

========================================================= */



.st-key-chat_composer {



    position:

        sticky;



    bottom:

        18px;



    z-index:

        20;



    width:

        min(

            900px,

            92vw

        ) !important;



    margin-left:

        auto !important;



    margin-right:

        auto !important;



    padding:

        10px 12px !important;



    border-radius:

        26px;



    background:

        rgba(

            255,

            255,

            255,

            0.88

        );



    border:

        1px solid

        rgba(

            255,

            255,

            255,

            0.93

        );



    box-shadow:

        0 16px 45px

        rgba(

            48,

            70,

            49,

            0.12

        );



    backdrop-filter:

        blur(16px);

}





.st-key-chat_composer

[data-testid="stForm"] {



    border:

        none !important;



    padding:

        0 !important;



    background:

        transparent !important;

}





.st-key-chat_composer

div[data-testid="stTextInput"] > div,



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





.st-key-chat_composer input {



    height:

        52px !important;



    background:

        transparent !important;



    border:

        none !important;



    color:

        #294638 !important;



    -webkit-text-fill-color:

        #294638 !important;



    font-size:

        15px !important;



    box-shadow:

        none !important;

}





.st-key-chat_composer

input::placeholder {



    color:

        #89908A !important;



    -webkit-text-fill-color:

        #89908A !important;

}





/* Chat send circle */



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



    max-width:

        52px !important;



    max-height:

        52px !important;



    border:

        none !important;



    border-radius:

        50% !important;



    background:

        #285E3D !important;



    padding:

        0 !important;



    color:

        white !important;

}





/* Hide Submit text in chat */



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



    color:

        white;



    font-size:

        23px;



    line-height:

        1;

}





/* =========================================================

   MOBILE

========================================================= */



@media (

    max-width:

    760px

) {



    .block-container {



        padding-left:

            14px !important;



        padding-right:

            14px !important;

    }





    .hero-shell {



        padding-top:

            8vh;



        margin-bottom:

            30px;

    }





    .hero-eyebrow {



        font-size:

            10px;



        letter-spacing:

            3px;



        line-height:

            1.5;



        margin-bottom:

            22px;

    }





    .hero-title {



        font-size:

            46px;



        line-height:

            1.02;

    }





    .st-key-hero_card {



        width:

            94vw !important;



        padding:

            17px !important;



        border-radius:

            26px;

    }





    .leaf-orb {



        width:

            48px;



        height:

            48px;

    }





    .leaf-orb svg {



        width:

            25px;



        height:

            25px;

    }





    .st-key-hero_card input {



        font-size:

            16px !important;

    }





    .message {



        max-width:

            86%;

    }





    .route-card {



        min-width:

            240px;

    }



}



</style>

""",

        unsafe_allow_html=True,

    )


# ============================================================
# LANDING -> LIVE RASA CHAT
# ============================================================

def handle_prompt(user_message):
    """Switch to the real chat page, carrying the first user's message."""
    message = str(user_message or "").strip()
    if not message:
        return
    st.session_state.page = "chat"
    st.session_state.landing_first_message = message
    st.rerun()


# ============================================================

# LANDING PAGE

# ============================================================



def render_landing_page():



    # ========================================================

    # HERO

    # ========================================================



    st.markdown(

        '<div class="hero-shell"><div class="hero-eyebrow">YOUR SUSTAINABLE AI TRAVEL COMPANION</div><div class="hero-title">Plan greener<br>travel experiences.</div></div>',

        unsafe_allow_html=True,

    )





    # ========================================================

    # HERO CARD

    # ========================================================



    with st.container(

        key="hero_card"

    ):





        # ====================================================

        # INPUT FORM

        # ====================================================



        with st.form(

            "landing_form",

            clear_on_submit=True,

            border=False,

        ):





            icon_col, input_col, send_col = (

                st.columns(

                    [

                        0.8,

                        9.2,

                        1

                    ],

                    vertical_alignment="center",

                    gap="small",

                )

            )





            # ================================================

            # ICON

            # ================================================



            with icon_col:



                st.markdown(

                    '<div class="leaf-orb"><svg viewBox="0 0 48 48"><path d="M10 31 C11 18 20 12 32 10 C31 22 25 30 15 34"></path><path d="M15 34 C20 26 25 20 32 14"></path><path d="M16 35 C10 29 8 24 9 19 C16 20 21 25 22 31"></path></svg></div>',

                    unsafe_allow_html=True,

                )





            # ================================================

            # INPUT

            # ================================================



            with input_col:



                landing_prompt = (

                    st.text_input(

                        "Travel request",



                        placeholder=

                            (

                                "Where would you like "

                                "to travel sustainably?"

                            ),



                        label_visibility=

                            "collapsed",

                    )

                )





            # ================================================

            # SEND

            # ================================================



            with send_col:



                submitted = (

                    st.form_submit_button(

                        "Submit"

                    )

                )





        # ====================================================

        # DIVIDER

        # ====================================================



        st.markdown(

            '<div class="prompt-divider"></div>',

            unsafe_allow_html=True,

        )





        # ====================================================

        # SUGGESTION PILLS

        # ====================================================



        col1, col2, col3, col4 = (

            st.columns(

                4,

                gap="small",

            )

        )





        with col1:



            japan = st.button(

                "🍃 Eco-friendly in Japan",

                use_container_width=True,

                key="japan_prompt",

            )





        with col2:



            norway = st.button(

                "🌲 Nature escapes in Norway",

                use_container_width=True,

                key="norway_prompt",

            )





        with col3:



            city = st.button(

                "🚲 Low-carbon city breaks",

                use_container_width=True,

                key="city_prompt",

            )





        with col4:



            beach = st.button(

                "🍃 Sustainable beach trips",

                use_container_width=True,

                key="beach_prompt",

            )





    # ========================================================

    # LANDING EVENTS

    # ========================================================



    if (

        submitted

        and

        landing_prompt

    ):



        handle_prompt(

            landing_prompt

        )





    if japan:



        handle_prompt(

            "I want to plan an eco-friendly trip to Japan."

        )





    if norway:



        handle_prompt(

            (

                "I want to explore sustainable "

                "nature destinations in Norway."

            )

        )





    if city:



        handle_prompt(

            "I want to plan a low-carbon city break."

        )





    if beach:



        handle_prompt(

            "I want to plan a sustainable beach holiday."

        )


# ============================================================
# RUN APP — only app.py needs to be launched
# ============================================================

if st.session_state.page == "landing":
    # Keep the original landing page and its existing styles.
    inject_css()
    render_landing_page()
else:
    # Import the REAL Rasa-connected chatbot, not app.py's old mock chat.
    # Keep chat_page.py in the same directory as app.py.
    import chat_page

    # A new landing message starts a fresh chatbot conversation.
    first_message = st.session_state.pop("landing_first_message", None)
    if first_message is not None:
        chat_page.fresh_trip_state()
        chat_page.process_message(first_message)
        # process_message calls st.rerun() after receiving the Rasa response.

    # Reuse the entire working interface and its existing state.
    chat_page.main()
