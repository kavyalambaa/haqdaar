import os
import sys
import unittest

# Ensure UTF-8 output encoding for console
sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from stt_service import app

client = TestClient(app)

# Workspace root directory contains actual test audio files
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestSTTService(unittest.TestCase):

    def test_01_health_check(self):
        """Verify that GET /health returns ok status and model configuration."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertEqual(data.get("service"), "stt")
        self.assertTrue(data.get("has_credentials"))
        print("PASS: test_01_health_check")

    def test_02_unsupported_language_rejection(self):
        """Verify that unsupported languages are strictly rejected with 400 without silent substitution."""
        dummy_audio = b"\xff\xfb\x90\x64\x00\x00\x00\x00"  # Small valid MP3 frame
        for bad_lang in ["en", "te", "bn", "gu", "klingon"]:
            response = client.post(
                "/api/stt",
                data={"language": bad_lang},
                files={"file": ("test.mp3", dummy_audio, "audio/mp3")}
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("Silent substitution is prohibited", response.json()["detail"])
        print("PASS: test_02_unsupported_language_rejection (No silent substitution)")

    def test_03_empty_audio_rejection(self):
        """Verify that empty (0 bytes) audio files are rejected with 400."""
        response = client.post(
            "/api/stt",
            data={"language": "hi"},
            files={"file": ("empty.mp3", b"", "audio/mp3")}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("is empty", response.json()["detail"])
        print("PASS: test_03_empty_audio_rejection")

    def test_04_invalid_mime_type_rejection(self):
        """Verify that unsupported media types are rejected with 415."""
        dummy_content = b"Not an audio file, just text"
        for bad_mime in ["text/plain", "application/json", "image/png"]:
            response = client.post(
                "/api/stt",
                data={"language": "hi"},
                files={"file": ("document.txt", dummy_content, bad_mime)}
            )
            self.assertEqual(response.status_code, 415)
            self.assertIn("Unsupported audio type", response.json()["detail"])
        print("PASS: test_04_invalid_mime_type_rejection")

    def test_05_oversized_audio_rejection(self):
        """Verify that audio payloads exceeding the 10MB limit are rejected with 413."""
        oversized_data = b"0" * (10 * 1024 * 1024 + 1024)  # 10MB + 1KB
        response = client.post(
            "/api/stt",
            data={"language": "hi"},
            files={"file": ("oversized.mp3", oversized_data, "audio/mp3")}
        )
        self.assertEqual(response.status_code, 413)
        self.assertIn("exceeds 10MB limit", response.json()["detail"])
        print("PASS: test_05_oversized_audio_rejection")

    def test_06_hindi_audio_transcription(self):
        """Live integration test: Transcribe actual Hindi audio sample (hindi_test.mp3)."""
        audio_path = os.path.join(WORKSPACE_ROOT, "hindi_test.mp3")
        self.assertTrue(os.path.exists(audio_path), f"Audio file not found: {audio_path}")

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        response = client.post(
            "/api/stt",
            data={"language": "hi"},
            files={"file": ("hindi_test.mp3", audio_bytes, "audio/mp3")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("language"), "hi")
        self.assertEqual(data.get("language_name"), "Hindi")
        self.assertTrue(len(data.get("transcript", "")) > 0)
        print(f"PASS: test_06_hindi_audio_transcription -> Transcript: '{data.get('transcript')}'")

    def test_07_marathi_audio_transcription(self):
        """Live integration test: Transcribe actual Marathi audio sample (marathi_test.mp3)."""
        audio_path = os.path.join(WORKSPACE_ROOT, "marathi_test.mp3")
        self.assertTrue(os.path.exists(audio_path), f"Audio file not found: {audio_path}")

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        response = client.post(
            "/api/stt",
            data={"language": "mr"},
            files={"file": ("marathi_test.mp3", audio_bytes, "audio/mp3")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("language"), "mr")
        self.assertEqual(data.get("language_name"), "Marathi")
        self.assertTrue(len(data.get("transcript", "")) > 0)
        print(f"PASS: test_07_marathi_audio_transcription -> Transcript: '{data.get('transcript')}'")

    def test_08_tamil_audio_transcription(self):
        """Live integration test: Transcribe actual Tamil audio sample (tamil_test.mp3)."""
        audio_path = os.path.join(WORKSPACE_ROOT, "tamil_test.mp3")
        self.assertTrue(os.path.exists(audio_path), f"Audio file not found: {audio_path}")

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        response = client.post(
            "/api/stt",
            data={"language": "ta"},
            files={"file": ("tamil_test.mp3", audio_bytes, "audio/mp3")}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("language"), "ta")
        self.assertEqual(data.get("language_name"), "Tamil")
        self.assertTrue(len(data.get("transcript", "")) > 0)
        print(f"PASS: test_08_tamil_audio_transcription -> Transcript: '{data.get('transcript')}'")

if __name__ == "__main__":
    unittest.main()

