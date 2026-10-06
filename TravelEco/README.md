# 🌿 TravelEco – Sustainable AI Travel Companion

TravelEco is a conversational AI chatbot designed to help users plan environmentally responsible trips. Built using **Rasa, Python, Streamlit and CSS**, it provides personalised travel recommendations while helping users understand the environmental impact of their choices.

## Project Features

- **Multi-Turn Trip Planning:** Collects departure location, destination, travel dates, budget and sustainability preferences.
- **Sustainable Transport:** Compares rail, bus, car and flight options.
- **Carbon Emission Estimates:** Uses Climatiq API to estimate emissions for selected transport.
- **Accommodation Recommendations:** Retrieves hotel options using SerpApi.
- **Cultural Events:** Helps users discover events and local experiences at their destination.
- **Human Assistance:** Prepares travel details and conversation context for a simulated advisor handover.
- **Interactive Interface:** Includes transport selection, accommodation cards, quick actions and a final trip summary.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10 | Backend development |
| Rasa Open Source 3.6.21 | Natural language understanding and dialogue management |
| Rasa SDK | Custom actions and API integration |
| Streamlit | Chatbot frontend |
| HTML and CSS | User interface styling |
| Climatiq API | Carbon emission estimates |
| SerpApi | Hotel, flight and cultural-event information |

## Installation and Setup

### 1. Download the Repository

Clone the repository or download its ZIP file from GitHub.

Open the `TravelEco` project folder in VS Code.

### 2. Set Up Python

Install Python 3.10.

Create and activate a virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Install the required Rasa dependencies:

```cmd
pip install rasa==3.6.21 rasa-sdk==3.6.2 python-dotenv requests
```

Install any additional project dependencies listed in `requirements.txt`, if provided.

### 3. Configure API Keys

The project includes an `.env.example` file.

Create a file named `.env` in the same directory and add:

```env
CLIMATIQ_API_KEY=your_climatiq_api_key
SERPAPI_API_KEY=your_serpapi_api_key
```

API keys can be obtained from:

- https://www.climatiq.io/
- https://serpapi.com/


### 4. Start the Rasa Action Server

Open a terminal in the `TravelEco` folder and activate `.venv`.

Run:

```cmd
rasa run actions --port 5055
```

Keep this terminal running.

### 5. Start the Rasa Server

Open a second terminal, activate `.venv` and run:

```cmd
rasa run --enable-api --cors "*" --port 5005
```

Keep this terminal running.

The repository includes a trained Rasa model. If you make changes to the chatbot's training data, domain or dialogue rules, retrain using:

```cmd
rasa train
```

### 6. Launch TravelEco

Open a third terminal.

Create a frontend environment if needed:

```cmd
python -m venv .venv-ui
.venv-ui\Scripts\activate
```

Install Streamlit and Requests:

```cmd
pip install streamlit requests
```

Start the application:

```cmd
streamlit run app.py
```

TravelEco should open automatically in your browser, usually at:

http://localhost:8501

## How to Use TravelEco

1. Open TravelEco and enter a greeting such as **Hi** on the landing page.
2. The application automatically opens the chatbot interface.
3. Enter **I want to plan a trip**.
4. Provide your departure location, destination, travel dates, budget and sustainability preferences.
5. Compare the transport options and choose your preferred mode.
6. Review the estimated carbon emissions and accommodation recommendations.
7. Select a hotel and optionally explore cultural events.
8. View your final trip summary.

Users can also access transport recommendations, carbon estimates, flights and human assistance through the quick-action buttons.

## Project Structure

```text
TravelEco/
├── app.py                 # Landing page
├── chat_page.py           # Chat interface
├── actions/
│   └── actions.py         # Custom Rasa actions
├── data/
│   ├── nlu.yml            # NLU training examples
│   ├── rules.yml          # Dialogue rules
│   └── stories.yml        # Conversation stories
├── models/                # Trained Rasa model
├── config.yml             # Rasa configuration
├── domain.yml             # Intents, slots and responses
├── endpoints.yml          # Action server configuration
├── credentials.yml        # Rasa channel configuration
├── .env.example           # API configuration template
└── README.md              # Project documentation
```

## Limitations

TravelEco is an academic prototype intended to demonstrate sustainable travel assistance.

- Carbon emissions are estimates and may differ from actual journey emissions.
- Hotel listings do not automatically confirm independent sustainability certification.
- Live information depends on external API availability and valid API keys.
- Human assistance prepares a handover context but does not connect to a live travel advisor.
- The application has been developed and tested locally and is not a production deployment.

## Academic Project

**Project:** Eco-Travel Advisor – Conversational Agent for Sustainable Tourism Planning

**Module:** Advanced Conversational UI Design and Chatbot Development

**Programme:** MSc Artificial Intelligence

**Institution:** Berlin School of Business and Innovation (BSBI)

**Developed by:** Nisarga Girish Kumar

---

*TravelEco – Making sustainable travel planning simpler, one conversation at a time.*