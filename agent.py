from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# TOOL 1: Web Search
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
    """Get a 5-day weather forecast for a city."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()

    if response.get("cod") != "200":
        return f"Could not fetch weather for {city}."

    forecasts = response["list"][:5]  # next ~5 time slots (~1 per day simplified)

    result = []
    for i, f in enumerate(forecasts):
        temp = f["main"]["temp"]
        desc = f["weather"][0]["description"]
        result.append(f"Day {i+1}: {desc}, {temp}°C")

    return "\n".join(result)


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
# TOOL 4: Top Places 
# ─────────────────────────────────────────
@tool
def get_top_places(city_vibe: str) -> str:
    """Get top attractions based on city and vibe."""
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    url = (
        f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        f"?query={city_vibe}&key={api_key}"
    )
    response = requests.get(url).json()
    places = response.get("results", [])[:5]

    if not places:
        return f"No places found for {city_vibe}."

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
        "You are an intelligent travel planning agent. "
        "Your job is to create a highly personalized and realistic travel itinerary. "

        "You MUST: "
        "1. Use tools to gather real data (weather, places, budget, etc.). "
        "2. Align ALL activities strictly with the user's travel vibe. "
        "3. Explain briefly why each activity fits the vibe. "
        "4. Avoid generic tourist plans unless they match the vibe. "
        "5. Group nearby places to minimize travel time. "
        "6. Use realistic cost estimates. "

        "Output format: "
        "- Day-by-day itinerary "
        "- Each activity includes a short reason "
        "- Weather per day (do not repeat identical values unless necessary) "
        "- Budget breakdown "
        "- Top places "
    )
)


# ─────────────────────────────────────────
# MAIN FUNCTION 
# ─────────────────────────────────────────
def plan_trip(destination: str, num_days: int, budget_level: str, vibe: str) -> str:
    user_input = (
        f"Plan a {num_days}-day trip to {destination}. "
        f"Budget level: {budget_level}. "
        f"Travel vibe: {vibe}. "
        f"Only include activities that match this vibe. Avoid unrelated tourist attractions. "
        f"When searching for places, use queries like '{vibe} places in {destination}'."
    )

    result = agent_executor.invoke({
        "messages": [{"role": "user", "content": user_input}]
    })

    return result["messages"][-1].content