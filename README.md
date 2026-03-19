#  Travel Planner Agent

An AI-powered travel planning agent built with LangChain, LangGraph, and OpenAI. Tell it where you want to go, your budget, and your vibe  and it builds you a complete day-by-day itinerary using real-time data.

## How It Works

The agent uses a ReAct reasoning loop to decide which tools to call and in what order, then synthesizes everything into a detailed travel plan.

It has access to 4 tools:

-  **Web Search** (Tavily) — finds flights, hotels, and travel tips
-  **Weather** (OpenWeatherMap) — gets the forecast for your destination
-  **Budget Estimator** — calculates cost breakdown per day and total trip cost
-  **Top Places** (Google Places API) — finds the best rated attractions

## Tech Stack

- [LangChain](https://python.langchain.com/) — agent framework and tool definitions
- [LangGraph](https://langchain-ai.github.io/langgraph/) — ReAct agent execution
- [OpenAI GPT-4o](https://openai.com/) — language model
- [Streamlit](https://streamlit.io/) — frontend UI
- [Tavily](https://tavily.com/) — web search API
- [OpenWeatherMap](https://openweathermap.org/) — weather API
- [Google Places API](https://developers.google.com/maps/documentation/places/web-service) — attractions data

## Getting Started

### 1. Clone the repo
git clone https://github.com/SaraAlbeyrouti/travel-agent.git
cd travel-agent

### 2. Install dependencies
pip install -r Requirements.txt

### 3. Set up your API keys
Create a `.env` file in the root directory:
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
GOOGLE_PLACES_API_KEY=your_key_here

### 4. Run the app
streamlit run app.py

## Project Structure

travel-agent/
├── agent.py          # LangChain agent + 4 tool definitions
├── app.py            # Streamlit UI
├── Requirements.txt  # Dependencies
└── .env              # API keys (never commit this!)

## Example Output

Given: "7 days in Venice, mid budget, cultural vibe"

The agent will return:
-  Real-time weather forecast
-  Full budget breakdown (~€1,645 for 7 days)
-  Top 5 rated attractions with ratings
-  Complete day-by-day itinerary
