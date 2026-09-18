import json, re, sys
from pathlib import Path
from scipy.stats import binomtest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.extractor import ClinicalFact, extract_facts, MEDICATION_HINTS, ALLERGY_PATTERNS, NEGATION_PATTERNS
from src.drift_engine import compare_facts

BASE_DOSAGE_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|units?)\b", re.I)
BASE_BP_RE = re.compile(r"\b(?:[89]\d|1\d\d|2[0-4]\d)\s*/\s*(?:[4-9]\d|1\d\d)\b")
BASE_DURATION_RE = re.compile(r"\b\d+\s+(?:hours?|days?|weeks?|months?|years?)\b", re.I)
BASE_FREQ_RE = re.compile(r"\b(?:once|twice|three times|four times)\s+(?:a|per)\s+day\b|\b(?:daily|weekly|nightly|morning|evening)\b", re.I)
BASE_LAT_RE = re.compile(r"\b(?:left|right|bilateral)\b", re.I)


def sentences(text):
    return [c.strip() for c in re.split(r"(?<=[.!?])\s+|\n+", text.strip()) if c.strip()]


def baseline_extract(text):
    facts = []
    for sentence in sentences(text):
        lower = sentence.lower()
        allergy_context = "allerg" in lower
        for med in sorted(MEDICATION_HINTS):
            if re.search(rf"\b{re.escape(med)}\b", lower):
                if allergy_context:
                    continue
                facts.append(ClinicalFact("medication", med, sentence))
        for p in ALLERGY_PATTERNS:
            m = p.search(sentence)
            if m:
                facts.append(ClinicalFact("allergy", m.group(1).strip(" .,:;").lower(), sentence))
        for p in NEGATION_PATTERNS:
            m = p.search(sentence)
            if m:
                facts.append(ClinicalFact("negation", m.group(0).strip().lower(), sentence))
        for m in BASE_DOSAGE_RE.finditer(sentence):
            facts.append(ClinicalFact("dosage", m.group(0).lower().replace(" ", ""), sentence))
        for m in BASE_BP_RE.finditer(sentence):
            facts.append(ClinicalFact("measurement", m.group(0).replace(" ", ""), sentence))
        for m in BASE_DURATION_RE.finditer(sentence):
            facts.append(ClinicalFact("duration", m.group(0).lower(), sentence))
        for m in BASE_FREQ_RE.finditer(sentence):
            facts.append(ClinicalFact("frequency", m.group(0).lower(), sentence))
        for m in BASE_LAT_RE.finditer(sentence):
            facts.append(ClinicalFact("laterality", m.group(0).lower(), sentence))
    out = []
    seen = set()
    for f in facts:
        k = (f.category, f.value, f.evidence)
        if k not in seen:
            seen.add(k)
            out.append(f)
    return out


def add(cases, group, positive, source, transformed, expected):
    cases.append({"id": f"CD-{len(cases)+1:03d}", "group": group, "positive": positive, "source": source, "transformed": transformed, "expected": expected})


