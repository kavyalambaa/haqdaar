from typing import Dict, Any, List

class SchemeEligibilityAdapter:
    """
    Deterministic rule engine evaluating citizen eligibility against official scheme criteria.
    Supports ternary outcomes:
    - POTENTIALLY_ELIGIBLE
    - POTENTIALLY_INELIGIBLE
    - NEEDS_VERIFICATION
    Strictly follows rule: Never treat unknown as false.
    """

    @staticmethod
    def evaluate_pm_kisan(profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates PM-KISAN rules based on 2020 Revised Operational Guidelines.
        """
        land = profile.get("land")
        occupation = profile.get("occupation")
        is_taxpayer = profile.get("is_taxpayer")
        is_govt_emp = profile.get("is_govt_employee")

        # 1. Exclusion checks
        if is_taxpayer is True:
            return {
                "outcome": "POTENTIALLY_INELIGIBLE",
                "scheme": "PM-KISAN",
                "reason": "Exclusion Rule: Individuals who paid income tax in the last assessment year are ineligible under clause 3.2.",
                "action": "If your income tax status has changed, please present current income proof."
            }

        if is_govt_emp is True and profile.get("is_class_iv") is not True:
            return {
                "outcome": "POTENTIALLY_INELIGIBLE",
                "scheme": "PM-KISAN",
                "reason": "Exclusion Rule: Serving or retired government employees (excluding Group D / Class IV / MTS) are ineligible.",
                "action": "Group D / MTS staff are exempt. Please verify your employment grade."
            }

        # 2. Landholding checks
        if land is not None and isinstance(land, dict):
            val = land.get("value")
            if val is not None and val == 0:
                return {
                    "outcome": "POTENTIALLY_INELIGIBLE",
                    "scheme": "PM-KISAN",
                    "reason": "PM-KISAN requires the farmer family to own cultivable agricultural land registered in land records.",
                    "action": "Agricultural laborers without land title may qualify for MGNREGA or e-Shram benefits."
                }
            elif val is not None and val > 0:
                return {
                    "outcome": "POTENTIALLY_ELIGIBLE",
                    "scheme": "PM-KISAN",
                    "reason": f"Your family owns {val} {land.get('unit', 'units')} of cultivable land and no disqualifying exclusions were reported.",
                    "benefit": "₹6,000 per year in three 4-monthly instalments of ₹2,000.",
                    "documents_needed": ["Aadhaar-seeded bank account", "Jamabandi / Khatoni land records copy"],
                    "action": "Indicative only. Official verification is performed by the local Patwari/Tehsildar via pmkisan.gov.in."
                }

        # 3. Unknown / Ambiguous case
        return {
            "outcome": "NEEDS_VERIFICATION",
            "scheme": "PM-KISAN",
            "reason": "Land ownership status is unconfirmed or whose name appears on the revenue record is unknown.",
            "action": "Please verify if cultivable land is registered in your name or your spouse's name in revenue records."
        }

    @staticmethod
    def evaluate_diggi_scheme(profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates Rajasthan Diggi Construction Subsidy criteria.
        """
        land = profile.get("land")
        state = (profile.get("state") or "").lower()

        if state and "rajasthan" not in state and "राजस्थान" not in state:
            return {
                "outcome": "POTENTIALLY_INELIGIBLE",
                "scheme": "Diggi Subsidy Scheme",
                "reason": "This is a State-specific scheme for canal-command agricultural areas of Rajasthan.",
                "action": "Please check irrigation schemes applicable to your state."
            }

        if land and isinstance(land, dict):
            val = land.get("value")
            unit = (land.get("unit") or "").lower()
            # 0.5 hectare is approx 2 bigha (depending on pacca/kachha)
            if val == 0:
                return {
                    "outcome": "POTENTIALLY_INELIGIBLE",
                    "scheme": "Diggi Subsidy Scheme",
                    "reason": "Minimum 0.5 hectare irrigated agricultural land is required for diggi subsidy.",
                    "action": "Landless farmers cannot apply for irrigation storage subsidies."
                }
            elif val > 0:
                return {
                    "outcome": "POTENTIALLY_ELIGIBLE",
                    "scheme": "डिग्गी निर्माण अनुदान (Rajasthan)",
                    "benefit": "Small/Marginal: 85% up to ₹3,40,000; Others: 75% up to ₹3,00,000 (Indicative Portal Snapshot — Subject to Current Financial Year Verification. Not a guaranteed current benefit).",
                    "conditions": [
                        "Minimum storage capacity of 4,00,000 litres.",
                        "Administrative approval from Agriculture Department required BEFORE starting construction.",
                        "Compulsory installation of drip or sprinkler irrigation set."
                    ],
                    "action": "Apply through RajKisan Sathi portal or nearest e-Mitra with Jamabandi copy."
                }

        return {
            "outcome": "NEEDS_VERIFICATION",
            "scheme": "Diggi Subsidy Scheme",
            "reason": "Requires confirmation of land area (minimum 0.5 hectare) and canal water supply availability.",
            "action": "Check your Jamabandi not older than 6 months."
        }

