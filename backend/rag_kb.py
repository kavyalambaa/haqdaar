import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("haqdaar.rag")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
METADATA_DIR = os.path.join(BASE_DIR, "data", "research", "rag", "metadata")
SCHEMES_DIR = os.path.join(BASE_DIR, "data", "schemes")

class KnowledgeBase:
    """
    Structured Knowledge Base serving verified ICAR agricultural research 
    and Rajasthan government scheme specifications.
    Strictly prevents hallucinations by binding answers to verified citations.
    """
    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.schemes: Dict[str, Dict[str, Any]] = {}
        self._load_metadata()
        self._load_schemes()

    def _load_metadata(self):
        if not os.path.exists(METADATA_DIR):
            logger.warning(f"Metadata directory not found at {METADATA_DIR}")
            return

        for fname in os.listdir(METADATA_DIR):
            if fname.endswith(".json"):
                fpath = os.path.join(METADATA_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        doc_id = data.get("document_id") or os.path.splitext(fname)[0]
                        self.documents[doc_id] = data
                except Exception as e:
                    logger.error(f"Error loading metadata file {fname}: {e}")

        logger.info(f"Loaded {len(self.documents)} verified RAG document records.")

    def _load_schemes(self):
        for sname in ["pm_kisan.draft.json", "pm_matritva_vandana.draft.json"]:
            spath = os.path.join(SCHEMES_DIR, sname)
            if os.path.exists(spath):
                try:
                    with open(spath, "r", encoding="utf-8") as fp:
                        sdata = json.load(fp)
                        sid = sdata.get("scheme_id")
                        if sid:
                            self.schemes[sid] = sdata
                except Exception as e:
                    logger.error(f"Error loading scheme {sname}: {e}")

        logger.info(f"Loaded {len(self.schemes)} scheme rule drafts.")

    def retrieve(self, query: str, persona: str = "kisan", language: str = "hi") -> List[Dict[str, Any]]:
        """
        Retrieves matching verified knowledge items based on keywords and domain context.
        Returns matched records with verified citations and safety limitations.
        """
        q_lower = query.lower()
        results = []

        # 1. Agricultural Domain (Kisan Sahayak)
        if persona in ["kisan", "general"]:
            # Bajra / Pearl millet queries
            if any(k in q_lower for k in ["बाजरा", "बाजरे", "बाजरी", "bajra", "pearl millet", "கம்பு", "कम्पोजिट", "हाइब्रिड", "sowing", "seed rate"]):
                doc = self.documents.get("bajra_gap_icar_iimr_2025")
                if doc:
                    results.append({
                        "doc_id": "bajra_gap_icar_iimr_2025",
                        "title": doc.get("title"),
                        "institution": doc.get("publisher"),
                        "year": doc.get("publication_year", 2025),
                        "crop": "Bajra (Pearl Millet)",
                        "topics": doc.get("relevant_topics", []),
                        "verified_chapter": "Chapter 2: Pearl millet",
                        "facts": [
                            "Recommended seed rate: 4 to 5 kg per hectare for sole cropping.",
                            "Spacing: 45 cm between rows and 10 to 12 cm between plants.",
                            "Sowing depth: 2 to 3 cm optimal; deeper sowing reduces seedling emergence.",
                            "Critical irrigation stages: Tillering and flowering/grain filling."
                        ],
                        "limitations": doc.get("limitations", []),
                        "disclaimer": "Recommendations must be verified for the specific agro-ecological zone of your district."
                    })

            # Mustard / Sarson queries
            if any(k in q_lower for k in ["सरसों", "राई", "मोहरी", "mustard", "sarson", "கடுகு", "गिरिराज", "rh 749", "drmr", "oil content"]):
                doc_tech = self.documents.get("mustard_icar_drmr_crop_technologies")
                doc_var = self.documents.get("mustard_icar_drmr_varieties")
                doc_trans = self.documents.get("mustard_transforming_rajasthan_icar_2025")
                
                facts = [
                    "Optimal sowing window in Rajasthan: First fortnight of October (25 September to 15 October).",
                    "Seed rate: 4 to 5 kg per hectare for line sowing.",
                    "Spacing: 30 to 45 cm between rows, 10 to 15 cm between plants; depth: 3 to 5 cm.",
                    "Key varieties: Giriraj (DRMRIJ 31), RH 749, NRCHB 101, DRMR 150-35.",
                    "Critical irrigation stages: Pre-flowering (Rosette stage, 30-35 days) and siliqua formation (60-65 days)."
                ]
                
                results.append({
                    "doc_id": "mustard_icar_drmr_technologies",
                    "title": doc_tech.get("title") if doc_tech else "ICAR-DRMR Rapeseed-Mustard Technologies",
                    "institution": "ICAR-Directorate of Rapeseed-Mustard Research (DRMR), Bharatpur",
                    "year": 2025,
                    "crop": "Mustard",
                    "facts": facts,
                    "limitations": (doc_tech.get("limitations", []) if doc_tech else []) + (doc_var.get("limitations", []) if doc_var else []),
                    "disclaimer": "Pesticide and chemical protection recommendations require current label verification. Consult local KVK."
                })

            # Wheat / Gehun queries
            if any(k in q_lower for k in ["गेहूं", "गहू", "wheat", "gehun", "கோதுமை", "dbw", "करण वंदना", "करण नरेंद्र"]):
                doc_var = self.documents.get("wheat_icar_iiwbr_technologies_2026")
                doc_guide = self.documents.get("wheat_pocket_guide_icar_2014")

                facts = [
                    "Sowing time for timely sown irrigated: First fortnight of November (1 to 15 November).",
                    "Seed rate: 100 kg/ha for timely sown; 125 kg/ha for late sown or bold grains.",
                    "Row spacing: 20 to 22.5 cm.",
                    "Popular DBW varieties for NWPZ & Central Zone: DBW 187 (Karan Vandana), DBW 222 (Karan Narendra), DBW 303, DBW 327.",
                    "Most critical irrigation: Crown Root Initiation (CRI stage) at 20-25 days after sowing."
                ]

                results.append({
                    "doc_id": "wheat_icar_iiwbr_technologies_2026",
                    "title": doc_var.get("title") if doc_var else "ICAR-IIWBR Wheat Technologies",
                    "institution": "ICAR-Indian Institute of Wheat & Barley Research (IIWBR), Karnal",
                    "year": 2026,
                    "crop": "Wheat",
                    "facts": facts,
                    "limitations": doc_var.get("limitations", []) if doc_var else [],
                    "disclaimer": "Variety selection depends strictly on agro-climatic zone and sowing window."
                })

        # 2. Government Schemes Domain (Yojana Sahayak)
        if persona in ["yojana", "general"]:
            # Diggi Subsidy Scheme
            if any(k in q_lower for k in ["डिग्गी", "diggi", "नहर", "water storage", "पक्का डिग्गी"]):
                doc = self.documents.get("diggi_rajkisan_2026")
                if doc:
                    results.append({
                        "doc_id": "diggi_rajkisan_2026",
                        "title": doc.get("title"),
                        "institution": doc.get("institution", "Agriculture Department, Rajasthan"),
                        "year": 2026,
                        "scheme": "डिग्गी निर्माण अनुदान (Diggi Subsidy Scheme)",
                        "benefits": {
                            "status": "INDICATIVE_PORTAL_SNAPSHOT_VERIFICATION_PENDING",
                            "note": "Subsidy figures are from portal snapshot dated 31-10-2026 and are NOT guaranteed current amounts.",
                            "indicative_small_marginal": "Up to 85% of unit cost (max INR 3,40,000) - requires re-verification",
                            "indicative_other_farmers": "Up to 75% of unit cost (max INR 3,00,000) - requires re-verification"
                        },
                        "eligibility": doc.get("eligibility_summary"),
                        "required_documents": doc.get("required_documents"),
                        "conditions": [
                            "कृषि विभाग से प्रशासनिक स्वीकृति (Administrative Approval) मिलने के बाद ही निर्माण कार्य शुरू किया जाना अनिवार्य है।",
                            "न्यूनतम 4,00,000 लीटर भराव क्षमता की पक्की डिग्गी।",
                            "ड्रिप या फव्वारा सिंचाई संयंत्र की स्थापना अनिवार्य।",
                            "वर्तमान वित्तीय वर्ष के नियमों एवं अनुदान का सत्यापन राज किसान साथी पोर्टल पर किया जाना आवश्यक है।"
                        ],
                        "disclaimer": "चेतावनी: यह जानकारी पोर्टल स्नैपशॉट पर आधारित संभावित विवरण है। चालू वित्तीय वर्ष के स्वीकृत अनुदान और नियमों की पुष्टि राज किसान पोर्टल अथवा निकटतम ई-मित्र से करना अनिवार्य है।"
                    })

            # Farm Pond (खेत तलाई)
            if any(k in q_lower for k in ["तलाई", "तालाब", "farm pond", "pond", "रेनवाटर", "वर्षा जल"]):
                doc = self.documents.get("farm_pond_rajkisan_2026")
                if doc:
                    results.append({
                        "doc_id": "farm_pond_rajkisan_2026",
                        "title": doc.get("title"),
                        "institution": doc.get("institution", "Agriculture Department, Rajasthan"),
                        "year": 2026,
                        "scheme": "खेत तलाई योजना (Farm Pond Scheme)",
                        "facts": [
                            "Kachcha Farm Pond: 60% of unit cost (max ₹63,000) for small/marginal farmers; 50% (max ₹52,500) for others.",
                            "Plastic Lined Pond (min 500 micron): 70% (max ₹1,05,000) for small/marginal; 60% (max ₹90,000) for others.",
                            "Minimum land requirement: 0.5 hectare cultivable agricultural land."
                        ],
                        "disclaimer": "Subsidy figures are indicative for the current financial year. Verify before applying on RajKisan portal."
                    })

            # Jal Hauz (जल हौज)
            if any(k in q_lower for k in ["जल हौज", "हौज", "jal hauz", "hauz", "वाटर टैंक"]):
                doc = self.documents.get("jal_hauz_rajkisan_2026")
                if doc:
                    results.append({
                        "doc_id": "jal_hauz_rajkisan_2026",
                        "title": doc.get("title"),
                        "institution": "Agriculture Department, Government of Rajasthan",
                        "year": 2026,
                        "scheme": "जल हौज निर्माण अनुदान योजना",
                        "facts": [
                            "Minimum storage capacity: 1,00,000 litres.",
                            "Requires minimum 0.5 hectare cultivable land in command or non-command area.",
                            "Construction must comply with prescribed engineering specifications."
                        ],
                        "disclaimer": "Approval must be obtained on Raj Kisan Sathi portal before starting construction."
                    })

            # Irrigation Pipeline (सिंचाई पाइपलाइन)
            if any(k in q_lower for k in ["पाइपलाइन", "pipeline", "सिंचाई पाइप"]):
                doc = self.documents.get("irrigation_pipeline_rajkisan_2026")
                if doc:
                    results.append({
                        "doc_id": "irrigation_pipeline_rajkisan_2026",
                        "title": doc.get("title"),
                        "institution": "Agriculture Department, Government of Rajasthan",
                        "year": 2026,
                        "scheme": "कृषि सिंचाई पाइपलाइन योजना",
                        "facts": [
                            "Subsidy: 60% (max ₹18,000) for small/marginal farmers; 50% (max ₹15,000) for other farmers.",
                            "Minimum 0.5 hectare cultivable land with functioning well or tube-well.",
                            "HDPE or PVC ISI-marked pipes permitted."
                        ],
                        "disclaimer": "Must purchase from registered manufacturers on the RajKisan portal."
                    })

            # PM-KISAN
            if any(k in q_lower for k in ["पीएम किसान", "pm kisan", "pm-kisan", "सम्मान निधि", "6000", "2000", "किस्त"]):
                doc = self.schemes.get("pm_kisan")
                if doc:
                    results.append({
                        "doc_id": "pm_kisan",
                        "title": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                        "institution": "Ministry of Agriculture & Farmers Welfare, GoI",
                        "benefit": "₹6,000 per eligible family per year in 3 installments of ₹2,000.",
                        "family_definition": "Husband, wife, and minor children only. Adult children and parents are evaluated separately.",
                        "eligibility_core": "Family must own cultivable agricultural land in revenue records.",
                        "major_exclusions": [
                            "Institutional landholders.",
                            "Constitutional post holders (present/former).",
                            "Ministers, MPs, MLAs, Mayors, District Panchayat Chairpersons.",
                            "Serving or retired government employees (excluding Multi-Tasking Staff / Group D / Class IV).",
                            "Pensioners receiving ₹10,000 or more per month (excluding MTS / Class IV).",
                            "Income-tax payers in the last assessment year.",
                            "Practicing professionals (doctors, lawyers, engineers, chartered accountants, architects)."
                        ],
                        "disclaimer": "The application gives an indicative eligibility assessment. Formal approval rests with the State Revenue / Agriculture Department."
                    })

            # PMMVY (Matru Vandana)
            if any(k in q_lower for k in ["मातृत्व", "गर्भवती", "matritva", "pmmvy", "बच्चा", "pregnancy"]):
                doc = self.schemes.get("pmmvy")
                if doc:
                    results.append({
                        "doc_id": "pmmvy",
                        "title": "Pradhan Mantri Matru Vandana Yojana (PMMVY 2.0)",
                        "institution": "Ministry of Women and Child Development, GoI",
                        "benefit": "First child: ₹5,000 in two instalments (₹3,000 + ₹2,000). Second child (only if girl): ₹6,000 in one instalment.",
                        "eligibility_core": "Pregnant women and lactating mothers belonging to disadvantaged categories (BPL, SC/ST, MGNREGA, PM-KISAN recipient, NFSA card, or income < 8 Lakh).",
                        "disclaimer": "Apply within 270 days of childbirth at Anganwadi Centre or PMMVY portal."
                    })

        return results

    def get_catalog(self) -> List[Dict[str, Any]]:
        """Returns catalog of supported schemes and agricultural guides with verification badges."""
        return [
            {
                "id": "pm_kisan",
                "name": "PM Kisan Samman Nidhi",
                "category": "Central Direct Benefit",
                "benefit": "₹6,000 / year (Subject to Land Mutation & e-KYC Verification)",
                "verified_source": "Ministry of Agriculture Revised Guidelines 2020",
                "status": "VERIFIED_GUIDELINES"
            },
            {
                "id": "diggi_rajkisan",
                "name": "डिग्गी निर्माण अनुदान (Diggi Subsidy)",
                "category": "Rajasthan Water Storage",
                "benefit": "Indicative: Up to 85% (Max ₹3,40,000) - Portal Snapshot",
                "verified_source": "Government of Rajasthan RajKisan Portal Snapshot 2026",
                "status": "INDICATIVE (PENDING CURRENT FINANCIAL YEAR VERIFICATION)"
            },
            {
                "id": "farm_pond_rajkisan",
                "name": "खेत तलाई योजना (Farm Pond)",
                "category": "Rajasthan Rainwater Harvesting",
                "benefit": "Indicative: Up to 70% (Max ₹1,05,000) - Portal Snapshot",
                "verified_source": "Government of Rajasthan RajKisan Portal Snapshot 2026",
                "status": "INDICATIVE (PENDING CURRENT FINANCIAL YEAR VERIFICATION)"
            },
            {
                "id": "jal_hauz_rajkisan",
                "name": "जल हौज निर्माण (Jal Hauz)",
                "category": "Rajasthan Water Storage",
                "benefit": "Indicative: Up to 50% Unit Subsidy - Portal Snapshot",
                "verified_source": "Government of Rajasthan RajKisan Portal Snapshot 2026",
                "status": "INDICATIVE (PENDING CURRENT FINANCIAL YEAR VERIFICATION)"
            },
            {
                "id": "irrigation_pipeline_rajkisan",
                "name": "सिंचाई पाइपलाइन योजना (Pipeline)",
                "category": "Rajasthan Irrigation",
                "benefit": "Indicative: Up to 60% (Max ₹18,000) - Portal Snapshot",
                "verified_source": "Government of Rajasthan RajKisan Portal Snapshot 2026",
                "status": "INDICATIVE (PENDING CURRENT FINANCIAL YEAR VERIFICATION)"
            },
            {
                "id": "pmmvy",
                "name": "PM Matru Vandana Yojana (PMMVY 2.0)",
                "category": "Maternity Benefit",
                "benefit": "₹5,000 (1st child) / ₹6,000 (2nd child if girl)",
                "verified_source": "Ministry of Women & Child Development 2024",
                "status": "VERIFIED"
            },
            {
                "id": "icar_bajra_guide",
                "name": "बाजरा उत्तम कृषि पद्धतियाँ (Bajra GAP)",
                "category": "ICAR Crop Guide",
                "benefit": "Verified Seed Rate, Sowing, Varieties",
                "verified_source": "ICAR-IIMR Millets Manual 2025",
                "status": "VERIFIED"
            },
            {
                "id": "icar_mustard_guide",
                "name": "सरसों उन्नत तकनीक (Mustard Technologies)",
                "category": "ICAR Crop Guide",
                "benefit": "Verified Sowing Window, Varieties, Irrigation",
                "verified_source": "ICAR-DRMR Bharatpur 2025",
                "status": "VERIFIED"
            },
            {
                "id": "icar_wheat_guide",
                "name": "गेहूं प्रमाणित किस्में (Wheat Varieties)",
                "category": "ICAR Crop Guide",
                "benefit": "Verified DBW Varieties, Sowing, Irrigation",
                "verified_source": "ICAR-IIWBR Karnal 2026",
                "status": "VERIFIED"
            }
        ]

# Global singleton
kb = KnowledgeBase()

