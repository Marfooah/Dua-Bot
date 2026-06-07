import os
import json
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Dua Bot", page_icon="🕋", layout="centered")

# ---------------- UI ----------------
st.markdown("""
<style>
.main-container {max-width: 760px; margin: auto;}
.card {background: white; padding: 18px; border-radius: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.08);}
.arabic {font-size: 28px; direction: rtl; text-align: right; font-weight: 600;}
.translation {color: #111; font-size: 16px;}
.source {color: gray; font-size: 13px;}
</style>
""", unsafe_allow_html=True)

st.title("🕋 Dua Bot")
st.markdown("AI-powered guidance for your heart.")

# ---------------- API ----------------
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("Missing GROQ_API_KEY")
    st.stop()

client = Groq(api_key=api_key)

# ---------------- SAFE DUA DATABASE (NO AI ARABIC) ----------------
DUA_DB = {
    "stress": {
        "arabic": "اللَّهُمَّ لا سَهْلَ إِلَّا مَا جَعَلْتَهُ سَهْلًا",
        "source": "Hadith"
    },
    "anxiety": {
        "arabic": "أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ",
        "source": "Quran 13:28"
    },
    "sadness": {
        "arabic": "إِنَّمَا أَشْكُو بَثِّي وَحُزْنِي إِلَى اللَّهِ",
        "source": "Quran 12:86"
    },
    "fear": {
        "arabic": "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ",
        "source": "Quran 3:173"
    },
    "gratitude": {
        "arabic": "لَئِن شَكَرْتُمْ لَأَزِيدَنَّكُمْ",
        "source": "Quran 14:7"
    },
    "guidance": {
        "arabic": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
        "source": "Quran 1:6"
    },
    "tawbah": {
        "arabic": "رَبِّ اغْفِرْ لِي وَتُبْ عَلَيَّ",
        "source": "Hadith"
    },
    "loneliness": {
        "arabic": "اللَّهُمَّ أَنِسْ وَحْشَتِي",
        "source": "General Dua"
    }
}
# ---------------- INPUT ----------------
mood_select = st.selectbox(
    "Choose your situation",
    ["Select...", "Stress", "Sadness", "Gratitude", "Exam Anxiety", "Illness",
     "Fear", "Anger", "Confusion", "Tawbah", "Guidance", "Loneliness"]
)

mood_text = st.text_input("Or describe your situation")
submit = st.button("Get Dua 💫")

# ---------------- LLM PROMPT (NO ARABIC GENERATION) ----------------
SYSTEM_PROMPT = """
You are an Islamic guidance classifier.

Classify the user's situation into ONLY one category:

stress, anxiety, sadness, fear, gratitude, guidance, tawbah, loneliness

Return ONLY JSON:
{
  "category": "...",
  "translation": "...",
  "explanation": "..."
}

DO NOT generate Arabic.
DO NOT add extra text.
"""

# ---------------- HELPERS ----------------
def safe_json(raw):
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


def call_llm(msg):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": msg},
        ],
        temperature=0.3,
    )
    return safe_json(res.choices[0].message.content)


# ---------------- MAIN ----------------
if submit:

    user_mood = mood_text.strip() if mood_text.strip() else mood_select

    if not user_mood or user_mood == "Select...":
        st.error("Please enter a valid mood.")
        st.stop()

    result = call_llm(f"Classify this situation: {user_mood}")

    if not result:
        st.error("Failed response. Try again.")
        st.stop()

    category = result.get("category", "").lower()
    dua = DUA_DB.get(category, {
        "arabic": "اللَّهُمَّ اهْدِنِي وَارْزُقْنِي الطمأنينة",
        "source": "General Dua"
    })

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(f"<div class='arabic'>{dua['arabic']}</div>", unsafe_allow_html=True)
    st.markdown(f"<b>Translation:</b> {result.get('translation','')}", unsafe_allow_html=True)
    st.markdown(f"<b>Explanation:</b> {result.get('explanation','')}", unsafe_allow_html=True)
    st.markdown(f"<div class='source'><b>Source:</b> {dua['source']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
