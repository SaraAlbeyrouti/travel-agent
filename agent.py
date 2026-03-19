from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# TOOL 1: Web Search (via Tavily)
# ─────────────────────────────────────────
from tavily import TavilyClient

@tool
def search_travel_info(query: str) -> str:
    """Search the web for flights, hotels, and travel info."""
    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    results = client.search(query, max_results=3)
    return "\n".join([r["content"] for r in results["results"]])


# ─────────────────────────────────────────
# TOOL 2: Weather
# ─────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """Get the weather forecast for a city."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") != 200:
        return f"Could not fetch weather for {city}."

    temp = response["main"]["temp"]
    description = response["weather"][0]["description"]
    return f"Weather in {city}: {description}, {temp}°C"


# ─────────────────────────────────────────
# TOOL 3: Budget Estimator
# ─────────────────────────────────────────
@tool
def estimate_budget(destination: str, num_days: int, budget_level: str) -> str:
    """Estimate trip costs based on destination, duration, and budget level."""
    budgets = {
        "budget": {"hotel": 50,  "food": 20, "activities": 15, "transport": 10},
        "mid":    {"hotel": 120, "food": 50, "activities": 40, "transport": 25},
        "luxury": {"hotel": 300, "food": 120,"activities": 100,"transport": 60},
    }
    level = budget_level.lower()
    if level not in budgets:
        level = "mid"

    daily = budgets[level]
    trip_total = sum(daily.values()) * num_days

    return (
        f"Estimated costs for {num_days} days in {destination} ({level} level):\n"
        f"  Hotel/night: €{daily['hotel']}\n"
        f"  Food/day:    €{daily['food']}\n"
        f"  Activities:  €{daily['activities']}\n"
        f"  Transport:   €{daily['transport']}\n"
        f"  Total:       ~€{trip_total}"
    )


# ─────────────────────────────────────────
# TOOL 4: Top Places (via Google Places API)
# ─────────────────────────────────────────
@tool
def get_top_places(city: str) -> str:
    """Get top tourist attractions in a city."""
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    url = (
        f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query=top+attractions+in+{city}&key={api_key}"
    )
    response = requests.get(url).json()
    places = response.get("results", [])[:5]

    if not places:
        return f"No places found for {city}."

    return "\n".join([f"- {p['name']} (rating: {p.get('rating', 'N/A')})" for p in places])


# ─────────────────────────────────────────
# AGENT SETUP
# ─────────────────────────────────────────
tools = [search_travel_info, get_weather, estimate_budget, get_top_places]

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)

agent_executor = create_react_agent(
    model=llm,
    tools=tools,
    prompt=(
        "You are a helpful travel planning assistant. "
        "Use the available tools to gather information and create a detailed "
        "day-by-day itinerary with cost estimates. Always include: "
        "a day-by-day plan, weather expectations, budget breakdown, and top places to visit."
    )
)


# ─────────────────────────────────────────
# MAIN FUNCTION (called from app.py)
# ─────────────────────────────────────────
def plan_trip(destination: str, num_days: int, budget_level: str, vibe: str) -> str:
    user_input = (
        f"Plan a {num_days}-day trip to {destination}. "
        f"Budget level: {budget_level}. "
        f"Travel vibe: {vibe}."
    )
    result = agent_executor.invoke({
        "messages": [{"role": "user", "content": user_input}]
    })
    return result["messages"][-1].content