def build_cases():
    cases = []
    meds = ["metformin", "amoxicillin", "aspirin", "ibuprofen", "paracetamol", "lisinopril", "amlodipine", "warfarin", "atorvastatin", "omeprazole"]
    dose_pairs = [("500 mg", "1000 mg"), ("250 mg", "500 mg"), ("5 mg", "10 mg"), ("10 mg", "20 mg"), ("20 mg", "40 mg"), ("25 mg", "50 mg"), ("50 mg", "100 mg"), ("75 mg", "150 mg"), ("2 mg", "4 mg"), ("40 mg", "80 mg")]
    for i, (a, b) in enumerate(dose_pairs):
        add(cases, "dosage_drift", True, f"Patient takes {meds[i]} {a} once a day.", f"Patient takes {meds[i]} {b} once a day.", "Dosage drift")

    allergens = ["penicillin", "amoxicillin", "aspirin", "ibuprofen", "paracetamol", "lisinopril", "amlodipine", "warfarin", "atorvastatin", "omeprazole"]
    for x in allergens:
        add(cases, "allergy_contradiction", True, f"Patient is allergic to {x}.", "No known drug allergies.", "Allergy contradiction")

    durs = [("1 day", "2 days"), ("2 days", "5 days"), ("3 days", "3 weeks"), ("4 days", "2 weeks"), ("5 days", "1 month"), ("6 hours", "12 hours"), ("2 weeks", "4 weeks"), ("3 months", "6 months"), ("1 year", "2 years"), ("10 days", "12 days")]
    for a, b in durs:
        add(cases, "duration_drift", True, f"Symptoms have lasted {a}.", f"Symptoms have lasted {b}.", "Duration drift")

    freqs = [("once a day", "twice a day"), ("twice a day", "once a day"), ("three times a day", "once a day"), ("four times a day", "twice a day"), ("daily", "weekly"), ("weekly", "daily"), ("nightly", "daily"), ("morning", "evening"), ("once per day", "twice per day"), ("three times per day", "four times per day")]
    for a, b in freqs:
        add(cases, "frequency_drift", True, f"Patient takes metformin 500 mg {a}.", f"Patient takes metformin 500 mg {b}.", "Frequency drift")

    bps = [("120/80", "180/110"), ("122/78", "160/100"), ("118/76", "150/95"), ("130/85", "190/120"), ("110/70", "170/105"), ("125/82", "140/90"), ("135/88", "200/115"), ("128/84", "155/99"), ("115/75", "145/92"), ("132/86", "175/108")]
    for a, b in bps:
        add(cases, "measurement_drift", True, f"Blood pressure is {a}.", f"Blood pressure is {b}.", "Measurement drift")

    lat = [("left", "right"), ("right", "left"), ("left", "bilateral"), ("right", "bilateral"), ("bilateral", "left"), ("bilateral", "right"), ("left", "right"), ("right", "left"), ("left", "bilateral"), ("right", "bilateral")]
    for i, (a, b) in enumerate(lat):
        add(cases, "laterality_drift", True, f"Patient reports {a} knee pain for {i%5+1} days.", f"Patient reports {b} knee pain for {i%5+1} days.", "Laterality drift")

    for i, m in enumerate(meds):
        add(cases, "omission", True, f"Patient takes {m}. Patient reports nausea.", "Patient reports nausea.", "Omission")
    for i, m in enumerate(meds):
        add(cases, "supported_addition", True, "Patient reports nausea.", f"Patient reports nausea. Patient takes {m}.", "Unsupported addition")

    diagnoses = ["chronic kidney disease", "pneumonia", "heart failure", "diabetes mellitus", "asthma", "sepsis", "migraine", "anemia", "depression", "osteoarthritis"]
    for d in diagnoses:
        add(cases, "unsupported_diagnosis", True, "Patient reports headache.", f"Patient reports headache. Patient has {d}.", "challenge: unsupported diagnosis")

    contradictions = [
        ("Patient is afebrile.", "Patient is febrile."),
        ("The cough is productive.", "The cough is nonproductive."),
        ("The patient is alert.", "The patient is confused."),
        ("Symptoms are improving.", "Symptoms are worsening."),
        ("The wound is dry.", "The wound is draining."),
        ("The patient can walk independently.", "The patient cannot walk independently."),
        ("Appetite is normal.", "Appetite is poor."),
        ("The pain is mild.", "The pain is severe."),
        ("The patient is stable.", "The patient is unstable."),
        ("The rash is resolving.", "The rash is spreading."),
    ]
    for a, b in contradictions:
        add(cases, "semantic_contradiction", True, a, b, "challenge: semantic contradiction")

    unchanged = [
        "Patient takes metformin 500 mg twice a day.",
        "Blood pressure is 122/78.",
        "Headache for 3 days.",
        "Patient reports left knee pain.",
        "Patient is allergic to penicillin.",
        "Patient takes aspirin 75 mg once a day.",
        "Symptoms have lasted 2 weeks.",
        "Patient takes atorvastatin 20 mg nightly.",
        "Blood pressure is 130/85.",
        "Patient reports bilateral ankle pain.",
    ]
    for t in unchanged:
        add(cases, "unchanged_control", False, t, t, "no finding")

    formatting = [
        ("Patient takes metformin 500 mg once a day.", "Patient takes metformin 500mg once a day."),
        ("Blood pressure is 122 / 78.", "Blood pressure is 122/78."),
        ("Patient takes aspirin 75 mg twice a day.", "Patient takes aspirin 75mg twice a day."),
        ("Blood pressure is 130/85.", "Blood pressure is 130 / 85."),
        ("Patient takes lisinopril 10 mg daily.", "Patient takes lisinopril 10mg daily."),
        ("Patient takes amlodipine 5 mg weekly.", "Patient takes amlodipine 5mg weekly."),
        ("Blood pressure is 118 / 76.", "Blood pressure is 118/76."),
        ("Patient takes warfarin 2 mg nightly.", "Patient takes warfarin 2mg nightly."),
        ("Patient takes ibuprofen 200 mg once per day.", "Patient takes ibuprofen 200mg once per day."),
        ("Blood pressure is 140/90.", "Blood pressure is 140 / 90."),
    ]
    for a, b in formatting:
        add(cases, "formatting_control", False, a, b, "no finding")

    words = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    for i, w in enumerate(words, 1):
        add(cases, "duration_paraphrase_control", False, f"Headache for {i} {'day' if i==1 else 'days'}.", f"Headache for {w} {'day' if i==1 else 'days'}.", "no finding")

    fpar = [
        ("Patient takes metformin 500 mg once a day.", "Patient takes metformin 500 mg once per day."),
        ("Patient takes metformin 500 mg once a day.", "Patient takes metformin 500 mg daily."),
        ("Patient takes metformin 500 mg twice a day.", "Patient takes metformin 500 mg twice per day."),
        ("Patient takes metformin 500 mg twice a day.", "Patient takes metformin 500 mg twice daily."),
        ("Patient takes metformin 500 mg three times a day.", "Patient takes metformin 500 mg three times per day."),
        ("Patient takes metformin 500 mg three times a day.", "Patient takes metformin 500 mg three times daily."),
        ("Patient takes metformin 500 mg four times a day.", "Patient takes metformin 500 mg four times per day."),
        ("Patient takes metformin 500 mg four times a day.", "Patient takes metformin 500 mg four times daily."),
        ("Patient takes metformin 500 mg weekly.", "Patient takes metformin 500 mg once a week."),
        ("Patient takes metformin 500 mg nightly.", "Patient takes metformin 500 mg each night."),
    ]
    for a, b in fpar:
        add(cases, "frequency_paraphrase_control", False, a, b, "no finding")

    assert len(cases) == 140
    return cases


