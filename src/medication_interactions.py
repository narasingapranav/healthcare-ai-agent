from itertools import combinations

# Simple educational interaction map for demo purposes.
# This is not a clinical decision system.
KNOWN_INTERACTIONS: dict[frozenset[str], str] = {
    frozenset({"ibuprofen", "warfarin"}): "Higher bleeding risk when used together. Consult a doctor.",
    frozenset({"aspirin", "warfarin"}): "Higher bleeding risk when used together. Consult a doctor.",
    frozenset({"metformin", "alcohol"}): "May raise risk of lactic acidosis. Avoid heavy alcohol use.",
    frozenset({"lisinopril", "potassium"}): "May increase potassium levels. Monitor with clinician guidance.",
}


def check_interactions(medication_names: list[str]) -> list[str]:
    normalized = [name.strip().lower() for name in medication_names if name and name.strip()]
    findings: list[str] = []

    for a, b in combinations(sorted(set(normalized)), 2):
        key = frozenset({a, b})
        warning = KNOWN_INTERACTIONS.get(key)
        if warning:
            findings.append(f"{a.title()} + {b.title()}: {warning}")

    return findings
