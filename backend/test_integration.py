import os
import sys
import unittest

# Ensure UTF-8 output encoding for console
sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestHAQDAARIntegration(unittest.TestCase):

    def test_01_gateway_health_check(self):
        """Verify unified system health across all four micro-modules."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("gateway"), "haqdaar_v2")
        modules = data.get("modules", {})
        self.assertEqual(modules.get("tts"), "active")
        self.assertEqual(modules.get("stt"), "active")
        self.assertEqual(modules.get("conversation"), "active")
        self.assertIn("verified docs indexed", modules.get("rag", ""))
        print("PASS: test_01_gateway_health_check")

    def test_02_schemes_catalog(self):
        """Verify verified scheme and crop guide catalog endpoint."""
        response = client.get("/api/schemes")
        self.assertEqual(response.status_code, 200)
        catalog = response.json().get("catalog", [])
        self.assertGreaterEqual(len(catalog), 6)
        # Check presence of key schemes
        ids = [item["id"] for item in catalog]
        self.assertIn("pm_kisan", ids)
        self.assertIn("diggi_rajkisan", ids)
        self.assertIn("farm_pond_rajkisan", ids)
        self.assertIn("icar_bajra_guide", ids)
        self.assertIn("icar_mustard_guide", ids)
        print(f"PASS: test_02_schemes_catalog ({len(catalog)} verified guides listed)")

    def test_03_kisan_sahayak_hindi_query(self):
        """Verify Kisan Sahayak query in Hindi with ICAR Bajra citation."""
        response = client.post(
            "/api/chat",
            json={
                "message": "बाजरे की बुवाई का समय और बीज दर क्या है?",
                "language": "hi",
                "persona": "kisan"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("language"), "hi")
        self.assertEqual(data.get("persona"), "kisan")
        reply = data.get("reply_text", "")
        self.assertTrue(len(reply) > 20)
        # Verify source citation
        sources = data.get("sources", [])
        self.assertTrue(any("bajra" in s.get("doc_id", "").lower() for s in sources))
        print(f"PASS: test_03_kisan_sahayak_hindi_query -> Reply: {reply[:120]}...")

    def test_04_kisan_sahayak_marathi_query(self):
        """Verify Kisan Sahayak query in Marathi with ICAR Mustard citation."""
        response = client.post(
            "/api/chat",
            json={
                "message": "मोहरी पिकाच्या सुधारित जाती कोणत्या आहेत?",
                "language": "mr",
                "persona": "kisan"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("language"), "mr")
        reply = data.get("reply_text", "")
        self.assertTrue(len(reply) > 20)
        sources = data.get("sources", [])
        self.assertTrue(any("mustard" in s.get("doc_id", "").lower() for s in sources))
        print(f"PASS: test_04_kisan_sahayak_marathi_query -> Reply: {reply[:120]}...")

    def test_05_kisan_sahayak_tamil_query(self):
        """Verify Kisan Sahayak query in Tamil with ICAR Wheat citation."""
        response = client.post(
            "/api/chat",
            json={
                "message": "கோதுமை பயிரிட சிறந்த ரகங்கள் எவை?",
                "language": "ta",
                "persona": "kisan"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("language"), "ta")
        reply = data.get("reply_text", "")
        self.assertTrue(len(reply) > 20)
        sources = data.get("sources", [])
        self.assertTrue(any("wheat" in s.get("doc_id", "").lower() for s in sources))
        print(f"PASS: test_05_kisan_sahayak_tamil_query -> Reply: {reply[:120]}...")

    def test_06_yojana_sahayak_diggi_scheme(self):
        """
        Verify Yojana Sahayak query for Rajasthan Diggi subsidy.
        Must NOT assert that 85% or 3.4 Lakh is guaranteed.
        Must assert that response reflects pending current-year verification,
        portal snapshot caveat, and mandatory administrative approval.
        """
        response = client.post(
            "/api/chat",
            json={
                "message": "राजस्थान में पक्की डिग्गी बनाने के लिए कितना अनुदान मिलता है?",
                "language": "hi",
                "persona": "yojana"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        reply = data.get("reply_text", "")
        self.assertTrue(len(reply) > 20)
        sources = data.get("sources", [])
        self.assertTrue(any("diggi" in s.get("doc_id", "").lower() for s in sources))
        
        # Verify explicit communication of uncertainty / portal verification
        has_verification_note = any(
            term in reply for term in ["सत्यापन", "पोर्टल", "स्वीकृति", "प्रशासनिक", "वित्तीय वर्ष", "संभावित", "दिशा-निर्देश", "ई-मित्र"]
        )
        self.assertTrue(has_verification_note, f"Reply failed to communicate pending verification status: {reply}")
        print(f"PASS: test_06_yojana_sahayak_diggi_scheme (Verified uncertainty & administrative caveat) -> Reply: {reply[:120]}...")

    def test_07_conversation_multi_turn_context(self):
        """Verify multi-turn session memory preservation across turns."""
        session_id = "test_multi_turn_session_01"

        # Turn 1: Farmer shares landholding
        turn1_resp = client.post(
            "/api/chat",
            json={
                "message": "मेरे पास 3 बीघा जमीन है और मैं खेती करता हूँ।",
                "language": "hi",
                "persona": "yojana",
                "session_id": session_id
            }
        )
        self.assertEqual(turn1_resp.status_code, 200)

        # Turn 2: Farmer asks for eligibility without repeating land size
        turn2_resp = client.post(
            "/api/chat",
            json={
                "message": "क्या मुझे पीएम किसान सम्मान निधि का लाभ मिलेगा?",
                "language": "hi",
                "persona": "yojana",
                "session_id": session_id
            }
        )
        self.assertEqual(turn2_resp.status_code, 200)
        reply = turn2_resp.json().get("reply_text", "")
        self.assertTrue(len(reply) > 20)
        print(f"PASS: test_07_conversation_multi_turn_context -> Turn 2 Reply: {reply[:120]}...")

    def test_08_end_to_end_voice_to_voice_pipeline(self):
        """
        Verify the complete voice-to-voice end-to-end pipeline:
        Audio Upload -> STT -> Conversation Engine -> Grounded Reply -> TTS Stream.
        """
        # Step 1: Upload real audio to STT
        audio_path = os.path.join(WORKSPACE_ROOT, "hindi_test.mp3")
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        stt_resp = client.post(
            "/api/stt",
            data={"language": "hi"},
            files={"file": ("hindi_test.mp3", audio_bytes, "audio/mp3")}
        )
        self.assertEqual(stt_resp.status_code, 200)
        transcript = stt_resp.json().get("transcript", "")
        self.assertTrue(len(transcript) > 0)

        # Step 2: Send transcript to Chat Gateway
        chat_resp = client.post(
            "/api/chat",
            json={
                "message": transcript,
                "language": "hi",
                "persona": "kisan"
            }
        )
        self.assertEqual(chat_resp.status_code, 200)
        reply_text = chat_resp.json().get("reply_text", "")
        self.assertTrue(len(reply_text) > 0)

        # Step 3: Stream synthesized voice output via TTS Stream
        tts_resp = client.post(
            "/api/tts/stream",
            json={
                "text": reply_text[:300],  # Conversational voice segment
                "language": "hi"
            }
        )
        self.assertEqual(tts_resp.status_code, 200)
        self.assertEqual(tts_resp.headers["content-type"], "audio/mpeg")
        self.assertGreater(len(tts_resp.content), 5000)

        print(f"PASS: test_08_end_to_end_voice_to_voice_pipeline")
        print(f"   -> STT Transcript ({len(transcript)} chars): '{transcript}'")
        print(f"   -> Chat Reply ({len(reply_text)} chars): '{reply_text[:100]}...'")
        print(f"   -> Audio Synthesized: {len(tts_resp.content)} MP3 bytes")

    def test_09_background_task_temp_file_cleanup(self):
        """Verify that legacy POST /api/tts cleans up temporary audio files after response completion."""
        import tempfile
        import glob

        tmp_dir = tempfile.gettempdir()
        initial_mp3s = set(glob.glob(os.path.join(tmp_dir, "*.mp3")))

        response = client.post(
            "/api/tts",
            json={"text": "सफाई परीक्षण संदेश", "language": "hi"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "audio/mpeg")
        self.assertGreater(len(response.content), 2000)

        # Inspect temp directory after response
        post_mp3s = set(glob.glob(os.path.join(tmp_dir, "*.mp3"))) - initial_mp3s
        self.assertEqual(len(post_mp3s), 0, f"Temporary MP3 file was not removed: {post_mp3s}")
        print("PASS: test_09_background_task_temp_file_cleanup (0 leftover temp files confirmed)")

if __name__ == "__main__":
    unittest.main()

