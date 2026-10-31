import os
import sys
import unittest

# Ensure UTF-8 output encoding for console
sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from tts_service import app, VOICE_MAPPING

client = TestClient(app)

class TestTTSService(unittest.TestCase):

    def test_01_health_check(self):
        """Verify that GET /health continues to return ok status."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("service"), "tts")
        print("PASS: test_01_health_check")

    def test_02_unsupported_language_rejection(self):
        """Verify that unsupported languages are strictly rejected with 400 and not substituted."""
        for unsupported_lang in ["en", "te", "bn", "gu", "klingon"]:
            response = client.post(
                "/api/tts/stream",
                json={"text": "Test rejection", "language": unsupported_lang}
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("Silent substitution is prohibited", response.json()["detail"])
        print("PASS: test_02_unsupported_language_rejection (No silent substitution)")

    def test_03_empty_text_rejection(self):
        """Verify that empty or whitespace-only text is rejected with 400."""
        response = client.post(
            "/api/tts/stream",
            json={"text": "   ", "language": "hi"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("cannot be empty", response.json()["detail"])
        print("PASS: test_03_empty_text_rejection")

    def test_04_hindi_streaming(self):
        """Verify in-memory audio streaming for Hindi (hi-IN-SwaraNeural)."""
        text = "नमस्ते, हकदार में आपका स्वागत है। मैं आपकी क्या सहायता कर सकता हूँ?"
        response = client.post(
            "/api/tts/stream",
            json={"text": text, "language": "hi"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "audio/mpeg")
        self.assertEqual(response.headers["x-voice-used"], "hi-IN-SwaraNeural")
        self.assertEqual(response.headers["x-language"], "hi")

        audio_bytes = response.content
        self.assertGreater(len(audio_bytes), 5000, f"Expected >5000 bytes, got {len(audio_bytes)}")
        # Check standard MP3 magic bytes: ID3 header or sync frame 0xFF 0xFB/0xF3/0xF2
        is_mp3 = audio_bytes.startswith(b"ID3") or (audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0)
        self.assertTrue(is_mp3, "Response audio bytes do not start with valid MP3 frame header")
        print(f"PASS: test_04_hindi_streaming ({len(audio_bytes)} bytes received)")

    def test_05_marathi_streaming(self):
        """Verify in-memory audio streaming for Marathi (mr-IN-AarohiNeural)."""
        text = "नमस्कार, हकदार मध्ये आपले स्वागत आहे. मी तुम्हाला कशी मदत करू शकतो?"
        response = client.post(
            "/api/tts/stream",
            json={"text": text, "language": "mr"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "audio/mpeg")
        self.assertEqual(response.headers["x-voice-used"], "mr-IN-AarohiNeural")
        self.assertEqual(response.headers["x-language"], "mr")

        audio_bytes = response.content
        self.assertGreater(len(audio_bytes), 5000, f"Expected >5000 bytes, got {len(audio_bytes)}")
        is_mp3 = audio_bytes.startswith(b"ID3") or (audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0)
        self.assertTrue(is_mp3, "Response audio bytes do not start with valid MP3 frame header")
        print(f"PASS: test_05_marathi_streaming ({len(audio_bytes)} bytes received)")

    def test_06_tamil_streaming(self):
        """Verify in-memory audio streaming for Tamil (ta-IN-PallaviNeural)."""
        text = "வணக்கம், हकदार-க்கு உங்களை வரவேற்கிறோம். நான் உங்களுக்கு எவ்வாறு உதவ முடியும்?"
        response = client.post(
            "/api/tts/stream",
            json={"text": text, "language": "ta"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "audio/mpeg")
        self.assertEqual(response.headers["x-voice-used"], "ta-IN-PallaviNeural")
        self.assertEqual(response.headers["x-language"], "ta")

        audio_bytes = response.content
        self.assertGreater(len(audio_bytes), 5000, f"Expected >5000 bytes, got {len(audio_bytes)}")
        is_mp3 = audio_bytes.startswith(b"ID3") or (audio_bytes[0] == 0xFF and (audio_bytes[1] & 0xE0) == 0xE0)
        self.assertTrue(is_mp3, "Response audio bytes do not start with valid MP3 frame header")
        print(f"PASS: test_06_tamil_streaming ({len(audio_bytes)} bytes received)")

    def test_07_legacy_api_tts_regression(self):
        """Verify that legacy POST /api/tts endpoint continues to function without regression."""
        response = client.post(
            "/api/tts",
            json={"text": "परीक्षण संदेश", "language": "hi"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "audio/mpeg")
        self.assertGreater(len(response.content), 2000)
        print(f"PASS: test_07_legacy_api_tts_regression ({len(response.content)} bytes received)")

if __name__ == "__main__":
    unittest.main()
