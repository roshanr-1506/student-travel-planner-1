"""
Wayfare — Trip Planning for Students
Flask port of the original client-side (HTML/JS) itinerary engine.
All budgeting / itinerary logic now runs in Python on the server;
the front-end just renders whatever JSON the server returns.
"""

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ----------------------------------------------------------------
# Destination data (ported 1:1 from the original DESTINATIONS object)
# ----------------------------------------------------------------
DESTINATIONS = {
    "goa": {
        "label": "Goa", "region": "Beach & coast",
        "dailyBudgetLow": 1200, "dailyBudgetHigh": 3500,
        "stayOptions": [
            {"name": "Hostel dorm bed in Anjuna/Baga", "cost": 450, "tag": "budget stay"},
            {"name": "Shared guesthouse room", "cost": 900, "tag": "mid stay"},
            {"name": "Beach-facing cottage", "cost": 1800, "tag": "upgrade stay"},
        ],
        "food": [
            {"name": "Beach shack thali", "cost": 150, "tag": "food"},
            {"name": "Goan fish curry & rice", "cost": 220, "tag": "food"},
            {"name": "Street-side sandwich & juice", "cost": 90, "tag": "food"},
        ],
        "transport": [
            {"name": "Rent a scooter for the day", "cost": 350, "tag": "transport"},
            {"name": "Shared pilot taxi hop", "cost": 80, "tag": "transport"},
        ],
        "activities": {
            "nature": [{"name": "Sunset at Vagator cliffs", "desc": "Walk up to the laterite cliffs above Vagator beach for golden-hour views.", "cost": 0}],
            "food": [{"name": "Mapusa market food crawl", "desc": "Wander the local market for fresh produce, snacks, and feni tastings.", "cost": 200}],
            "culture": [{"name": "Old Goa churches walk", "desc": "Basilica of Bom Jesus and Se Cathedral, both UNESCO sites.", "cost": 50}],
            "nightlife": [{"name": "Tito's Lane / Anjuna night market", "desc": "Live music, stalls, and the famous Wednesday flea market (if timing allows).", "cost": 300}],
            "adventure": [{"name": "Parasailing at Baga", "desc": "15-minute tandem parasail over the bay.", "cost": 1200}],
            "shopping": [{"name": "Anjuna flea market browsing", "desc": "Textiles, jewellery, and souvenirs — bargain hard.", "cost": 300}],
            "chill": [{"name": "Cafe hop in Assagao", "desc": "Slow morning at one of Assagao's leafy cafes.", "cost": 250}],
            "photo": [{"name": "Chapora Fort at sunset", "desc": "The 'Dil Chahta Hai' fort with panoramic coastline views.", "cost": 0}],
        },
    },
    "manali": {
        "label": "Manali", "region": "Mountains",
        "dailyBudgetLow": 1000, "dailyBudgetHigh": 3000,
        "stayOptions": [
            {"name": "Hostel dorm in Old Manali", "cost": 400, "tag": "budget stay"},
            {"name": "Guesthouse with mountain view", "cost": 850, "tag": "mid stay"},
            {"name": "Riverside cottage", "cost": 1700, "tag": "upgrade stay"},
        ],
        "food": [
            {"name": "Himachali thali", "cost": 180, "tag": "food"},
            {"name": "Israeli cafe shakshuka", "cost": 220, "tag": "food"},
            {"name": "Momos & thukpa", "cost": 120, "tag": "food"},
        ],
        "transport": [
            {"name": "Rent a bike for the day", "cost": 700, "tag": "transport"},
            {"name": "Shared taxi to Solang/Old Manali", "cost": 150, "tag": "transport"},
        ],
        "activities": {
            "nature": [{"name": "Walk through Old Manali orchards", "desc": "Wander apple orchards along the Manalsu stream.", "cost": 0}],
            "food": [{"name": "Old Manali cafe trail", "desc": "Hop between cafes known for wood-fired pizza and local trout.", "cost": 250}],
            "culture": [{"name": "Hadimba Temple visit", "desc": "Ancient wooden temple set inside a cedar forest.", "cost": 0}],
            "nightlife": [{"name": "Bonfire night at a hostel", "desc": "Most hostels run a communal bonfire with music after dark.", "cost": 0}],
            "adventure": [{"name": "Paragliding at Solang Valley", "desc": "Tandem flight over the valley with mountain backdrops.", "cost": 2200}],
            "shopping": [{"name": "Tibetan Market browsing", "desc": "Woollens, prayer flags, and handicrafts.", "cost": 300}],
            "chill": [{"name": "Riverside reading session", "desc": "Find a quiet ledge along the Beas river.", "cost": 0}],
            "photo": [{"name": "Jogini Waterfall hike", "desc": "A moderate hike to a scenic waterfall above Vashisht.", "cost": 0}],
        },
    },
    "jaipur": {
        "label": "Jaipur", "region": "Heritage city",
        "dailyBudgetLow": 900, "dailyBudgetHigh": 2800,
        "stayOptions": [
            {"name": "Hostel dorm near Hawa Mahal", "cost": 400, "tag": "budget stay"},
            {"name": "Heritage guesthouse room", "cost": 900, "tag": "mid stay"},
            {"name": "Boutique haveli stay", "cost": 1900, "tag": "upgrade stay"},
        ],
        "food": [
            {"name": "Dal baati churma thali", "cost": 160, "tag": "food"},
            {"name": "Lassiwala kulhad lassi", "cost": 60, "tag": "food"},
            {"name": "Street kachori & chai", "cost": 80, "tag": "food"},
        ],
        "transport": [
            {"name": "Auto-rickshaw day pass", "cost": 400, "tag": "transport"},
            {"name": "Rent a scooter", "cost": 350, "tag": "transport"},
        ],
        "activities": {
            "nature": [{"name": "Nahargarh Fort sunset", "desc": "Panoramic views over the pink city from the ridge.", "cost": 200}],
            "food": [{"name": "Chandpole street food trail", "desc": "Pyaaz kachori, ghewar, and more in the old city.", "cost": 200}],
            "culture": [{"name": "Amber Fort & City Palace", "desc": "Two of Jaipur's most iconic Rajput-era monuments.", "cost": 550}],
            "nightlife": [{"name": "Rooftop dinner with fort views", "desc": "Several old-city rooftops overlook lit-up forts at night.", "cost": 400}],
            "adventure": [{"name": "Hot air balloon ride", "desc": "Sunrise balloon flight over the Aravalli foothills.", "cost": 9500}],
            "shopping": [{"name": "Johari Bazaar browsing", "desc": "Jewellery, block-print textiles, and lac bangles.", "cost": 300}],
            "chill": [{"name": "Cafe at Bapu Bazaar", "desc": "People-watch with a chai near the old city gates.", "cost": 120}],
            "photo": [{"name": "Hawa Mahal at golden hour", "desc": "Best light hits the honeycomb facade just after sunrise.", "cost": 50}],
        },
    },
    "rishikesh": {
        "label": "Rishikesh", "region": "Riverside & adventure",
        "dailyBudgetLow": 900, "dailyBudgetHigh": 2700,
        "stayOptions": [
            {"name": "Hostel dorm near Laxman Jhula", "cost": 400, "tag": "budget stay"},
            {"name": "Riverside guesthouse", "cost": 800, "tag": "mid stay"},
            {"name": "Ganga-view cottage", "cost": 1600, "tag": "upgrade stay"},
        ],
        "food": [
            {"name": "Pure-veg ashram thali", "cost": 120, "tag": "food"},
            {"name": "German Bakery breakfast", "cost": 200, "tag": "food"},
            {"name": "Street chaat by the ghats", "cost": 80, "tag": "food"},
        ],
        "transport": [
            {"name": "Rent a bike", "cost": 500, "tag": "transport"},
            {"name": "Shared auto along the ghats", "cost": 60, "tag": "transport"},
        ],
        "activities": {
            "nature": [{"name": "Walk across Ram Jhula at sunrise", "desc": "Quiet riverside views before the crowds arrive.", "cost": 0}],
            "food": [{"name": "Cafe-hop along Tapovan", "desc": "Health-food cafes overlooking the Ganga.", "cost": 250}],
            "culture": [{"name": "Triveni Ghat evening aarti", "desc": "Daily fire ritual on the riverbank, open to all.", "cost": 0}],
            "nightlife": [{"name": "Live acoustic night at a cafe", "desc": "Several riverside cafes host informal music evenings.", "cost": 150}],
            "adventure": [{"name": "Grade III white-water rafting", "desc": "16km rafting stretch from Shivpuri to Rishikesh.", "cost": 600}],
            "shopping": [{"name": "Tibetan market browsing", "desc": "Beads, singing bowls, and prayer flags.", "cost": 200}],
            "chill": [{"name": "Riverside yoga session", "desc": "Drop-in yoga classes run along the ghats most mornings.", "cost": 200}],
            "photo": [{"name": "Laxman Jhula bridge views", "desc": "Iconic suspension bridge over the Ganga.", "cost": 0}],
        },
    },
    "pondicherry": {
        "label": "Pondicherry", "region": "French quarter & coast",
        "dailyBudgetLow": 1000, "dailyBudgetHigh": 3000,
        "stayOptions": [
            {"name": "Hostel dorm in White Town", "cost": 450, "tag": "budget stay"},
            {"name": "Guesthouse in Tamil quarter", "cost": 850, "tag": "mid stay"},
            {"name": "Colonial-style heritage room", "cost": 1900, "tag": "upgrade stay"},
        ],
        "food": [
            {"name": "French-Tamil fusion meal", "cost": 250, "tag": "food"},
            {"name": "Filter coffee & bun", "cost": 60, "tag": "food"},
            {"name": "Beachside seafood plate", "cost": 280, "tag": "food"},
        ],
        "transport": [
            {"name": "Rent a bicycle", "cost": 150, "tag": "transport"},
            {"name": "Rent a scooter", "cost": 350, "tag": "transport"},
        ],
        "activities": {
            "nature": [{"name": "Promenade beach walk at sunrise", "desc": "Car-free stretch along the Bay of Bengal.", "cost": 0}],
            "food": [{"name": "White Town cafe crawl", "desc": "French bakeries and fusion cafes in the old quarter.", "cost": 300}],
            "culture": [{"name": "French Quarter architecture walk", "desc": "Mustard-yellow colonial buildings and quiet lanes.", "cost": 0}],
            "nightlife": [{"name": "Live music at a beachside bar", "desc": "A handful of bars run acoustic sets in the evenings.", "cost": 300}],
            "adventure": [{"name": "Scuba diving taster session", "desc": "Beginner dive session run from Temple Adventures.", "cost": 3500}],
            "shopping": [{"name": "Auroville handicrafts browsing", "desc": "Sustainable crafts and incense from the Auroville collective.", "cost": 300}],
            "chill": [{"name": "Auroville visit & meditation", "desc": "Visit the Matrimandir grounds for quiet reflection.", "cost": 0}],
            "photo": [{"name": "Rue Romain Rolland street photos", "desc": "Bougainvillea-covered colonial facades.", "cost": 0}],
        },
    },
    "default": {
        "label": None, "region": "General",
        "dailyBudgetLow": 1000, "dailyBudgetHigh": 3000,
        "stayOptions": [
            {"name": "Hostel dorm bed", "cost": 450, "tag": "budget stay"},
            {"name": "Budget guesthouse room", "cost": 900, "tag": "mid stay"},
            {"name": "Comfort hotel room", "cost": 1800, "tag": "upgrade stay"},
        ],
        "food": [
            {"name": "Local thali / set meal", "cost": 180, "tag": "food"},
            {"name": "Street food trail", "cost": 120, "tag": "food"},
            {"name": "Sit-down cafe meal", "cost": 250, "tag": "food"},
        ],
        "transport": [
            {"name": "Local public transport day pass", "cost": 150, "tag": "transport"},
            {"name": "Shared cab / rickshaw", "cost": 300, "tag": "transport"},
        ],
        "activities": {
            "nature": [{"name": "Explore a nearby park or viewpoint", "desc": "Free or low-cost green space to start the day slow.", "cost": 0}],
            "food": [{"name": "Local market food trail", "desc": "Sample regional snacks at the central market.", "cost": 200}],
            "culture": [{"name": "Old town / heritage walk", "desc": "Self-guided walk through the historic core.", "cost": 100}],
            "nightlife": [{"name": "Evening market or night street", "desc": "Most towns have a lively after-dark stretch worth a wander.", "cost": 200}],
            "adventure": [{"name": "Local adventure activity", "desc": "Check for a regional activity — trekking, water sports, or biking.", "cost": 1000}],
            "shopping": [{"name": "Local bazaar browsing", "desc": "Handicrafts, textiles, or souvenirs unique to the region.", "cost": 250}],
            "chill": [{"name": "Cafe & journaling break", "desc": "Slow down with a coffee somewhere central.", "cost": 150}],
            "photo": [{"name": "Golden-hour landmark visit", "desc": "Time a visit to the area's best-known sight for soft light.", "cost": 50}],
        },
    },
}

