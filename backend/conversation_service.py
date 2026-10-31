import os
import json
import uuid
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rag_kb import kb
from scheme_adapter import SchemeEligibilityAdapter

load_dotenv()

logger = logging.getLogger("haqdaar.conversation")

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(api_key=API_KEY) if API_KEY else None

# In-memory session store (session_id -> list of turn messages)
SESSIONS: Dict[str, List[Dict[str, str]]] = {}

SYSTEM_PROMPTS = {
    "hi": """आप 'हकदार' (HAQDAAR) के मित्रवत और विश्वसनीय बहुभाषी सहायक हैं।
आपका उद्देश्य ग्रामीण नागरिकों और किसानों को कृषि (किसान सहायक) और सरकारी योजनाओं (योजना सहायक) की प्रामाणिक जानकारी देना है।

सख्त सुरक्षा एवं सत्यनिष्ठा नियम:
1. भाषा: उत्तर हमेशा सरल, स्पष्ट और सम्मानजनक हिन्दी भाषा (देवनागरी लिपि) में दें।
2. स्रोत एवं उद्धरण प्रतिबंध: केवल और केवल 'सत्यापित संदर्भ' (VERIFIED OFFICIAL CONTEXT) में दिए गए आधिकारिक स्रोतों का ही उद्धरण दें। कभी भी मनगढ़ंत ICAR संस्थान, काल्पनिक पुस्तक का नाम, फर्जी वर्ष या अपुष्ट स्रोत न बनाएं।
3. अनुपलब्ध जानकारी: यदि नागरिक के प्रश्न का उत्तर 'सत्यापित संदर्भ' में मौजूद नहीं है, तो स्पष्ट और विनम्रतापूर्वक कहें: "क्षमा करें, इस विषय पर हमारे पास वर्तमान में प्रमाणित ICAR या सरकारी दस्तावेज़ उपलब्ध नहीं है। कृपया अपने निकटतम कृषि विज्ञान केंद्र (KVK) अथवा संबंधित विभाग से संपर्क करें।"
4. कीटनाशक एवं रसायन सुरक्षा: कभी भी बिना आधिकारिक सिफारिश के रासायनिक कीटनाशकों या खरपतवारनाशकों की खुराक न बताएं।
5. सरकारी योजनाएं एवं अनुदान: योजनाओं (जैसे डिग्गी, खेत तलाई, पीएम-किसान) के लिए हमेशा स्पष्ट करें कि यह 'संभावित संकेत' है, गारंटी नहीं। चालू वित्तीय वर्ष के स्वीकृत अनुदान और नियमों का सत्यापन राज किसान पोर्टल अथवा कृषि विभाग से अनिवार्य है। डिग्गी निर्माण के लिए प्रशासनिक स्वीकृति (Administrative Approval) पूर्व में प्राप्त करना अनिवार्य है।
6. गोपनीयता: कभी भी चैट में आधार कार्ड, ओटीपी, जन आधार या बैंक खाता नंबर न मांगें।""",

    "mr": """तुम्ही 'हकदार' (HAQDAAR) चे विश्वासू आणि मार्गदर्शक बहुभाषिक सहाय्यक आहात.
ग्रामीण नागरिक आणि शेतकर्‍यांना कृषी (किसान सहायक) आणि सरकारी योजनांविषयी (योजना सहायक) अधिकृत माहिती देणे हे तुमचे काम आहे.

सुरक्षा आणि सत्यनिष्ठा नियम:
1. भाषा: उत्तर नेहमी सोप्या, स्पष्ट आणि आदरयुक्त मराठी भाषेत (देवनागरी लिपी) द्या.
2. स्रोत व संदर्भ: केवळ 'सत्यापित संदर्भ' (VERIFIED OFFICIAL CONTEXT) मधील दिलेल्या अधिकृत स्रोतांचाच उल्लेख करा. स्वतःच्या मनाने कोणतेही काल्पनिक ICAR संस्था किंवा खोटे स्रोत तयार करू नका.
3. माहिती अनुपलब्ध असल्यास: जर संदर्भामध्ये विचारलेल्या प्रश्नाची माहिती उपलब्ध नसेल, तर स्पष्टपणे सांगा: "क्षमस्व, या विषयावर आमच्याकडे सध्या प्रमाणित ICAR किंवा अधिकृत सरकारी दस्तऐवज उपलब्ध नाही. अचूक माहितीसाठी कृपया स्थानिक कृषी विज्ञान केंद्र (KVK) शी संपर्क साधा."
4. कीटकनाशक सुरक्षा: अनधिकृत किंवा लेबल पडताळणीशिवाय कोणत्याही रासायनिक कीटकनाशकांची शिफारस करू नका.
5. योजना व अनुदान: योजनांची माहिती केवळ संभाव्य मार्गदर्शन आहे, कोणतीही हमी नाही. चालू आर्थिक वर्षाच्या नियमांची पडताळणी संबंधित पोर्टलवर आवश्यक आहे.
6. गोपनीयता: चॅटमध्ये कधीही आधार क्रमांक, जन आधार किंवा बँक खाते मागू नका.""",

    "ta": """நீங்கள் 'ஹக்தார்' (HAQDAAR) இன் நம்பகமான மற்றும் நட்பு வாய்ந்த கிராமப்புற குரல் உதவியாளர்.
விவசாயிகள் மற்றும் பொதுமக்களுக்கு விவசாய வழிகாட்டுதல் (கிசான் சகாயக்) மற்றும் அரசு நலத்திட்டங்கள் (யோஜனா சகாயக்) குறித்த உண்மையான தகவல்களை வழங்குவதே உங்கள் பணி.

பாதுகாப்பு விதிகள்:
1. மொழி: எளிய, மரியாதையான தமிழ் மொழியில் பதிலளிக்கவும்.
2. அங்கீகரிக்கப்பட்ட ஆதாரங்கள் மட்டுமே: சரிபார்க்கப்பட்ட சூழலில் (VERIFIED OFFICIAL CONTEXT) வழங்கப்பட்டுள்ள அதிகாரப்பூர்வ ஆதாரங்களை மட்டுமே குறிப்பிடவும். புதிய அல்லது போலியான ICAR நிறுவன பெயர்களையோ, ஆண்டுகளையோ உருவாக்க வேண்டாம்.
3. தகவல் இல்லையெனில்: கேட்கப்பட்ட கேள்விக்கான தகவல் சரிபார்க்கப்பட்ட ஆவணங்களில் இல்லை என்றால், நேர்மையாகக் கூறுங்கள்: "மன்னிக்கவும், இந்த குறிப்பிட்ட கேள்விக்கான அதிகாரப்பூர்வ ICAR அல்லது அரசு ஆவணங்கள் தற்போது எங்களிடம் இல்லை. துல்லியமான தகவலுக்கு உங்கள் வட்டார வேளாண் அலுவலகம் அல்லது கேவிகே (KVK) ஐ அணுகவும்."
4. பூச்சிக்கொல்லி எச்சரிக்கை: உறுதிப்படுத்தப்படாத ரசாயன மருந்துகளை பரிந்துரைக்காதீர்கள்.
5. அரசு திட்டங்கள்: திட்ட விவரங்கள் வழிகாட்டுதலுக்கு மட்டுமே. தற்போதைய நிதி ஆண்டுக்கான இறுதி விதிமுறைகள் மற்றும் ஒப்புதல் அரசு அலுவலர்களாலேயே வழங்கப்படும்.
6. தனியுரிமை: ஆதார் எண் அல்லது வங்கி கணக்கு விவரங்களை ஒருபோதும் கேட்க வேண்டாம்."""
}

