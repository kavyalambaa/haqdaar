# HAQDAAR 🌾
### A Multilingual, Voice-First Assistant for Rural Citizens

**HAQDAAR** is a voice-first assistant designed to help rural citizens access useful information about agricultural practices and government schemes in their own language. It combines speech interaction, AI-powered responses, and Retrieval-Augmented Generation (RAG) to make information easier to understand and access.

Built by **Team Voyagers**.

## 🌐 Live Demo

**Try HAQDAAR here:** [https://haqdaar-tau.vercel.app/](https://haqdaar-tau.vercel.app/)

- **Frontend:** Vercel
- **Backend API:** [https://haqdaar.onrender.com](https://haqdaar.onrender.com)
- **API Documentation:** [Swagger UI](https://haqdaar.onrender.com/docs)

> HAQDAAR is a multilingual voice assistant designed to help citizens access information about government schemes and agricultural support in Hindi, Marathi, and Tamil.

---

## 🌟 Key Features

- **Multilingual interaction:** Supports Hindi, Marathi, and Tamil.
- **Voice-first experience:** Users can speak their queries using speech-to-text (STT).
- **AI-powered responses:** Generates conversational responses through an LLM.
- **RAG-based information retrieval:** Uses curated research documents and scheme-related sources to ground responses.
- **Agriculture assistance:** Provides information related to crops such as bajra, mustard, and wheat.
- **Government scheme assistance:** Helps users explore relevant agricultural schemes and information.
- **Text-to-speech (TTS):** Converts assistant responses into spoken audio.
- **Persona-based routing:** Routes queries to suitable assistant personas.
- **Source-aware responses:** Uses retrieved information and source metadata to support responses.

> HAQDAAR is an information assistant. It does not replace official government portals, agricultural experts, or professional advice.

---

## 🧠 How It Works

1. The user asks a question by voice or text.
2. Speech input is processed through STT when needed.
3. The backend identifies the query context and relevant assistant persona.
4. The RAG system retrieves relevant information from the curated knowledge base.
5. The LLM generates a response using the available context.
6. The response is displayed as text and can be converted into speech through TTS.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI |
| AI / LLM | Gemini API |
| Knowledge Retrieval | Retrieval-Augmented Generation (RAG) |
| Speech Input | Speech-to-Text (STT) |
| Speech Output | Text-to-Speech (TTS) |
| Data Sources | Curated agricultural research and scheme documents |
| Version Control | Git, GitHub |

---

## 📁 Project Structure

```text
haqdaar/
├── backend/
│   ├── conversation_service.py
│   ├── extractor.py
│   ├── main.py
│   ├── rag_kb.py
│   ├── scheme_adapter.py
│   ├── stt_service.py
│   ├── tts_service.py
│   └── tests/
│
├── data/
│   ├── eval/
│   ├── research/
│   └── schemes/
│
├── docs/
│   ├── M2_BASELINE.md
│   └── research and scheme documentation
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── services/
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js and npm
- A Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/kavyalambaa/haqdaar.git
cd haqdaar
```

### 2. Set up the backend

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

Configure the required environment variables in a `.env` file. Keep API keys private and never commit them to GitHub.

Start the FastAPI server:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

The backend API will be available at:

- API: `http://127.0.0.1:8001`
- Swagger documentation: `http://127.0.0.1:8001/docs`

### 3. Set up the frontend

Open another terminal:

```powershell
npm --prefix frontend install
npm --prefix frontend run dev
```

Open the frontend at:

`http://localhost:5173`

---

## 🔌 API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Health check |
| `GET /api/schemes` | Scheme information |
| `POST /api/chat` | Chat interaction |
| `POST /api/stt` | Speech-to-text |
| `POST /api/tts` | Text-to-speech |
| `POST /api/tts/stream` | Streaming text-to-speech |

See the interactive API documentation at `/docs` when the backend is running.

---

## 📚 Knowledge Base

HAQDAAR uses curated documents and metadata to support its retrieval system.

The repository includes material related to:

- Bajra cultivation
- Mustard cultivation and varieties
- Wheat cultivation
- Agricultural infrastructure and scheme information
- Rajasthan's Raj Kisan portal and related schemes

The knowledge base is intended to help responses remain grounded in relevant source material rather than relying only on general model knowledge.

---

## 👥 Team Voyagers

| Team Member |
|---|
| Kanishka Goyal |
| Aryan Tiwari |
| Shrishti Tiwari |
| Kavya Lamba |

---

## 🔮 Future Enhancements

- Improve speech recognition for regional accents and agricultural terminology.
- Expand verified knowledge sources and scheme coverage.
- Strengthen low-bandwidth support.
- Explore SMS-based assistance.
- Improve testing across languages,