TIME_SLOTS = ["7:30 AM", "9:30 AM", "12:30 PM", "3:30 PM", "6:30 PM", "9:00 PM"]

SPLIT_PCT = {"stay": 0.34, "food": 0.27, "transport": 0.16, "activities": 0.18, "buffer": 0.05}
BAR_COLORS = {"stay": "#FF6B4A", "food": "#D9A441", "transport": "#7BA0D6", "activities": "#5F7A5C", "buffer": "#C9C2AE"}
BAR_LABELS = {"stay": "Stay", "food": "Food", "transport": "Transport", "activities": "Activities", "buffer": "Buffer"}

PACKING_BASE = [
    "Reusable water bottle",
    "Power bank & charging cable",
    "Copy of student ID / travel ID",
    "Basic first-aid + any personal meds",
]
PACKING_BY_INTEREST = {
    "nature": ["Light rain jacket", "Comfortable walking shoes"],
    "adventure": ["Quick-dry clothing", "Extra change of clothes"],
    "nightlife": ["One smart-casual outfit"],
    "culture": ["Modest clothing for temples/heritage sites"],
    "photo": ["Spare memory card / phone storage"],
    "chill": ["A good book or journal"],
    "food": ["Antacid / digestion tablets, just in case"],
    "shopping": ["A foldable extra bag for purchases"],
}


