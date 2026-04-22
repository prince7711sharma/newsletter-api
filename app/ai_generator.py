import json
import os
import logging
from groq import Groq

from app.config import settings

logger = logging.getLogger(__name__)

_groq_client = Groq(api_key=settings.GROQ_API_KEY)

# ─── Reusable system prompt ───────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert content writer for R.S Education Solution — an educational counselling platform with the tagline: "Redefining academic excellence through personalized counseling and cutting-edge educational resources."

Your job is to write short, friendly, personalized weekly newsletter content for students.

STRICT RULES:
- Total output: 100–150 words maximum
- Friendly, simple, student-focused tone
- Use emojis moderately (🎓 💰 📈)
- Return ONLY the newsletter body content
- **STRICT DATA SOURCING**: You MUST choose exactly 3 colleges from the "AVAILABLE COLLEGES" list provided in your system context. 
- **DO NOT** make up colleges or use colleges from your internal memory that are not in the list.
- **LOCATION MATCHING**: Match the colleges to the student's city/state provided in the prompt.
- Structure exactly:
  1. Brief intro (1 line)
  2. 🎓 TOP COLLEGES: (Name + Type + 1-line reason)
  3. 💰 SCHOLARSHIP (Use the provided "RELEVANT SCHOLARSHIPS" info)
  4. 📈 CAREER TIP (1 short actionable tip)
- Do NOT include greeting or footer.
"""


def build_user_prompt(user: dict) -> str:
    """Build a clean, token-efficient prompt for the given user."""
    interests = ", ".join(user.get("interests", [])) or "General"
    marks = user.get("marks", "N/A")
    budget = user.get("budget", "N/A")
    location = user.get("location", "India")

    return f"""Generate a weekly newsletter for this student:
- Interests: {interests}
- Academic score: {marks}/100
- Budget: ₹{budget}/year
- Location: {location}

Follow the exact structure from your instructions. Keep it under 150 words."""


def generate_newsletter_content(user: dict) -> str:
    # Try to load local context from colleges.json
    local_data = _load_relevant_data(user.get("location", "India"))
    
    college_context = ""
    if local_data.get("colleges"):
        college_context += f"\nAVAILABLE COLLEGES (PICK 3 FROM THESE):\n{json.dumps(local_data['colleges'], indent=2)}"
    
    if local_data.get("scholarships"):
        college_context += f"\nRELEVANT SCHOLARSHIPS:\n{json.dumps(local_data['scholarships'], indent=2)}"

    try:
        response = _groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + college_context},
                {"role": "user", "content": build_user_prompt(user)},
            ],
            temperature=0.7,
            max_tokens=300,   # Small/medium newsletter — keep tokens low
            top_p=0.9,
        )
        content = response.choices[0].message.content.strip()
        logger.info(f"✅ AI content generated for: {user.get('email')}")
        return content
    except Exception as e:
        logger.error(f"❌ Groq AI error for {user.get('email')}: {e}")
        return _fallback_content(user)

def _load_relevant_data(location: str) -> dict:
    """Helper to load and filter colleges and scholarships from the new JSON structure."""
    json_path = os.path.join(os.getcwd(), "colleges.json")
    if not os.path.exists(json_path):
        return {"colleges": [], "scholarships": []}
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        all_colleges = data.get("colleges", [])
        
        # Filter by city or state (case-insensitive)
        filtered_colleges = [
            c for c in all_colleges 
            if c.get("city", "").lower() == location.lower() or 
               c.get("state", "").lower() == location.lower()
        ]
        
        # If no local match, return a few top-rated ones
        final_colleges = filtered_colleges if filtered_colleges else all_colleges[:10]

        # Get relevant scholarship info if location is a state
        scholarships = data.get("scholarship_info", {}).get("state_schemes", {}).get(location, "Check national portal")
        
        return {
            "colleges": final_colleges[:15], # Limit to 15 to keep prompt size manageable
            "scholarships": scholarships
        }
    except Exception as e:
        logger.error(f"⚠️ Error reading colleges.json: {e}")
        return {"colleges": [], "scholarships": []}


def _fallback_content(user: dict) -> str:
    """Fallback content when AI generation fails. Dynamically uses user location."""
    interests = ", ".join(user.get("interests", [])) or "your field"
    location = user.get("location", "your region")
    
    return f"""Here's your weekly update from R.S Education Solution! 🌟

🎓 TOP COLLEGES:
• Searching for the best colleges in {location}...
• We recommend checking the top-ranked Government and Private institutions near you. 
• Focus on colleges that offer strong placement support for {interests}.

💰 SCHOLARSHIP:
• National Merit Scholarship – Up to ₹1,20,000/year

📈 CAREER TIP:
Build your LinkedIn profile today — recruiters in {location} are actively looking for talented students like you!"""
