import os
import sys
import unittest

# Ensure UTF-8 output encoding for console
sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from conversation_service import engine

class TestPersonaRouting(unittest.TestCase):
    """
    Focused tests for smart persona routing in backend/conversation_service.py:
    1. Jal Hauz question with persona="kisan" routes to yojana.
    2. Crop question with persona="yojana" routes to kisan.
    3. Ambiguous question preserves the selected persona.
    4. Existing behavior remains intact for valid explicit personas.
    """

    def test_01_jal_hauz_scheme_with_kisan_persona(self):
        """Clear Jal Hauz scheme query must route to 'yojana' even when frontend selected 'kisan'."""
        queries = [
            "जल हौज निर्माण अनुदान योजना की जानकारी दें",
            "जल हौज़ सब्सिडी के लिए क्या पात्रता है?",
            "What is the subsidy for jal hauz under the government scheme?",
            "राजस्थान में जल हौज निर्माण के लिए आवेदन प्रक्रिया क्या है?"
        ]
        for q in queries:
            with self.subTest(query=q):
                resolved = engine._detect_persona(query=q, user_persona="kisan")
                self.assertEqual(resolved, "yojana", f"Failed for query '{q}': expected 'yojana', got '{resolved}'")
        print("PASS: test_01_jal_hauz_scheme_with_kisan_persona")

    def test_02_crop_query_with_yojana_persona(self):
        """Clear crop/agriculture query must route to 'kisan' even when frontend selected 'yojana'."""
        queries = [
            "सरसों की बुवाई का समय और बीज दर क्या है?",
            "बाजरे की उन्नत किस्में कौन सी हैं?",
            "मोहरी पिकाच्या सुधारित जाती कोणत्या आहेत?",
            "கோதுமை பயிரிட சிறந்த ரகங்கள் எவை?",
            "गेहूं की फसल में कौन सा खाद डालें?"
        ]
        for q in queries:
            with self.subTest(query=q):
                resolved = engine._detect_persona(query=q, user_persona="yojana")
                self.assertEqual(resolved, "kisan", f"Failed for query '{q}': expected 'kisan', got '{resolved}'")
        print("PASS: test_02_crop_query_with_yojana_persona")

    def test_03_ambiguous_query_preserves_selected_persona(self):
        """Ambiguous queries (neither or both intents present) must strictly preserve the user-selected persona."""
        # Ambiguous 1: Greeting / General message (neither intent)
        resolved_kisan = engine._detect_persona(query="नमस्ते, मुझे सहायता चाहिए", user_persona="kisan")
        self.assertEqual(resolved_kisan, "kisan")

        resolved_yojana = engine._detect_persona(query="नमस्ते, मुझे सहायता चाहिए", user_persona="yojana")
        self.assertEqual(resolved_yojana, "yojana")

        # Ambiguous 2: Both intents present (crop + scheme)
        both_query = "फसल के लिए सरकारी अनुदान योजना क्या है?"
        self.assertEqual(engine._detect_persona(query=both_query, user_persona="kisan"), "kisan")
        self.assertEqual(engine._detect_persona(query=both_query, user_persona="yojana"), "yojana")

        print("PASS: test_03_ambiguous_query_preserves_selected_persona")

    def test_04_existing_behavior_intact_for_explicit_personas(self):
        """Explicit scheme query with persona='yojana' remains 'yojana'; explicit crop with 'kisan' remains 'kisan'."""
        self.assertEqual(engine._detect_persona("डिग्गी निर्माण अनुदान", "yojana"), "yojana")
        self.assertEqual(engine._detect_persona("खेत तलाई योजना", "yojana"), "yojana")
        self.assertEqual(engine._detect_persona("बाजरा बुवाई", "kisan"), "kisan")

        # No persona provided fallback
        self.assertEqual(engine._detect_persona("सामान्य सहायता", None), "kisan")
        print("PASS: test_04_existing_behavior_intact_for_explicit_personas")

if __name__ == "__main__":
    unittest.main()

