import os
from typing import List, Dict, Optional
from django.conf import settings

def get_gemini_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        key = getattr(settings, 'GEMINI_API_KEY', '')
    return key

def get_personalized_ideas(profession: str, interests: Optional[List[str]] = None) -> List[Dict]:
    api_key = get_gemini_key()
    if not api_key:
        return _fallback_ideas(profession)
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = _build_prompt(profession, interests)
        response = model.generate_content(prompt)
        return _parse_response(response.text)
    except Exception:
        return _fallback_ideas(profession)

def _build_prompt(profession: str, interests: Optional[List[str]]) -> str:
    base = f"Suggest 3 business ideas for a {profession} starting out."
    if interests:
        base += f" Their interests: {', '.join(interests)}."
    base += " Return as JSON array with fields: title, description, market_demand (0-100), ease (Easy/Medium/Hard), profit_range (string like '$10k - $50k'), startup_cost (string like '$1k - $5k'), time_to_revenue (string like '2 months'), time_to_profit (string like '4 months'), growth_potential (0-100), risk (Low/Medium/High)."
    return base

def _parse_response(text: str) -> List[Dict]:
    import json
    import re
    try:
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, AttributeError):
        pass
    return _fallback_ideas("")

def _fallback_ideas(profession: str) -> List[Dict]:
    return [
        {
            "title": f"Micro-SaaS for {profession.title()}s",
            "description": f"Build a simple SaaS tool solving a specific pain point for {profession}s.",
            "market_demand": 88,
            "ease": "Medium",
            "profit_range": "$50k - $200k",
            "startup_cost": "$3k - $10k",
            "time_to_revenue": "3 months",
            "time_to_profit": "6 months",
            "growth_potential": 85,
            "risk": "Medium",
        },
        {
            "title": f"Local {profession.title()} Marketplace",
            "description": f"Connect local {profession}s with clients through a curated platform.",
            "market_demand": 76,
            "ease": "Easy",
            "profit_range": "$20k - $100k",
            "startup_cost": "$2k - $8k",
            "time_to_revenue": "2 months",
            "time_to_profit": "4 months",
            "growth_potential": 72,
            "risk": "Low",
        },
        {
            "title": f"{profession.title()} Education & Courses",
            "description": f"Create and sell online courses teaching {profession} skills to beginners.",
            "market_demand": 82,
            "ease": "Easy",
            "profit_range": "$10k - $150k",
            "startup_cost": "$500 - $3k",
            "time_to_revenue": "1 month",
            "time_to_profit": "3 months",
            "growth_potential": 78,
            "risk": "Low",
        },
    ]