# ----------------------------------------------------------------
# Helpers (ported from the original JS helpers)
# ----------------------------------------------------------------
def find_destination(name: str):
    key = (name or "").strip().lower()
    for k, data in DESTINATIONS.items():
        if k == "default":
            continue
        if key and key in k or (key and k in key):
            return data, True
    return DESTINATIONS["default"], False


def inr(n: float) -> str:
    """Format a number as Indian-Rupee with Indian-style thousands separators."""
    n = round(n)
    s = str(abs(n))
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        s = ",".join(groups) + "," + last3
    sign = "-" if n < 0 else ""
    return f"{sign}₹{s}"


def pick(arr, seed):
    return arr[seed % len(arr)]


def seeded_shuffle(arr, seed):
    """Deterministic pseudo-random shuffle, ported from the JS LCG version."""
    a = list(arr)
    s = seed
    for i in range(len(a) - 1, 0, -1):
        s = (s * 9301 + 49297) % 233280
        j = int((s / 233280) * (i + 1))
        a[i], a[j] = a[j], a[i]
    return a


def title_case(text: str) -> str:
    return " ".join(w[:1].upper() + w[1:] if w else w for w in text.split(" "))


# ----------------------------------------------------------------
# Core itinerary builder (ported from buildItinerary())
# ----------------------------------------------------------------
def build_itinerary(payload: dict) -> dict:
    destination_input = (payload.get("destination") or "").strip() or "your destination"
    origin = (payload.get("origin") or "").strip() or "your city"
    days = max(1, min(14, int(payload.get("days") or 4)))
    travelers = max(1, min(10, int(payload.get("travelers") or 1)))
    total_budget = max(500, int(payload.get("budget") or 5000))
    pace = payload.get("pace") or "balanced"
    interests = [i for i in (payload.get("interests") or []) if i]
    active_interests = interests if interests else ["nature", "food", "culture", "chill"]

    dest, matched = find_destination(destination_input)
    city_label = dest["label"] or title_case(destination_input.strip())

    # ---- Budget split ----
    allocation = {k: total_budget * pct for k, pct in SPLIT_PCT.items()}
    per_day_per_person = total_budget / days / travelers

    nightly_stay_budget_per_person = allocation["stay"] / days / travelers
    stay_choice = dest["stayOptions"][0]
    for opt in dest["stayOptions"]:
        if opt["cost"] <= nightly_stay_budget_per_person:
            stay_choice = opt

    activities_per_day = {"relaxed": 3, "packed": 5}.get(pace, 4)

    interest_pool = active_interests if active_interests else list(dest["activities"].keys())

    day_cards = []
    for d in range(1, days + 1):
        day_interests = seeded_shuffle(interest_pool, d * 7 + 3)
        chosen_activities = []
        i = 0
        while len(chosen_activities) < activities_per_day and i < len(day_interests) * 3:
            interest_key = day_interests[i % len(day_interests)]
            options = dest["activities"].get(interest_key) or dest["activities"]["chill"]
            act = pick(options, d + i)
            if not any(a["name"] == act["name"] for a in chosen_activities):
                chosen_activities.append({**act, "interest": interest_key})
            i += 1

        meal = pick(dest["food"], d)
        transport = pick(dest["transport"], d + 1)

        slot_items = chosen_activities[: len(TIME_SLOTS)]
        day_cost = stay_choice["cost"] + meal["cost"] * 2 + transport["cost"]

        activities_out = []
        for idx, act in enumerate(slot_items):
            day_cost += act.get("cost", 0)
            activities_out.append({
                "time": TIME_SLOTS[idx % len(TIME_SLOTS)],
                "name": act["name"],
                "desc": act.get("desc", ""),
                "tag": f"{inr(act['cost']) + ' est.' if act.get('cost') else 'free'} · {act['interest']}",
            })

        activities_out.append({
            "time": "Meals",
            "name": meal["name"],
            "desc": "Budget around twice this for two meals across the day.",
            "tag": f"{inr(meal['cost'])} per meal, per person",
        })
        activities_out.append({
            "time": "Getting around",
            "name": transport["name"],
            "desc": "Split this cost with your travel group where possible.",
            "tag": f"{inr(transport['cost'])} est.",
        })

        if d == 1:
            title = "Arrival & first impressions"
        elif d == days:
            title = "Last looks & departure"
        else:
            title = f"Exploring {city_label}"

        day_cards.append({
            "day_num": d,
            "days": days,
            "title": title,
            "cost_label": f"~{inr(day_cost * travelers)} for {'you' if travelers == 1 else str(travelers) + ' of you'}",
            "activities": activities_out,
        })

    # ---- Budget bars ----
    bars = []
    for k in SPLIT_PCT:
        pct = round(SPLIT_PCT[k] * 100)
        bars.append({
            "key": k,
            "label": BAR_LABELS[k],
            "pct": pct,
            "color": BAR_COLORS[k],
            "amount": inr(allocation[k]),
        })

    # ---- Packing list ----
    packing = list(dict.fromkeys(PACKING_BASE))
    for k in active_interests:
        for p in PACKING_BY_INTEREST.get(k, []):
            if p not in packing:
                packing.append(p)

    # ---- Money-saving tips ----
    tips = [
        f"Book {stay_choice['tag'].replace(' stay', '')} stays directly through hostel sites or call ahead — "
        f"you'll often beat the listed OTA price.",
        "Travel in a group and split cabs/scooters rather than booking solo rides.",
        "Eat where locals queue, not where the menu has photos — it's usually cheaper and better.",
        "Carry a copy of your student ID; many sights and transport options offer student discounts.",
        ("Buy a multi-day local transport pass if your destination offers one." if days >= 4
         else "For a short trip, a day-rental scooter or bicycle is usually cheaper than repeated cab rides."),
    ]

    total_estimate = sum(allocation.values())

    return {
        "origin": origin,
        "city_label": city_label,
        "days": days,
        "travelers": travelers,
        "pace": pace,
        "region": dest["region"],
        "total_budget": inr(total_budget),
        "per_day_per_person": inr(per_day_per_person),
        "bars": bars,
        "day_cards": day_cards,
        "stay_choice": {
            "name": stay_choice["name"],
            "cost": inr(stay_choice["cost"]),
            "nightly_budget": inr(nightly_stay_budget_per_person),
        },
        "packing": packing,
        "tips": tips,
        "total_estimate": inr(total_estimate),
    }


# ----------------------------------------------------------------
# Routes
# ----------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    payload = request.get_json(force=True, silent=True) or {}
    if not payload.get("budget"):
        return jsonify({"error": "Add a total budget so we can build cost-aware suggestions."}), 400
    try:
        result = build_itinerary(payload)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Something went wrong building your itinerary: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
