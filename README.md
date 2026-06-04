# 🕋 Dua Bot

An AI-powered Islamic assistant that provides authentic duas and Quranic ayat based on a user's emotional state or life situation.

Whether you're feeling stressed, anxious, grateful, confused, or seeking guidance, Dua Bot helps you discover relevant supplications and verses along with their translation, explanation, and source.

---

## 🌟 Features

* Select from common moods and situations
* Enter a custom emotional state or personal situation
* Receive an authentic dua or Quranic ayah
* View:

  * Arabic text
  * English translation
  * Brief explanation
  * Source reference
* Clean and responsive Streamlit interface
* Powered by a Large Language Model through the Groq API

---

## 🖥️ Demo

Example use cases:

* Stress
* Study / Exams
* Fear / Anxiety
* Illness
* Tawbah (Repentance)
* Seeking Guidance
* Grief
* Loneliness
* Travel / Safety

Example Input:

Anxious about my exam results

Example Output:

Arabic Dua

Translation

Explanation

Source Reference

---

## 🏗️ Tech Stack

### Frontend

* Streamlit

### Backend

* Python

### AI Model

* Llama 3.3 70B Versatile

### API Provider

* Groq

### Data Handling

* JSON Parsing

---

## ⚙️ How It Works

1. User selects or enters a mood/situation.
2. The application sends a structured prompt to the LLM.
3. The model is instructed to return output strictly in JSON format.
4. The response includes:

   * Arabic text
   * Translation
   * Explanation
   * Source
5. The JSON is parsed and displayed through Streamlit.

---

## 📂 Project Structure

```text
dua-bot/
│
├── README.md
├── app.py
├── requirements.txt
```

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/dua-bot.git
cd dua-bot
```

### Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create an environment variable for your Groq API Key.

Windows:

```bash
set GROQ_API_KEY=your_api_key_here
```

Mac/Linux:

```bash
export GROQ_API_KEY=your_api_key_here
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The application will launch in your browser.

---

## 📋 Requirements

```text
streamlit
groq
```

Install them using:

```bash
pip install -r requirements.txt
```

---

## 🧠 Prompt Engineering Approach

The model is guided through a system prompt that instructs it to:

* Act as an expert Islamic scholar
* Provide authentic duas or Quranic ayat
* Return responses in a strict JSON format
* Include:

  * Arabic text
  * Translation
  * Explanation
  * Source

To improve reliability, the application also includes fallback JSON extraction logic when the model returns extra text around the JSON response.

---

## ⚠️ Limitations

* Responses depend on the language model's accuracy.
* Users should verify religious references independently.
* Internet access is required for API communication.
* The project is intended for educational and learning purposes.

---


## 🎯 Learning Outcomes

This project helped me explore:

* Generative AI applications
* Prompt engineering
* API integration
* Error handling
* Streamlit application development
* User-focused AI design

---


## 👩‍💻 Author

Built with Python, Streamlit, and Generative AI as a project exploring how technology can be used to provide beneficial Islamic resources.

If you found this project interesting, consider giving the repository a ⭐.
