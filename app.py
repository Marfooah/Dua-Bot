import html
import json
import os
import re
from typing import Dict, Optional

import streamlit as st
from groq import Groq


st.set_page_config(page_title="Dua Bot", page_icon="🕋", layout="centered")

st.markdown(
    """
    <style>
    .main-container {
        max-width: 760px;
        margin: 0 auto;
    }
    .card {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        background: rgba(255, 255, 255, 0.04);
    }
    .arabic {
        font-size: 30px;
        font-weight: 700;
        line-height: 2.1;
        direction: rtl;
        text-align: right;
        margin-bottom: 14px;
        font-family: "Amiri", "Scheherazade New", "Noto Naskh Arabic", serif;
    }
    .translation {
        font-size: 16px;
        line-height: 1.65;
        margin-bottom: 10px;
    }
    .source {
        font-size: 13px;
        opacity: 0.78;
        margin-top: 10px;
    }
    .badge {
        display: inline-block;
        font-size: 12px;
        border: 1px solid rgba(148, 163, 184, 0.35);
        border-radius: 999px;
        padding: 3px 9px;
        margin-bottom: 10px;
        opacity: 0.82;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Important fix:
# The model is NOT allowed to generate Arabic. It may only choose one ID from
# this verified local library. This prevents corrupted or hallucinated Arabic.
DUA_LIBRARY: Dict[str, Dict[str, str]] = {
    "anxiety_grief": {
        "title": "For anxiety, worry, sadness, and pressure",
        "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ، وَالْعَجْزِ وَالْكَسَلِ، وَالْجُبْنِ وَالْبُخْلِ، وَضَلَعِ الدَّيْنِ، وَغَلَبَةِ الرِّجَالِ",
        "translation": "O Allah, I seek refuge in You from worry and grief, from incapacity and laziness, from cowardice and miserliness, from heavy debt and from being overpowered by people.",
        "explanation": "This prophetic dua directly names emotional heaviness, weakness, debt, and feeling overwhelmed.",
        "source": "Sahih al-Bukhari 6369",
        "tags": "stress anxiety sadness grief worry pressure debt overwhelmed fear",
    },
    "hardship_ease": {
        "title": "For hardship and hope",
        "arabic": "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا ۝ إِنَّ مَعَ الْعُسْرِ يُسْرًا",
        "translation": "For indeed, with hardship comes ease. Indeed, with hardship comes ease.",
        "explanation": "These ayat remind the heart that difficulty is not permanent and that Allah places ease with hardship.",
        "source": "Quran 94:5-6",
        "tags": "hardship stress exams difficulty sadness hope patience",
    },
    "capacity_relief": {
        "title": "For being overwhelmed",
        "arabic": "رَبَّنَا وَلَا تُحَمِّلْنَا مَا لَا طَاقَةَ لَنَا بِهِ ۖ وَاعْفُ عَنَّا وَاغْفِرْ لَنَا وَارْحَمْنَا",
        "translation": "Our Lord, do not burden us with what we cannot bear. Pardon us, forgive us, and have mercy upon us.",
        "explanation": "A Quranic dua for moments when life feels heavier than your strength.",
        "source": "Quran 2:286",
        "tags": "overwhelmed stress burden exams study anxiety fear",
    },
    "study_exams": {
        "title": "For study, exams, and speaking clearly",
        "arabic": "رَبِّ اشْرَحْ لِي صَدْرِي ۝ وَيَسِّرْ لِي أَمْرِي ۝ وَاحْلُلْ عُقْدَةً مِّن لِّسَانِي ۝ يَفْقَهُوا قَوْلِي",
        "translation": "My Lord, expand my chest, ease my task for me, and untie the knot from my tongue so that they may understand my speech.",
        "explanation": "The dua of Musa عليه السلام, fitting for study, interviews, exams, presentations, and clarity.",
        "source": "Quran 20:25-28",
        "tags": "study exams exam interview presentation speech confusion clarity",
    },
    "guidance": {
        "title": "For guidance and uprightness",
        "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْهُدَى وَالتُّقَى وَالْعَفَافَ وَالْغِنَى",
        "translation": "O Allah, I ask You for guidance, piety, chastity, and self-sufficiency.",
        "explanation": "A concise prophetic dua asking Allah for inner direction and a dignified, content heart.",
        "source": "Sahih Muslim; also Riyad as-Salihin 1468",
        "tags": "guidance confusion decision direction tawbah repentance self control",
    },
    "repentance": {
        "title": "For tawbah and forgiveness",
        "arabic": "رَبَّنَا ظَلَمْنَا أَنفُسَنَا وَإِن لَّمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ",
        "translation": "Our Lord, we have wronged ourselves, and if You do not forgive us and have mercy upon us, we will surely be among the losers.",
        "explanation": "A Quranic dua of repentance that combines honesty, humility, hope, and need for Allah's mercy.",
        "source": "Quran 7:23",
        "tags": "tawbah repentance guilt sin forgiveness regret",
    },
    "illness": {
        "title": "For illness and pain",
        "arabic": "أَنِّي مَسَّنِيَ الضُّرُّ وَأَنتَ أَرْحَمُ الرَّاحِمِينَ",
        "translation": "Indeed, adversity has touched me, and You are the Most Merciful of the merciful.",
        "explanation": "The dua of Ayyub عليه السلام, beautiful for sickness, pain, and long hardship.",
        "source": "Quran 21:83",
        "tags": "illness sick pain disease health hardship patience",
    },
    "fear_reliance": {
        "title": "For fear and reliance on Allah",
        "arabic": "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ",
        "translation": "Allah is sufficient for us, and He is the best disposer of affairs.",
        "explanation": "A statement of trust when fear, uncertainty, or pressure from others feels intense.",
        "source": "Quran 3:173",
        "tags": "fear anxiety safety reliance worry protection uncertainty",
    },
    "loneliness_distress": {
        "title": "For loneliness and distress",
        "arabic": "لَّا إِلَٰهَ إِلَّا أَنتَ سُبْحَانَكَ إِنِّي كُنتُ مِنَ الظَّالِمِينَ",
        "translation": "There is no deity except You; glory be to You. Indeed, I have been among the wrongdoers.",
        "explanation": "The dua of Yunus عليه السلام, often recited in distress and isolation.",
        "source": "Quran 21:87",
        "tags": "loneliness lonely distress sadness grief trapped panic",
    },
    "gratitude": {
        "title": "For gratitude",
        "arabic": "رَبِّ أَوْزِعْنِي أَنْ أَشْكُرَ نِعْمَتَكَ الَّتِي أَنْعَمْتَ عَلَيَّ وَعَلَىٰ وَالِدَيَّ وَأَنْ أَعْمَلَ صَالِحًا تَرْضَاهُ",
        "translation": "My Lord, enable me to be grateful for Your favor which You have bestowed upon me and upon my parents, and to do righteous deeds that please You.",
        "explanation": "A Quranic dua for turning blessings into gratitude and good action.",
        "source": "Quran 27:19",
        "tags": "gratitude thankful blessing parents success happiness",
    },
    "travel_safety": {
        "title": "For travel and safety",
        "arabic": "سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَٰذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ ۝ وَإِنَّا إِلَىٰ رَبِّنَا لَمُنقَلِبُونَ",
        "translation": "Glory be to the One who has subjected this to us, and we could not have otherwise subdued it. And indeed, to our Lord we will return.",
        "explanation": "A Quranic remembrance suited to journeys, reminding us that safety and return are from Allah.",
        "source": "Quran 43:13-14",
        "tags": "travel safety journey flight driving protection",
    },
    "general_good": {
        "title": "For complete good",
        "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ",
        "translation": "Our Lord, give us good in this world and good in the Hereafter, and protect us from the punishment of the Fire.",
        "explanation": "A comprehensive Quranic dua asking Allah for good in both worlds.",
        "source": "Quran 2:201",
        "tags": "general good success dua life akhirah protection",
    },
}

MOOD_OPTIONS = [
    "Select...",
    "Stress",
    "Sadness",
    "Gratitude",
    "Study / Exams",
    "Illness",
    "Fear / Anxiety",
    "Anger",
    "Confusion",
    "Tawbah (repentance)",
    "Seeking guidance",
    "Loneliness",
    "Grief",
    "Travel / Safety",
]

KEYWORD_TO_ID = {
    "stress": "anxiety_grief",
    "anxious": "anxiety_grief",
    "anxiety": "anxiety_grief",
    "worry": "anxiety_grief",
    "worried": "anxiety_grief",
    "sad": "anxiety_grief",
    "sadness": "anxiety_grief",
    "grief": "anxiety_grief",
    "debt": "anxiety_grief",
    "overwhelmed": "capacity_relief",
    "burden": "capacity_relief",
    "hard": "hardship_ease",
    "hardship": "hardship_ease",
    "exam": "study_exams",
    "exams": "study_exams",
    "study": "study_exams",
    "interview": "study_exams",
    "presentation": "study_exams",
    "confused": "guidance",
    "confusion": "guidance",
    "guidance": "guidance",
    "decision": "guidance",
    "tawbah": "repentance",
    "repentance": "repentance",
    "guilt": "repentance",
    "forgive": "repentance",
    "ill": "illness",
    "illness": "illness",
    "sick": "illness",
    "pain": "illness",
    "fear": "fear_reliance",
    "scared": "fear_reliance",
    "safety": "fear_reliance",
    "safe": "fear_reliance",
    "anger": "fear_reliance",
    "angry": "fear_reliance",
    "lonely": "loneliness_distress",
    "loneliness": "loneliness_distress",
    "distress": "loneliness_distress",
    "trapped": "loneliness_distress",
    "gratitude": "gratitude",
    "thankful": "gratitude",
    "thanks": "gratitude",
    "travel": "travel_safety",
    "journey": "travel_safety",
    "flight": "travel_safety",
}


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def local_match(user_mood: str) -> str:
    text = clean_text(user_mood)

    for keyword, dua_id in KEYWORD_TO_ID.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text):
            return dua_id

    best_id = "general_good"
    best_score = 0
    mood_words = set(re.findall(r"[a-zA-Z]+", text))

    for dua_id, item in DUA_LIBRARY.items():
        searchable = f"{item['title']} {item['tags']}".lower()
        score = sum(1 for word in mood_words if word in searchable)
        if score > best_score:
            best_id = dua_id
            best_score = score

    return best_id


def parse_json_object(raw: str) -> Dict[str, str]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start < 0 or end <= start:
            raise
        data = json.loads(raw[start:end])

    if not isinstance(data, dict):
        raise ValueError("Model did not return a JSON object.")

    return data


def ai_select_dua_id(api_key: str, user_mood: str, model: str) -> Optional[str]:
    if not api_key:
        return None

    allowed_ids = ", ".join(DUA_LIBRARY.keys())
    library_summary = "\n".join(
        f"- {dua_id}: {item['title']} | tags: {item['tags']}"
        for dua_id, item in DUA_LIBRARY.items()
    )

    system_prompt = (
        "You are only a classifier for a Dua Bot. "
        "Choose the single best dua_id from the allowed list. "
        "Do not generate Arabic. Do not generate translation. Do not generate explanation. "
        'Return only JSON like {"dua_id":"stress_anxiety"}.\n\n'
        f"Allowed dua_ids: {allowed_ids}\n\n"
        f"Dua library:\n{library_summary}"
    )

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=80,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Mood or situation: {user_mood}"},
        ],
    )

    raw = completion.choices[0].message.content or "{}"
    data = parse_json_object(raw)
    dua_id = data.get("dua_id")

    if dua_id in DUA_LIBRARY:
        return dua_id

    return None


def render_dua(item: Dict[str, str], matched_by: str) -> None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        f"<div class='badge'>{html.escape(matched_by)}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='arabic'>{html.escape(item['arabic'])}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='translation'><strong>Translation:</strong> {html.escape(item['translation'])}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='translation'><strong>Explanation:</strong> {html.escape(item['explanation'])}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='source'><strong>Source:</strong> {html.escape(item['source'])}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title("🕋 Dua Bot")
    st.markdown(
        "Get an authentic dua or Quranic ayah tailored to your current mood or situation."
    )

    api_key = os.environ.get("GROQ_API_KEY", "").strip()

    with st.sidebar:
        st.subheader("Settings")
        model = st.selectbox(
            "Groq model",
            ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
            index=0,
        )
        use_ai = st.toggle("Use AI to choose from verified library", value=bool(api_key))

        if not api_key:
            st.info(
                "No GROQ_API_KEY found. The app will still work using safe local matching."
            )

    st.subheader("How are you feeling or what do you need?")
    mood_select = st.selectbox(
        "Choose a mood / situation",
        options=MOOD_OPTIONS,
        index=0,
    )
    mood_text = st.text_input(
        "Or type your own situation or mood",
        placeholder="e.g. anxious about results...",
    )

    submit = st.button("Get Dua 💫", type="primary")

    if submit:
        selected = "" if mood_select == "Select..." else mood_select
        typed = mood_text.strip()
        user_mood = " ".join(part for part in [selected, typed] if part).strip()

        if not user_mood:
            st.error("Please select or type a mood before submitting.")
            st.stop()

        dua_id = None
        matched_by = "Matched locally"

        if use_ai and api_key:
            with st.spinner("Choosing the best match from the verified dua library..."):
                try:
                    dua_id = ai_select_dua_id(api_key, user_mood, model)
                    if dua_id:
                        matched_by = "AI selected from verified library"
                except Exception as exc:
                    st.warning(
                        "AI selection failed, so I used the safe local matcher instead."
                    )
                    with st.expander("Technical details"):
                        st.code(str(exc))

        if dua_id is None:
            dua_id = local_match(user_mood)

        render_dua(DUA_LIBRARY[dua_id], matched_by)

    st.markdown("</div>", unsafe_allow_html=True)
