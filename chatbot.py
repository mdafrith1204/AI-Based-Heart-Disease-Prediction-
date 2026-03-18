import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv(""))

SYSTEM_PROMPT = """
You are HeartCare AI — a friendly medical wellness assistant.

PERSONALITY:
- Warm
- Supportive
- Friendly like therapist + doctor
- Good listener
- Encouraging tone

YOU HELP WITH:
✔ Heart health education
✔ Diet advice
✔ Exercise guidance
✔ Lifestyle improvements
✔ Stress & emotional wellness
✔ Friendly daily conversation
✔ Motivation and support

IMPORTANT RULES:
- Allow normal human conversation
- Allow emotional sharing
- Allow daily talk
- Always try to connect back to health or wellbeing gently

ONLY HARD BLOCK:
❌ Coding / programming help
❌ Technology tutorials
❌ Politics
❌ Hacking / illegal topics

STYLE:
- Friendly tone
- Emojis sometimes ❤️🙂💪
- Medium length answers
- Supportive and human-like
"""

BLOCK_TOPICS = [
    "python", "coding", "programming", "sql", "javascript",
    "hacking", "politics", "election", "government"
]


def get_chatbot_response(user_message):

    msg = user_message.lower()

    if any(word in msg for word in BLOCK_TOPICS):
        return "🙂 I focus on health, wellness, and supportive conversation. Tell me how you're feeling or ask me about health."

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return "⚠️ I'm having trouble connecting right now. Please try again."
