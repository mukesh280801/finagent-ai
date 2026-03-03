def classify(merchant: str | None, text: str | None) -> str:
    t = ((merchant or "") + " " + (text or "")).lower()

    rules = {
        "groceries": ["reliance", "dmart", "supermarket", "smart", "more"],
        "food": ["swiggy", "zomato", "hotel", "restaurant", "cafe"],
        "travel": ["uber", "ola", "rapido", "irctc", "metro"],
        "utilities": ["electricity", "tneb", "airtel", "jio", "vi", "broadband"],
        "health": ["hospital", "pharmacy", "apollo", "clinic", "medical"],
        "entertainment": ["bookmyshow", "pvr", "inox", "netflix", "spotify"],
    }

    for cat, keys in rules.items():
        if any(k in t for k in keys):
            return cat
    return "misc"