class ConversationEngine:
    """Orchestrates citizen dialogue, verified knowledge retrieval, and grounded response synthesis."""

    def __init__(self):
        self.model = MODEL_NAME

    def _detect_persona(self, query: str, user_persona: Optional[str]) -> str:
        q_lower = query.lower()

        # 1. Conservative Scheme Intent Detection (Government Schemes)
        scheme_keywords = [
            "जल हौज", "हौज", "हौज़", "jal hauz", "hauz",
            "डिग्गी", "diggi",
            "सब्सिडी", "subsidy",
            "अनुदान",
            "तलाई", "खेत तलाई", "farm pond", "तालाब", "pond",
            "पाइपलाइन", "pipeline",
            "योजना", "scheme",
            "पात्रता", "eligibility",
            "आवेदन", "application", "आवेदन प्रक्रिया",
            "किस्त", "pm kisan", "पीएम किसान",
            "திட்டம்", "மானியம்"
        ]

        # 2. Conservative Crop/Agriculture Intent Detection (ICAR Agriculture)
        crop_keywords = [
            "बुवाई", "पेरणी", "sowing",
            "बीज दर", "बियाणे प्रमाण", "seed rate",
            "किस्में", "किस्म", "जाती", "varieties", "variety", "ரகங்கள்",
            "खाद", "खत", "fertilizer", "manure",
            "फसल", "पीक", "crop", "பயிர்",
            "रोग", "disease", "நோய்",
            "कीट", "कीटक", "pest", "பூச்சி",
            "बाजरा", "बाजरे", "बाजरी", "bajra", "கம்பு",
            "सरसों", "राई", "मोहरी", "mustard", "கடுகு",
            "गेहूं", "गहू", "wheat", "கோதுமை"
        ]

        has_scheme = any(w in q_lower for w in scheme_keywords)
        has_crop = any(w in q_lower for w in crop_keywords)

        # Strong scheme intent routes to yojana, even if kisan was selected
        if has_scheme and not has_crop:
            return "yojana"

        # Strong crop intent routes to kisan, even if yojana was selected
        if has_crop and not has_scheme:
            return "kisan"

        # If ambiguous (both or neither), preserve the valid user-selected persona
        if user_persona in ["kisan", "yojana"]:
            return user_persona

        # Fallback default if no persona is selected
        return "kisan"

    def _prepare_spoken_text(self, reply_text: str, max_chars: int = 500) -> str:
        """
        Prepares a clean, sentence-bounded spoken version for TTS.
        Ensures the complete written answer is preserved for UI display,
        while spoken audio stays within comfortable conversational lengths (<= 500 chars).
        """
        clean = reply_text.strip()
        if len(clean) <= max_chars:
            return clean

        # Sentence-bounded slicing
        for delim in ["।", ".", "\n"]:
            sentences = clean.split(delim)
            accumulated = ""
            for s in sentences:
                candidate = (accumulated + delim + s).strip() if accumulated else s.strip()
                if len(candidate) <= max_chars:
                    accumulated = candidate
                else:
                    break
            if accumulated and len(accumulated) >= 40:
                return accumulated + (delim if delim != "\n" else "।")

        return clean[:max_chars].rsplit(" ", 1)[0] + "..."

    def process_turn(
        self,
        message: str,
        language: str = "hi",
        persona: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # 1. Session and language normalization
        sess_id = session_id or str(uuid.uuid4())
        clean_lang = language.lower().strip() if language in ["hi", "mr", "ta"] else "hi"
        resolved_persona = self._detect_persona(message, persona)

        if sess_id not in SESSIONS:
            SESSIONS[sess_id] = []

        history = SESSIONS[sess_id]

        # 2. Knowledge Retrieval from Verified Documents
        retrieved_items = kb.retrieve(query=message, persona=resolved_persona, language=clean_lang)
        
        # Build context prompt
        context_blocks = []
        source_badges = []

        for item in retrieved_items:
            doc_title = item.get("title") or item.get("scheme") or item.get("crop")
            inst = item.get("institution", "Government / ICAR")
            year = item.get("year", 2025)
            source_badges.append({
                "doc_id": item.get("doc_id"),
                "title": doc_title,
                "institution": inst,
                "year": year
            })

            block = f"--- [VERIFIED DOCUMENT: {doc_title} ({inst}, {year})] ---\n"
            if item.get("facts"):
                block += "Facts: " + " | ".join(item["facts"]) + "\n"
            if item.get("benefits"):
                block += "Benefits: " + json.dumps(item["benefits"], ensure_ascii=False) + "\n"
            if item.get("eligibility"):
                block += "Eligibility: " + json.dumps(item["eligibility"], ensure_ascii=False) + "\n"
            if item.get("disclaimer"):
                block += "Mandatory Note: " + item["disclaimer"] + "\n"
            context_blocks.append(block)

        context_text = "\n".join(context_blocks) if context_blocks else "No specific research guide matched in our approved database."

        # 3. Construct Model Prompt
        system_instruction = SYSTEM_PROMPTS.get(clean_lang, SYSTEM_PROMPTS["hi"])
        
        prompt = f"""[CITIZEN MESSAGE]: {message}
[SELECTED ASSISTANT]: {'किसान सहायक (Kisan Sahayak - Agriculture)' if resolved_persona == 'kisan' else 'योजना सहायक (Yojana Sahayak - Schemes)'}
[SELECTED LANGUAGE]: {clean_lang}

[VERIFIED OFFICIAL CONTEXT]:
{context_text}

[CONVERSATION RECENT TURNS]:
{json.dumps(history[-4:], ensure_ascii=False)}

Please answer the citizen directly, warmly, and concisely in {clean_lang}. 
IMPORTANT: Only include citations that exist in the supplied verified context. If no context matches, state that verified information is currently unavailable and advise visiting the local office/KVK."""

        # 4. Generate Grounded Response
        try:
            if not client:
                raise RuntimeError("Gemini Client not initialized.")

            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                    max_output_tokens=800
                )
            )

            reply_text = (response.text or "").strip()

        except Exception as e:
            logger.exception(f"Conversation generation failed: {e}")
            # Fallback safe responses in respective languages
            fallbacks = {
                "hi": "नमस्ते, तकनीकी समस्या के कारण इस समय उत्तर देने में असमर्थ हूँ। कृपया पुनः प्रयास करें।",
                "mr": "नमस्कार, तांत्रिक अडचणीमुळे सध्या उत्तर देता येत नाही. कृपया पुन्हा प्रयत्न करा.",
                "ta": "வணக்கம், தொழில்நுட்பக் கோளாறு காரணமாக தற்போது பதிலளிக்க முடியவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
            }
            reply_text = fallbacks.get(clean_lang, fallbacks["hi"])

        # 5. Prepare Safe Spoken Text (<= 500 chars) for TTS
        spoken_text = self._prepare_spoken_text(reply_text, max_chars=500)

        # 6. Record session history
        history.append({"user": message, "assistant": reply_text})
        if len(history) > 10:
            history.pop(0)

        return {
            "session_id": sess_id,
            "reply_text": reply_text,
            "spoken_text": spoken_text,
            "language": clean_lang,
            "persona": resolved_persona,
            "sources": source_badges,
            "audio_stream_url": f"/api/tts/stream"
        }

engine = ConversationEngine()

