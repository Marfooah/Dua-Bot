import os
import json
import traceback
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Dua Bot", page_icon="🕋", layout="centered")

# ---------------- UI STYLING ----------------
st.markdown(
    """
    <style>
    .main-container {max-width: 760px; margin: 0 auto;}
    .card {background: #fff; border-radius: 12px; box-shadow: 0 6px 18px rgba(16,24,40,0.08); padding: 18px; margin-top: 12px;}
    .arabic {font-size: 28px; font-weight: 600; direction: rtl; text-align: right; margin-bottom: 8px;}
    .translation {font-size: 16px; color: #ffffff !important; margin-bottom: 6px;}
    .source {font-size: 13px; color: #e5e7eb !important; margin-top: 8px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🕋 Dua Bot")
st.markdown("AI-powered duas based on your emotional state.")

# ---------------- API KEY ----------------
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("Missing GROQ_API_KEY environment variable.")
    st.stop()

client = Groq(api_key=api_key)

# ---------------- INPUT ----------------
mood_select = st.selectbox(
    "Choose a situation",
    ["Select...", "Stress", "Sadness", "Gratitude", "Exam Anxiety", "Illness",
     "Fear", "Anger", "Confusion", "Tawbah", "Guidance", "Loneliness"]
)

mood_text = st.text_input("Or describe your situation")

submit = st.button("Get Dua 💫")

# ---------------- PROMPT (FIXED) ----------------
SYSTEM_PROMPT = """
You are NOT allowed to generate Arabic text.

You are an Islamic knowledge assistant.

Return ONLY valid JSON with keys:
arabic, translation, explanation, source

RULES:
- Arabic MUST be a real authentic Quranic verse or authentic dua text
- If unsure, return empty string for arabic
- Do NOT invent Arabic words
- Do NOT translate into Arabic
- Output ONLY JSON, no extra text
"""

# ---------------- HELPERS ----------------

def is_valid_arabic(text: str) -> bool:
    return bool(text) and any('\u0600' <= c <= '\u06FF' for c in text)


def safe_json_parse(raw: str):
    try:
        return json.loads(raw)
    except:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == -1:
            return None
        try:
            return json.loads(raw[start:end])
        except:
            return None


def call_groq(user_message: str, retries=1):
    for _ in range(retries + 1):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
            )

            raw = completion.choices[0].message.content
            data = safe_json_parse(raw)

            if not data:
                continue

            # FIX: validate Arabic
            if not is_valid_arabic(data.get("arabic", "")):
                data["arabic"] = "⚠️ Authentic Arabic unavailable. Please retry."

            return data

        except Exception:
            continue

    return None


# ---------------- MAIN LOGIC ----------------
if submit:

    user_mood = mood_text.strip() if mood_text.strip() else mood_select

    if not user_mood or user_mood == "Select...":
        st.error("Please enter a valid mood or situation.")
        st.stop()

    user_message = f"""
Give an authentic dua or Quranic ayah for someone feeling: {user_mood}.
Return JSON only.
"""

    with st.spinner("Finding comfort for your heart..."):
        result = call_groq(user_message, retries=2)

    if not result:
        st.error("Failed to generate a valid response. Please try again.")
        st.stop()

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(f"<div class='arabic'>{result.get('arabic','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='translation'><b>Translation:</b> {result.get('translation','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='translation'><b>Explanation:</b> {result.get('explanation','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='source'><b>Source:</b> {result.get('source','')}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
