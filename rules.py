import re

# -------------------------
# Helper functions
# -------------------------
def preprocess(text: str) -> str:
    text = text.lower()
    text = text.replace("can't", "cant")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def keyword_match_score(text: str, keywords: list) -> int:
    """
    More reliable scoring:
    - phrase match counts more
    - word boundary match avoids false positives
    """
    score = 0
    for k in keywords:
        k = k.lower()

        # phrase match
        if " " in k and k in text:
            score += 3
        else:
            # single keyword - word boundary
            pattern = r"\b" + re.escape(k) + r"\b"
            if re.search(pattern, text):
                score += 2

    return score


SEVERITY_RANK = {"High": 3, "Medium": 2, "Low": 1}

# -------------------------
# Conditions Knowledge Base
# follow_up now has types: choice/number/text
# -------------------------
CONDITIONS = [

    # ================= HIGH =================
    {
        "id": "heart",
        "condition": "Possible Heart Issue",
        "severity": "High",
        "doctor": "Cardiologist",
        "keywords": [
            "chest pain", "pressure in chest", "tightness in chest",
            "pain in chest", "heart pain"
        ],
        "advice": "Seek emergency medical help immediately. Do not ignore chest pain.",
        "follow_up": [
            {"q": "Is the chest pain severe and lasting more than 5 minutes?", "type": "choice"},
            {"q": "Do you also have sweating, dizziness, or pain spreading to arm/jaw?", "type": "choice"},
        ],
    },

    {
        "id": "breathing",
        "condition": "Serious Breathing Issue",
        "severity": "High",
        "doctor": "Pulmonologist",
        "keywords": [
            "shortness of breath", "difficulty breathing", "breathlessness",
            "cant breathe", "breathing problem", "breathless"
        ],
        "advice": "Seek medical attention immediately. Breathing difficulty can be dangerous.",
        "follow_up": [
            {"q": "Is it sudden and worsening quickly?", "type": "choice"},
            {"q": "Do you feel chest tightness or wheezing?", "type": "choice"},
        ],
    },

    {
        "id": "seizure",
        "condition": "Seizure Episode",
        "severity": "High",
        "doctor": "Neurologist",
        "keywords": ["seizure", "fits", "convulsions"],
        "advice": "Seek urgent medical help.",
        "follow_up": [
            {"q": "Did the person lose consciousness?", "type": "choice"},
            {"q": "How many minutes did the episode last?", "type": "number", "min": 0, "max": 30},
        ],
    },

    {
        "id": "bleeding",
        "condition": "Severe Bleeding",
        "severity": "High",
        "doctor": "Emergency Medicine",
        "keywords": ["heavy bleeding", "severe bleeding", "blood loss", "bleeding a lot"],
        "advice": "Apply pressure to the wound and seek emergency help immediately.",
        "follow_up": [
            {"q": "Is the bleeding not stopping even after applying pressure?", "type": "choice"},
            {"q": "Is the person feeling dizzy or weak?", "type": "choice"},
        ],
    },

    # ================= MEDIUM =================
    {
        "id": "viral",
        "condition": "Viral Fever (Possible Infection)",
        "severity": "Medium",
        "doctor": "General Physician",
        "keywords": ["fever", "high temperature", "body pain", "fatigue", "weakness", "headache"],
        "advice": "Rest, drink fluids, and monitor temperature. Consult a doctor if fever lasts >2 days.",
        "follow_up": [
            {"q": "How many days have you had fever?", "type": "number", "min": 0, "max": 14},
            {"q": "Do you also have sore throat, cough, or chills?", "type": "choice"},
        ],
    },

    {
        "id": "stomach",
        "condition": "Stomach Infection / Gastric Issue",
        "severity": "Medium",
        "doctor": "Gastroenterologist",
        "keywords": ["stomach pain", "abdominal pain", "stomach ache", "belly pain", "cramps"],
        "advice": "Eat light food and drink ORS.",
        "follow_up": [
            {"q": "Do you have vomiting or loose motions along with stomach pain?", "type": "choice"},
            {"q": "Rate your stomach pain from 1 to 10", "type": "number", "min": 1, "max": 10},
        ],
    },

    {
        "id": "food_poisoning",
        "condition": "Food Poisoning / Diarrhea",
        "severity": "Medium",
        "doctor": "Gastroenterologist",
        "keywords": ["vomiting", "nausea", "diarrhea", "loose motions", "watery stools"],
        "advice": "ORS and hydration are essential.",
        "follow_up": [
            {"q": "How many times today?", "type": "number", "min": 0, "max": 25},
            {"q": "Are you able to drink fluids?", "type": "choice"},
        ],
    },

    {
        "id": "uti",
        "condition": "Urinary Tract Infection",
        "severity": "Medium",
        "doctor": "Urologist",
        "keywords": ["burning urination", "frequent urination", "uti"],
        "advice": "Drink water and consult a doctor.",
        "follow_up": [
            {"q": "Do you have fever or back pain?", "type": "choice"},
            {"q": "How many days has this continued?", "type": "number", "min": 0, "max": 30},
        ],
    },

    {
        "id": "ear",
        "condition": "Ear Pain / Infection",
        "severity": "Medium",
        "doctor": "ENT Specialist",
        "keywords": ["ear pain", "ear ache", "ear infection"],
        "advice": "Avoid water in ear and consult ENT.",
        "follow_up": [
            {"q": "Is there ear discharge?", "type": "choice"},
            {"q": "Is hearing reduced?", "type": "choice"},
        ],
    },

    {
        "id": "eye",
        "condition": "Eye Irritation / Watery Eyes",
        "severity": "Low",
        "doctor": "Ophthalmologist",
        "keywords": ["watery eyes", "eye irritation", "red eyes", "eye pain"],
        "advice": "Avoid rubbing eyes and use clean water.",
        "follow_up": [
            {"q": "Is there redness or itching?", "type": "choice"},
        ],
    },

    {
        "id": "burping",
        "condition": "Frequent Burping / Gas",
        "severity": "Low",
        "doctor": "Gastroenterologist",
        "keywords": ["burping", "gas", "bloating", "belching"],
        "advice": "Avoid carbonated drinks and eat slowly.",
        "follow_up": [
            {"q": "Does it worsen after meals?", "type": "choice"},
        ],
    },

    {
        "id": "leg_pain",
        "condition": "Leg Pain / Muscle Strain",
        "severity": "Low",
        "doctor": "Orthopedic",
        "keywords": ["leg pain", "calf pain", "thigh pain"],
        "advice": "Rest and gentle stretching.",
        "follow_up": [
            {"q": "Did pain start after physical activity?", "type": "choice"},
        ],
    },

    {
        "id": "arm_pain",
        "condition": "Arm Pain / Muscle Strain",
        "severity": "Low",
        "doctor": "Orthopedic",
        "keywords": ["arm pain", "shoulder pain", "elbow pain"],
        "advice": "Avoid strain and rest.",
        "follow_up": [
            {"q": "Is movement painful?", "type": "choice"},
        ],
    },

    {
        "id": "joint_pain",
        "condition": "Joint Pain",
        "severity": "Low",
        "doctor": "Orthopedic / Rheumatologist",
        "keywords": ["joint pain", "knee pain", "shoulder joint pain"],
        "advice": "Warm compress and rest.",
        "follow_up": [
            {"q": "Is joint swelling present?", "type": "choice"},
        ],
    },

    {
        "id": "back_pain",
        "condition": "Back Pain",
        "severity": "Low",
        "doctor": "Orthopedic",
        "keywords": ["back pain", "lower back pain", "spine pain"],
        "advice": "Correct posture and rest.",
        "follow_up": [
            {"q": "Does pain increase on bending?", "type": "choice"},
        ],
    },

    {
        "id": "menstrual",
        "condition": "Menstrual Cramps",
        "severity": "Low",
        "doctor": "Gynecologist",
        "keywords": ["period pain", "menstrual cramps", "period cramps"],
        "advice": "Warm compress and rest help.",
        "follow_up": [
            {"q": "Is pain severe enough to stop daily activity?", "type": "choice"},
        ],
    },
]


