"""
ai_generator.py - AI-powered newsletter content generation using Groq API
"""

import logging
from groq import Groq

from config import settings

logger = logging.getLogger(__name__)

_groq_client = Groq(api_key=settings.GROQ_API_KEY)

# ─── Reusable system prompt ───────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert content writer for R.S Education — an educational counselling platform with the tagline: "Redefining academic excellence through personalized counseling and cutting-edge educational resources."

Your job is to write short, friendly, personalized weekly newsletter content for students.

STRICT RULES:
- Total output: 100–150 words maximum
- Friendly, simple, student-focused tone
- Use emojis moderately (🎓 💰 📈)
- Return ONLY the newsletter body content (no HTML, no subject line)
- Structure exactly:
  1. Brief intro (1 line)
  2. 🎓 TOP COLLEGES (2 colleges, name + 1-line reason)
  3. 💰 SCHOLARSHIP (1 scholarship, name + amount)
  4. 📈 CAREER TIP (1 short actionable tip)
- Do NOT include greeting (Hi name) — that is added separately
- Do NOT include CTA or footer — those are added separately
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
    """
    Call Groq API to generate personalized newsletter content.
    Returns plain-text newsletter body (100–150 words).
    """
    try:
        response = _groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
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


def _fallback_content(user: dict) -> str:
    """Fallback content when AI generation fails."""
    interests = ", ".join(user.get("interests", [])) or "your field"
    location = user.get("location", "India")
    return f"""Here's your weekly update from R.S Education! 🌟

🎓 TOP COLLEGES:
• IIT Delhi – Top-ranked for {interests}, excellent placements
• BITS Pilani – Great for tech & science, strong alumni network

💰 SCHOLARSHIP:
• National Merit Scholarship – Up to ₹1,20,000/year

📈 CAREER TIP:
Build your LinkedIn profile today — recruiters in {location} actively search for students like you!"""
