import re


def mutate_dosage(text: str) -> tuple[str, dict]:
    """
    Deliberately changes a medication dosage in clinical text.

    This is used for controlled integrity testing only.
    """

    dosage_pattern = r"\b500\s*mg\b"

    match = re.search(dosage_pattern, text, flags=re.IGNORECASE)

    if not match:
        return text, {
            "mutation_type": "Dosage drift",
            "applied": False,
            "original_value": None,
            "mutated_value": None,
        }

    mutated_text = re.sub(
        dosage_pattern,
        "1000 mg",
        text,
        count=1,
        flags=re.IGNORECASE,
    )

    return mutated_text, {
        "mutation_type": "Dosage drift",
        "applied": True,
        "original_value": match.group(0),
        "mutated_value": "1000 mg",
    }
def mutate_allergy(text: str) -> tuple[str, dict]:
    """
    Deliberately changes a documented allergy into
    a statement saying there are no known drug allergies.
    """

    allergy_pattern = r"\bPatient is allergic to ([A-Za-z-]+)\."

    match = re.search(allergy_pattern, text, flags=re.IGNORECASE)

    if not match:
        return text, {
            "mutation_type": "Allergy contradiction",
            "applied": False,
            "original_value": None,
            "mutated_value": None,
        }

    allergy = match.group(1)

    mutated_text = re.sub(
        allergy_pattern,
        "No known drug allergies.",
        text,
        count=1,
        flags=re.IGNORECASE,
    )

    return mutated_text, {
        "mutation_type": "Allergy contradiction",
        "applied": True,
        "original_value": allergy,
        "mutated_value": "No known drug allergies",
    }
def mutate_duration(text: str) -> tuple[str, dict]:
    """
    Deliberately changes a symptom duration
    from days to weeks for integrity testing.
    """

    duration_pattern = r"\b(\d+)\s+days\b"

    match = re.search(duration_pattern, text, flags=re.IGNORECASE)

    if not match:
        return text, {
            "mutation_type": "Duration drift",
            "applied": False,
            "original_value": None,
            "mutated_value": None,
        }

    number = match.group(1)

    mutated_text = re.sub(
        duration_pattern,
        f"{number} weeks",
        text,
        count=1,
        flags=re.IGNORECASE,
    )

    return mutated_text, {
        "mutation_type": "Duration drift",
        "applied": True,
        "original_value": f"{number} days",
        "mutated_value": f"{number} weeks",
    }
def apply_all_mutations(text: str) -> tuple[str, list[dict]]:
    """
    Apply all available controlled clinical mutations
    to a source record for integrity testing.
    """

    mutated_text = text
    results = []

    mutation_functions = [
        mutate_dosage,
        mutate_allergy,
        mutate_duration,
    ]

    for mutation_function in mutation_functions:
        mutated_text, result = mutation_function(mutated_text)
        results.append(result)

    return mutated_text, results