# -------------------------
# Main Analyzer
# -------------------------
def analyze_symptoms(user_text: str):
    text = preprocess(user_text)

    scored = []
    for item in CONDITIONS:
        score = keyword_match_score(text, item["keywords"])
        if score > 0:
            scored.append((score, item))

    # No match
    if not scored:
        return {
            "condition": "Unidentified Symptoms",
            "severity": "Low",
            "advice": "Monitor your symptoms. If they persist or worsen, consult a healthcare professional.",
            "possible_conditions": [],
            "follow_up_questions": [],
            "condition_id": None,
        }

    # Sort by score (desc)
    scored.sort(key=lambda x: x[0], reverse=True)

    # Get top 3 to show possible conditions
    top_matches = scored[:3]

    # ✅ Pick the most critical severity among top matches (priority to High)
    chosen = top_matches[0][1]
    for _, item in top_matches:
        if SEVERITY_RANK[item["severity"]] > SEVERITY_RANK[chosen["severity"]]:
            chosen = item

    possible_conditions = [m[1]["condition"] for m in top_matches]

    return {
        "condition": chosen["condition"],
        "severity": chosen["severity"],
        "advice": chosen["advice"],
        "possible_conditions": possible_conditions,
        "follow_up_questions": chosen.get("follow_up", []),
        "condition_id": chosen["id"],
        "doctor": chosen.get("doctor", "General Physician"),

    }