def evaluate(cases, extractor):
    rows = []
    tp = tn = fp = fn = 0
    for c in cases:
        fs = compare_facts(extractor(c["source"]), extractor(c["transformed"]))
        pred = bool(fs)
        pos = c["positive"]
        if pos and pred:
            tp += 1
            cls = "TP"
        elif pos and not pred:
            fn += 1
            cls = "FN"
        elif not pos and pred:
            fp += 1
            cls = "FP"
        else:
            tn += 1
            cls = "TN"
        rows.append({**c, "prediction": pred, "classification": cls, "findings": [f.to_dict() for f in fs]})
    precision = tp/(tp+fp) if tp+fp else 0
    recall = tp/(tp+fn) if tp+fn else 0
    specificity = tn/(tn+fp) if tn+fp else 0
    accuracy = (tp+tn)/len(cases)
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0
    return rows, {"TP": tp, "TN": tn, "FP": fp, "FN": fn, "precision": precision, "recall": recall, "f1": f1, "specificity": specificity, "accuracy": accuracy}


def main():
    out = Path(__file__).parent
    cases = build_cases()
    current_rows, current = evaluate(cases, extract_facts)
    base_rows, base = evaluate(cases, baseline_extract)

    with open(out / "icaiae_benchmark_v1.jsonl", "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    with open(out / "icaiae_results_current.jsonl", "w", encoding="utf-8") as f:
        for r in current_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out / "icaiae_results_baseline.jsonl", "w", encoding="utf-8") as f:
        for r in base_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    b_correct = [r["classification"] in {"TP", "TN"} for r in base_rows]
    c_correct = [r["classification"] in {"TP", "TN"} for r in current_rows]
    improve = sum((not b) and c for b, c in zip(b_correct, c_correct))
    regress = sum(b and (not c) for b, c in zip(b_correct, c_correct))
    p = binomtest(min(improve, regress), n=improve+regress, p=0.5, alternative="two-sided").pvalue if improve+regress else 1

    print("BASELINE", base)
    print("CURRENT", current)
    print("paired improved", improve, "regressed", regress, "McNemar exact p", p)

    from collections import Counter, defaultdict
    for label, rows in [("baseline", base_rows), ("current", current_rows)]:
        d = defaultdict(Counter)
        for r in rows:
            d[r["group"]][r["classification"]] += 1
        print("\n", label)
        for g in sorted(d):
            print(g, dict(d[g]))


if __name__ == "__main__":
    main()
