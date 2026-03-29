import json
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import (
    AYURVEDA_API_KEY,
    AYURVEDA_API_URL,
    ONE_MG_API_KEY,
    ONE_MG_API_URL,
    PRACTO_API_KEY,
    PRACTO_API_URL,
)


class IndianHealthService:
    def __init__(self) -> None:
        self.one_mg_api_url = ONE_MG_API_URL.strip()
        self.one_mg_api_key = ONE_MG_API_KEY.strip()
        self.practo_api_url = PRACTO_API_URL.strip()
        self.practo_api_key = PRACTO_API_KEY.strip()
        self.ayurveda_api_url = AYURVEDA_API_URL.strip()
        self.ayurveda_api_key = AYURVEDA_API_KEY.strip()

    def search_1mg_medicines(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        query_text = query.strip()
        if not query_text:
            return []

        if self.one_mg_api_url:
            payload = self._safe_get_json(
                self.one_mg_api_url,
                params={"q": query_text, "limit": limit},
                api_key=self.one_mg_api_key,
            )
            normalized = self._normalize_medicine_payload(payload)
            if normalized:
                return normalized[:limit]

        return self._sample_1mg_results(query_text, limit)

    def search_practo_doctors(self, city: str, specialty: str, limit: int = 10) -> list[dict[str, Any]]:
        city_text = city.strip()
        specialty_text = specialty.strip()
        if not city_text or not specialty_text:
            return []

        if self.practo_api_url:
            payload = self._safe_get_json(
                self.practo_api_url,
                params={"city": city_text, "specialty": specialty_text, "limit": limit},
                api_key=self.practo_api_key,
            )
            normalized = self._normalize_doctor_payload(payload)
            if normalized:
                return normalized[:limit]

        return self._sample_practo_results(city_text, specialty_text, limit)

    def get_ayurvedic_info(self, remedy_name: str) -> dict[str, Any]:
        remedy = remedy_name.strip().lower()
        if not remedy:
            return {}

        if self.ayurveda_api_url:
            payload = self._safe_get_json(
                self.ayurveda_api_url,
                params={"q": remedy_name.strip()},
                api_key=self.ayurveda_api_key,
            )
            parsed = self._normalize_ayurveda_payload(payload)
            if parsed:
                return parsed

        return self._local_ayurveda_knowledge(remedy)

    def _safe_get_json(self, url: str, params: dict[str, Any], api_key: str = "") -> Any:
        try:
            query_string = urlencode({key: value for key, value in params.items() if value is not None})
            full_url = f"{url}?{query_string}" if query_string else url
            headers = {"Accept": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
                headers["x-api-key"] = api_key

            request = Request(full_url, headers=headers, method="GET")
            with urlopen(request, timeout=10) as response:
                body = response.read().decode("utf-8")
            return json.loads(body)
        except Exception:
            return None

    def _normalize_medicine_payload(self, payload: Any) -> list[dict[str, Any]]:
        if payload is None:
            return []

        items: list[dict[str, Any]] = []
        if isinstance(payload, list):
            items = [item for item in payload if isinstance(item, dict)]
        elif isinstance(payload, dict):
            for key in ("results", "items", "data", "medicines"):
                value = payload.get(key)
                if isinstance(value, list):
                    items = [item for item in value if isinstance(item, dict)]
                    break

        normalized: list[dict[str, Any]] = []
        for item in items:
            normalized.append(
                {
                    "name": str(item.get("name") or item.get("title") or "Unknown"),
                    "manufacturer": str(item.get("manufacturer") or item.get("brand") or ""),
                    "price_inr": self._to_float(item.get("price") or item.get("mrp") or item.get("price_inr")),
                    "uses": str(item.get("uses") or item.get("description") or item.get("indications") or ""),
                    "url": str(item.get("url") or item.get("link") or ""),
                    "raw": item,
                }
            )

        return normalized

    def _normalize_doctor_payload(self, payload: Any) -> list[dict[str, Any]]:
        if payload is None:
            return []

        items: list[dict[str, Any]] = []
        if isinstance(payload, list):
            items = [item for item in payload if isinstance(item, dict)]
        elif isinstance(payload, dict):
            for key in ("results", "items", "data", "doctors"):
                value = payload.get(key)
                if isinstance(value, list):
                    items = [item for item in value if isinstance(item, dict)]
                    break

        doctors: list[dict[str, Any]] = []
        for item in items:
            doctors.append(
                {
                    "name": str(item.get("name") or item.get("doctor_name") or "Unknown Doctor"),
                    "specialty": str(item.get("specialty") or item.get("category") or "General"),
                    "city": str(item.get("city") or item.get("location") or ""),
                    "experience_years": int(item.get("experience_years") or item.get("experience") or 0),
                    "consultation_fee_inr": self._to_float(item.get("consultation_fee") or item.get("fee")),
                    "clinic": str(item.get("clinic") or item.get("hospital") or ""),
                    "url": str(item.get("url") or item.get("link") or ""),
                }
            )

        return doctors

    def _normalize_ayurveda_payload(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            return {}

        if "name" in payload and "uses" in payload:
            return {
                "name": str(payload.get("name", "")),
                "uses": str(payload.get("uses", "")),
                "common_forms": payload.get("common_forms", []),
                "cautions": payload.get("cautions", []),
                "evidence_note": str(payload.get("evidence_note", "")),
            }

        data = payload.get("data")
        if isinstance(data, dict):
            return {
                "name": str(data.get("name", "")),
                "uses": str(data.get("uses", "")),
                "common_forms": data.get("common_forms", []),
                "cautions": data.get("cautions", []),
                "evidence_note": str(data.get("evidence_note", "")),
            }

        return {}

    def _local_ayurveda_knowledge(self, remedy: str) -> dict[str, Any]:
        knowledge_base: dict[str, dict[str, Any]] = {
            "ashwagandha": {
                "name": "Ashwagandha",
                "uses": "Traditionally used for stress support, sleep quality, and general vitality.",
                "common_forms": ["Churna (powder)", "Capsules", "Tablets"],
                "cautions": [
                    "May cause drowsiness in some people.",
                    "Use caution with thyroid medications.",
                    "Avoid during pregnancy unless advised by a qualified clinician.",
                ],
                "evidence_note": "Clinical evidence is emerging, but quality and dosing vary by formulation.",
            },
            "triphala": {
                "name": "Triphala",
                "uses": "Traditionally used to support digestion and bowel regularity.",
                "common_forms": ["Powder", "Tablets", "Decoction"],
                "cautions": [
                    "May cause loose stools at higher doses.",
                    "Separate from other oral medicines by a few hours.",
                ],
                "evidence_note": "Small studies suggest digestive benefits; more robust trials are needed.",
            },
            "tulsi": {
                "name": "Tulsi (Holy Basil)",
                "uses": "Traditionally used for respiratory comfort and immune support.",
                "common_forms": ["Tea", "Extract", "Capsules"],
                "cautions": [
                    "May lower blood sugar in some individuals.",
                    "Discuss use if taking anti-diabetic medication.",
                ],
                "evidence_note": "Evidence is preliminary for stress and metabolic support.",
            },
            "giloy": {
                "name": "Giloy (Guduchi)",
                "uses": "Traditionally used for fever support and immune health.",
                "common_forms": ["Juice", "Tablets", "Stem extract"],
                "cautions": [
                    "Use caution in autoimmune conditions.",
                    "Potential liver injury has been reported in rare cases.",
                ],
                "evidence_note": "Traditional use is common; modern evidence and quality control remain variable.",
            },
        }

        if remedy in knowledge_base:
            return knowledge_base[remedy]

        for key, value in knowledge_base.items():
            if remedy in key or key in remedy:
                return value

        return {
            "name": remedy.title(),
            "uses": "No local ayurvedic profile found for this remedy.",
            "common_forms": [],
            "cautions": ["Consult a qualified Ayurvedic practitioner before use."],
            "evidence_note": "Information unavailable in local dataset.",
        }

    def _sample_1mg_results(self, query: str, limit: int) -> list[dict[str, Any]]:
        sample_rows = [
            {
                "name": f"{query.title()} 500",
                "manufacturer": "Sample Pharma India",
                "price_inr": 95.0,
                "uses": "Temporary sample entry for fever/pain profile.",
                "url": "",
                "raw": {"sample": True, "source": "1mg"},
            },
            {
                "name": f"{query.title()} Plus",
                "manufacturer": "HealthKart Labs",
                "price_inr": 132.0,
                "uses": "Temporary sample entry for demonstration of Indian catalog.",
                "url": "",
                "raw": {"sample": True, "source": "1mg"},
            },
        ]
        return sample_rows[: max(1, limit)]

    def _sample_practo_results(self, city: str, specialty: str, limit: int) -> list[dict[str, Any]]:
        doctors = [
            {
                "name": "Dr. Ananya Sharma",
                "specialty": specialty.title(),
                "city": city.title(),
                "experience_years": 12,
                "consultation_fee_inr": 700.0,
                "clinic": "CityCare Clinic",
                "url": "",
            },
            {
                "name": "Dr. Rohan Iyer",
                "specialty": specialty.title(),
                "city": city.title(),
                "experience_years": 8,
                "consultation_fee_inr": 500.0,
                "clinic": "Wellness Point",
                "url": "",
            },
        ]
        return doctors[: max(1, limit)]

    def _to_float(self, value: Any) -> float | None:
        try:
            if value is None or value == "":
                return None
            return float(value)
        except (TypeError, ValueError):
            return None
