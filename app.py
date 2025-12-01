# app.py
import os
import json
import traceback
from typing import Optional

import streamlit as st
from groq import Groq
from groq import GroqError

st.set_page_config(page_title="Dua Bot", page_icon="🕋", layout="centered")

# Inline styling
st.markdown(
    """
    <style>
    .main-container {max-width: 760px; margin: 0 auto;}
    .card {background: #fff; border-radius: 12px; box-shadow: 0 6px 18px rgba(16,24,40,0.08); padding: 18px; margin-top: 12px;}
    .arabic {font-size: 28px; font-weight: 600; direction: rtl; text-align: right; margin-bottom: 8px;}
    .translation {font-size: 16px; color: #111827; margin-bottom: 6px;}
    .source {font-size: 13px; color: #6b7280; margin-top: 8px;}
    .small {font-size: 12px; color: #6b7280;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title("🕋 Dua Bot")
    st.markdown(
        "Get an authentic dua or Quranic ayah tailored to your current mood or situation."
    )

    # --- CHECK API KEY (required) ---
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error(
            "No GROQ_API_KEY found in environment.\n\n"
            "In Google Colab, set it using:\n"
            "`os.environ['GROQ_API_KEY'] = 'your_key_here'`"
        )
        st.stop()

    # Mood selection
    st.subheader("How are you feeling or what do you need?")
    mood_select = st.selectbox(
        "Choose a mood / situation (or type your own)",
        options=[
            "Select...","Stress", "Sadness", "Gratitude", "Study / Exams", "Illness",
            "Fear / Anxiety", "Anger", "Confusion", "Tawbah (repentance)",
            "Seeking guidance", "Loneliness", "Grief", "Travel / Safety"
        ],
        index=0
    )
    mood_text = st.text_input("Or type your own situation or mood", placeholder="e.g. anxious about results...")

    submit = st.button("Get Dua 💫")

    SYSTEM_PROMPT = (
        "You are an expert Islamic scholar. Provide only authentic duas or Quranic ayat. "
        "Return output strictly as JSON with keys: arabic, translation, explanation, source."
    )

    def call_groq(api_key: str, system_prompt: str, user_message: str, model: str = "llama-3.3-70b-versatile"):
        try:
            client = Groq(api_key=api_key)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]

            completion = client.chat.completions.create(
                messages=messages,
                model=model,
            )
            raw = completion.choices[0].message.content

            try:
                return json.loads(raw)
            except:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                return json.loads(raw[start:end])

        except Exception as e:
            raise RuntimeError(f"API Error: {e}\n{traceback.format_exc()}")

    if submit:
        if mood_text.strip():
            user_mood = mood_text.strip()
        elif mood_select != "Select...":
            user_mood = mood_select
        else:
            st.error("Please select or type a mood before submitting.")
            st.stop()

        user_message = (
            f"Give me an authentic dua or Quranic ayah for someone feeling: {user_mood}. "
            "Provide Arabic, translation, explanation, and source in JSON."
        )

        with st.spinner("Finding the perfect dua for your heart..."):
            try:
                result = call_groq(api_key, SYSTEM_PROMPT, user_message)
            except Exception as e:
                st.error("Failed to fetch dua from Groq.")
                st.exception(e)
                result = None

        if result:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(f"<div class='arabic'>{result.get('arabic','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='translation'><strong>Translation:</strong> {result.get('translation','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='translation'><strong>Explanation:</strong> {result.get('explanation','')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='source'><strong>Source:</strong> {result.get('source','')}</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                "<div class='small'>Always verify references with a qualified scholar.</div>",
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)
