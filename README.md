# 🌾 HAQDAAR — हकदार
### A Multilingual, Voice-First AI Assistant for Rural India

> Making agricultural guidance and government scheme information more accessible to rural citizens—through voice, in their own language.

**HAQDAAR** is a multilingual, voice-first AI assistant designed to help rural citizens and farmers access agricultural guidance and government scheme information. It supports Hindi, Marathi, and Tamil, allowing users to ask questions naturally through voice or text.

The project focuses on accessibility, trustworthy information, and a simple user experience for citizens who may find complex government portals difficult to navigate.

---

## 📌 Problem Statement

Rural citizens and farmers often face challenges accessing reliable agricultural information and understanding government schemes.

- Information may be difficult to find across multiple websites and departments.
- Official information may be written in complex language.
- Language barriers can make digital services less accessible.
- Farmers may struggle to identify relevant scheme information or understand where to seek official assistance.

HAQDAAR aims to reduce these barriers through a simple, multilingual, voice-first interface.

## 💡 Our Solution

HAQDAAR provides a conversational interface where users can speak or type a question in their preferred supported language.

The system combines speech recognition, conversational AI, retrieval from a knowledge base, and text-to-speech to provide accessible responses.

The assistant is organized into two personas:

| Persona | Purpose |
|---|---|
| 🌾 **Kisan Sahayak** | Agricultural guidance and crop-related questions |
| 🏛️ **Yojana Sahayak** | Government scheme information and guidance |

## ✨ Key Features

- **Multilingual interaction:** Hindi, Marathi, and Tamil.
- **Voice-first experience:** Ask questions using the microphone.
- **Text input:** Type questions or correct recognized speech before sending.
- **Speech-to-text:** Converts spoken questions into text.
- **Text-to-speech:** Reads assistant responses aloud.
- **Two assistant personas:** Kisan Sahayak and Yojana Sahayak.
- **Knowledge-base retrieval:** Uses available reference documents to support answers.
- **Source information:** Displays source details when supplied by the backend.
- **Voice controls:** Stop listening and stop spoken responses.
- **Responsive interface:** Designed for desktop and mobile use.
- **Scheme discovery:** Explore scheme information available in the knowledge base.

> HAQDAAR is an information and guidance assistant. It does not replace official government authorities, agricultural experts, or formal eligibility decisions.

## 🧭 How It Works

1. The user selects a language.
2. The user chooses Kisan Sahayak or Yojana Sahayak.
3. The user speaks or types a question.
4. Speech input is converted into text.
5. The conversational backend processes the question.
6. The retrieval system searches available reference material.
7. HAQDAAR generates a response using the retrieved context.
8. The response is displayed and can be played through text-to-speech.

## 🏗️ System Architecture

```text
                 ┌──────────────────────┐
                 │       Citizen        │
                 │   Voice or Text      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   React Frontend     │
                 │ Language & Persona   │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │ Speech-to-Text (STT) │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   FastAPI Backend    │
                 │ Conversation Service │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   RAG Knowledge Base │
                 │ Reference Documents  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Generated Response   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Text-to-Speech     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Response to Citizen  │
                 └──────────────────────┘
```

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| Speech Recognition | Browser Web Speech API, Gemini-based fallback |
| Text-to-Speech | Edge TTS |
| AI Conversation | Gemini |
| Retrieval | RAG-based knowledge retrieval |
| API Testing | FastAPI Swagger UI |
| Version Control | Git, GitHub |

*The exact models and versions may vary according to the project's current configuration.*

## 📂 Project Structure

```text
HAQDAAR/
├── backend/
│   ├── main.py
│   ├── conversation_service.py
│   ├── rag_kb.py
│   ├── scheme_adapter.py
│   ├── stt_service.py
│   ├── tts_service.py
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── index.html
│
├── data/
├── docs/
├── .gitignore
└── README.md
```

*This is a representative structure. Update it if the actual repository differs.*

## 🚀 Getting Started

### Prerequisites

Install the following:

- Python 3.10 or later
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/HAQDAAR.git
cd HAQDAAR
```

### 2. Set up the backend

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create the required environment configuration based on the project's current requirements. Add your API keys locally—**never commit secrets to GitHub**.

Start the backend:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

Backend API:

```text
http://127.0.0.1:8001
```

Interactive API documentation:

```text
http://127.0.0.1:8001/docs
```

### 3. Set up the frontend

Open a second terminal:

```powershell
npm --prefix frontend install
npm --prefix frontend run dev
```

Open the local frontend:

```text
http://localhost:5173
```

Keep both the backend and frontend terminals running while testing the application.

## 🧪 Testing

Run the frontend production build:

```powershell
npm --prefix frontend run build
```

Run the backend regression tests:

```powershell
.\venv\Scripts\python.exe -m unittest -v backend.test_persona_routing
```

Additional integration tests can be run using the test modules available in the repository.

## 🔐 Trust, Safety & Limitations

HAQDAAR is designed to provide helpful guidance while avoiding unsupported claims.

- Responses should rely on available reference material.
- Source details should be displayed only when provided by the backend.
- Current scheme benefits, eligibility rules, and financial-year details require verification against official sources.
- The assistant does not make official eligibility decisions.
- Users should not share Aadhaar OTPs, bank OTPs, passwords, or other sensitive credentials.
- Agricultural recommendations should be confirmed with qualified local agricultural experts when necessary.

## 👥 Team

**Team Name:** [Add team name]  
**Hackathon:** Sphinx'26 — MNIT Jaipur

| Team Member | Contribution |
|---|---|
| [Member 1] | [Role] |
| [Member 2] | [Role] |
| [Member 3] | [Role] |
| [Member 4] | [Role] |

## 🎯 Future Enhancements

- Expand the verified agricultural and government scheme knowledge base.
- Add more Indian languages.
- Improve speech recognition for regional accents and noisy environments.
- Add clearer scheme discovery and navigation.
- Conduct usability testing with native speakers and rural users.
- Improve accessibility for users with limited digital literacy.

## 📄 License

This project is developed for the Sphinx'26 hackathon.

Add a license before permitting reuse or redistribution.

---

**HAQDAAR — हकदार**  
*Accessible information. Trusted guidance. Every voice matters.*