# -------------------------
# Follow-up evaluator
# answers_dict is {"question": answer}
# -------------------------
def evaluate_followup(condition_id: str, answers_dict: dict):
    final_severity = "Low"
    final_advice = "Monitor symptoms and consult a doctor if they worsen."

    # Helper: safely read choice answers
    def ans_yes(q):
        return str(answers_dict.get(q, "")).strip().lower() == "yes"

    # Helper: safely read number answers
    def ans_num(q):
        try:
            return int(answers_dict.get(q, 0))
        except:
            return 0

    # ✅ HEART
    if condition_id == "heart":
        if any(answers_dict.values()):
            final_severity = "High"
            final_advice = "Chest pain with risk signs needs emergency care. Call emergency services immediately."
        else:
            final_severity = "Medium"
            final_advice = "Chest discomfort should not be ignored. Consult a doctor soon."

    # ✅ BREATHING
    elif condition_id == "breathing":
        if "yes" in [str(v).lower() for v in answers_dict.values()]:
            final_severity = "High"
            final_advice = "Breathing difficulty may be serious. Seek urgent medical attention immediately."
        else:
            final_severity = "Medium"
            final_advice = "If breathing discomfort continues, consult a doctor and avoid exertion."

    # ✅ VIRAL FEVER
    elif condition_id == "viral":
        days_q = "How many days have you had fever?"
        days = ans_num(days_q)

        if days >= 3:
            final_severity = "Medium"
            final_advice = "Fever lasting 3+ days needs doctor consultation and testing if required."
        else:
            final_severity = "Low"
            final_advice = "Rest, fluids, and monitor temperature."

    # ✅ FOOD POISONING
    elif condition_id == "food_poisoning":
        count_q = "How many times did you vomit or have loose motions today?"
        count = ans_num(count_q)

        if count >= 6:
            final_severity = "High"
            final_advice = "High risk of dehydration. Seek medical help quickly and continue ORS if possible."
        else:
            final_severity = "Medium"
            final_advice = "Take ORS, rest, and eat bland food. Consult a doctor if symptoms persist."

    # ✅ STOMACH
    elif condition_id == "stomach":
        pain_q = "Rate your stomach pain from 1 to 10"
        pain = ans_num(pain_q)

        if pain >= 7:
            final_severity = "Medium"
            final_advice = "Severe stomach pain should be checked by a doctor soon."
        else:
            final_severity = "Low"
            final_advice = "Light diet + hydration. Avoid spicy/oily meals."

    # ✅ UTI
    elif condition_id == "uti":
        if "yes" in [str(v).lower() for v in answers_dict.values()]:
            final_severity = "Medium"
            final_advice = "UTI symptoms with fever/back pain need doctor evaluation soon."
        else:
            final_severity = "Low"
            final_advice = "Drink water and monitor. Consult doctor if burning continues."

    return {
        "final_severity": final_severity,
        "final_advice": final_advice,
    }
