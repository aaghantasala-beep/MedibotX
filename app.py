import streamlit as st
from rules import analyze_symptoms, evaluate_followup
import base64
import os
from datetime import datetime

# ✅ PDF
from fpdf import FPDF
import tempfile

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="MediBotX",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# Background + CSS
# -------------------------
def set_background(image_path):
    if not os.path.exists(image_path):
        st.error(f"❌ Background image not found: {image_path}")
        return

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.45);
            z-index: -1;
        }}

        .main .block-container {{
            padding-top: 2.0rem;
        }}

        /* Branding card */
        .brand-card {{
            background: rgba(255,255,255,0.60);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 2px solid rgba(37, 99, 235, 0.35);
            padding: 16px 22px;
            border-radius: 22px;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.22);
            margin-bottom: 18px;
            text-align: center;
        }}

        .brand-title {{
            font-size: 44px;
            font-weight: 900;
            letter-spacing: 1px;
            margin: 0;
            background: linear-gradient(90deg, #111827, #2563eb, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0px 6px 20px rgba(0,0,0,0.25);
            font-family: "Trebuchet MS", "Poppins", "Segoe UI", sans-serif;
        }}

        .brand-sub {{
            font-size: 16px;
            font-weight: 750;
            margin-top: 6px;
            color: rgba(0,0,0,0.75) !important;
            letter-spacing: 0.3px;
            font-family: "Segoe UI", "Poppins", sans-serif;
        }}

        /* Panels */
        .panel {{
            background: rgba(255,255,255,0.55);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.35);
            padding: 18px 18px;
            border-radius: 18px;
            box-shadow: 0px 8px 25px rgba(0,0,0,0.20);
            margin-bottom: 18px;
        }}

        .panel-title {{
            font-size: 20px;
            font-weight: 850;
            color: black !important;
            margin-bottom: 8px;
        }}

        /* Text */
        h1,h2,h3,h4,h5,h6,p,label,span {{
            color: black !important;
        }}

        /* Textarea */
        textarea {{
            background-color: rgba(255,255,255,0.92) !important;
            color: black !important;
            border-radius: 14px !important;
            border: 1px solid rgba(0,0,0,0.20) !important;
            padding: 12px !important;
            font-weight: 600 !important;
        }}

        /* Buttons */
        div.stButton > button {{
            background-color: #111827 !important;
            border-radius: 14px !important;
            font-weight: 750 !important;
            border: 1px solid rgba(255,255,255,0.35) !important;
            padding: 10px 18px !important;
            width: 100% !important;
        }}
        div.stButton > button * {{
            color: white !important;
        }}

        /* Download button */
        div[data-testid="stDownloadButton"] > button {{
            background-color: #111827 !important;
            border-radius: 14px !important;
            font-weight: 750 !important;
            border: 1px solid rgba(255,255,255,0.35) !important;
            padding: 10px 18px !important;
        }}
        div[data-testid="stDownloadButton"] > button * {{
            color: white !important;
        }}

        /* Link button */
        div[data-testid="stLinkButton"] > a {{
            background-color: #111827 !important;
            color: white !important;
            border-radius: 14px !important;
            font-weight: 750 !important;
            border: 1px solid rgba(255,255,255,0.35) !important;
            padding: 10px 18px !important;
            text-decoration: none !important;
            display: inline-block !important;
        }}
        div[data-testid="stLinkButton"] > a * {{
            color: white !important;
        }}

        /* Result cards */
        .result-card {{
            background: rgba(255,255,255,0.55);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.35);
            padding: 16px;
            border-radius: 18px;
            margin-top: 5px;
            margin-bottom: 12px;
            font-weight: 650;
            color: black !important;
        }}

        .doctor-card {{
            background: rgba(255,255,255,0.50);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.35);
            padding: 14px 16px;
            border-radius: 18px;
            margin-top: 10px;
            margin-bottom: 10px;
            font-weight: 750;
            color: black !important;
        }}

        .high {{ color: #ff1744 !important; font-weight: 800; }}
        .medium {{ color: #ff9100 !important; font-weight: 800; }}
        .low {{ color: #00c853 !important; font-weight: 800; }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: rgba(0,0,0,0.88) !important;
        }}
        section[data-testid="stSidebar"] * {{
            color: white !important;
        }}

        header, header * {{
            color: white !important;
        }}

        /* Alerts */
        div[data-testid="stAlert"] {{
            font-size: 18px !important;
            font-weight: 750 !important;
            border-radius: 16px !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            background: rgba(255,255,255,0.60) !important;
            border: 1px solid rgba(0,0,0,0.15) !important;
        }}

        div[data-testid="stAlert"] * {{
            font-size: 18px !important;
            font-weight: 750 !important;
            color: black !important;
        }}

        /* Follow-up section heading bigger */
        h2, h3 {{
            font-size: 30px !important;
            font-weight: 900 !important;
        }}

        /* ✅ Highlight ALL follow-up question texts (radio + number + text input) */
        /* ✅ Follow-up question text clean (no extra box) */
       /* ✅ SAME boxed style for all follow-up questions (radio + number + text inputs) */
        div[data-testid="stRadio"] p,
        div[data-testid="stNumberInput"] p,
        div[data-testid="stTextInput"] p {{
            display: inline-block !important;
            background: rgba(255, 255, 255, 0.78) !important;
            padding: 10px 14px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(0,0,0,0.12) !important;
            font-size: 22px !important;
            font-weight: 900 !important;
            color: black !important;
            margin-bottom: 10px !important;
}}
    /* ✅ Make textarea placeholder brighter (gray) */
        textarea::placeholder {{
            color: rgba(80, 80, 80, 0.65) !important;  /* gray-ish */
            font-weight: 700 !important;
            font-size: 24px !important;
}}


        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ Apply background image
set_background(r"C:\Users\alaka\Desktop\MediBotX\bot1.jpeg")

# -------------------------
# PDF Builder
# -------------------------
def generate_pdf_report(history_list, current_case):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "MediBotX Health Report", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Previous Cases:", ln=True)
    pdf.set_font("Arial", "", 11)

    if not history_list:
        pdf.multi_cell(0, 7, "No previous cases.")
    else:
        for i, h in enumerate(history_list, start=1):
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 7, f"Case {i}")
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(0, 7, f"Symptoms: {h['symptoms']}")
            pdf.multi_cell(0, 7, f"Condition: {h['condition']}")
            pdf.multi_cell(0, 7, f"Severity: {h['severity']}")
            pdf.multi_cell(0, 7, f"Advice: {h['advice']}")
            pdf.multi_cell(0, 7, f"Time: {h.get('time', '-')}")
            pdf.ln(3)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Current Case:", ln=True)
    pdf.set_font("Arial", "", 11)

    if current_case is None:
        pdf.multi_cell(0, 7, "No active case currently.")
    else:
        pdf.multi_cell(0, 7, f"Symptoms: {current_case['symptoms']}")
        pdf.multi_cell(0, 7, f"Condition: {current_case['result']['condition']}")
        pdf.multi_cell(0, 7, f"Severity: {current_case['result']['severity']}")
        pdf.multi_cell(0, 7, f"Advice: {current_case['result']['advice']}")

        if current_case.get("final"):
            pdf.ln(2)
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 7, "Final Follow-up Result:")
            pdf.set_font("Arial", "", 11)
            pdf.multi_cell(0, 7, f"Final Severity: {current_case['final']['final_severity']}")
            pdf.multi_cell(0, 7, f"Final Advice: {current_case['final']['final_advice']}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as f:
        return f.read()

# -------------------------
# Session state
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "current_case" not in st.session_state:
    st.session_state.current_case = None

if "followup_answers" not in st.session_state:
    st.session_state.followup_answers = {}

# -------------------------
# Sidebar History
# -------------------------
st.sidebar.title("📜 Previous Cases")

if st.sidebar.button("🧹 Clear History"):
    st.session_state.history = []

if not st.session_state.history:
    st.sidebar.write("No previous cases.")
else:
    for i, item in enumerate(reversed(st.session_state.history), start=1):
        label = f"Case {len(st.session_state.history) - i + 1}: {item['severity']}"
        with st.sidebar.expander(label):
            st.write("✅ Symptoms:", item["symptoms"])
            st.write("🩺 Condition:", item["condition"])
            st.write("⚠️ Severity:", item["severity"])
            st.write("💡 Advice:", item["advice"])
            st.write("🕒 Time:", item.get("time", "-"))

# -------------------------
# Branding
# -------------------------
st.markdown(
    """
    <div class="brand-card">
        <div class="brand-title">🩺 MediBotX</div>
        <div class="brand-sub">Health Assistant • Instant Symptom Triage</div>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# New case handler
# -------------------------
def handle_new_case(symptoms_text: str):
    if st.session_state.current_case is not None:
        old = st.session_state.current_case
        st.session_state.history.append({
            "symptoms": old["symptoms"],
            "condition": old["result"]["condition"],
            "severity": old["result"]["severity"],
            "advice": old["result"]["advice"],
            "time": datetime.now().strftime("%H:%M:%S")
        })

    res = analyze_symptoms(symptoms_text)
    st.session_state.current_case = {
        "symptoms": symptoms_text,
        "result": res,
        "final": None
    }
    st.session_state.followup_answers = {}

# -------------------------
# Layout (Input LEFT + Quick RIGHT)
# -------------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📝 Your Symptoms</div>', unsafe_allow_html=True)

    symptoms = st.text_area(
        "Enter symptoms to check and analyze:",
        height=140,
        placeholder="Example: fever, headache, stomach pain..."
    )

    b1, b2 = st.columns(2)
    analyze_btn = b1.button("✅ Analyze")
    clear_btn = b2.button("🧹 Clear")

    if clear_btn:
        st.session_state.current_case = None
        st.session_state.followup_answers = {}

    if analyze_btn and symptoms.strip():
        handle_new_case(symptoms.strip())

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">⚡ Quick Suggestions</div>', unsafe_allow_html=True)

    if st.button("🤒 Fever"):
        handle_new_case("fever headache weakness")
    if st.button("🤧 Cold"):
        handle_new_case("cold and cough")
    if st.button("💔 Chest Pain"):
        handle_new_case("chest pain and tightness in chest")
    if st.button("🤢 Stomach Pain"):
        handle_new_case("stomach pain and cramps")
    if st.button("😷 Breathing Issue"):
        handle_new_case("shortness of breath and difficulty breathing")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Output Section
# -------------------------
case = st.session_state.current_case

if case is None:
    st.info("🩺 Enter symptoms and click **Analyze** or use a quick suggestion.")
else:
    result = case["result"]
    doctor = result.get("doctor", "General Physician")
    severity = result["severity"]
    severity_class = severity.lower()

    st.markdown(
        f"""
        <div class="result-card">
            <b>Condition:</b> {result["condition"]}<br>
            <b>Severity:</b> <span class="{severity_class}">{severity}</span><br><br>
            <b>Recommended Specialist:</b> 🩺 <b>{doctor}</b><br><br>
            <b>Advice:</b> {result["advice"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    if severity == "High":
        st.progress(100)
    elif severity == "Medium":
        st.progress(60)
    else:
        st.progress(30)

    if severity == "High":
        st.error("🚨 This may be a medical emergency.")
        st.link_button("📞 Call Emergency Help (108)", "tel:108")
        doc_msg = f"🏥 Doctor Suggestion: <b>Immediate emergency care</b> required. Consult a <b>{doctor}</b> immediately."
    elif severity == "Medium":
        doc_msg = f"👨‍⚕️ Doctor Suggestion: Consult a <b>{doctor}</b> within 24–48 hours if symptoms continue."
    else:
        doc_msg = f"✅ Doctor Suggestion: Home care is usually enough. If needed, consult a <b>{doctor}</b>."


    st.markdown(f"<div class='doctor-card'>{doc_msg}</div>", unsafe_allow_html=True)

    if result.get("possible_conditions"):
        st.info("✅ Other possible conditions: " + ", ".join(result["possible_conditions"]))

    followups = result.get("follow_up_questions", [])
    condition_id = result.get("condition_id")

    if followups:
        st.markdown("### 🧾 Follow-up Questions")

        for i, fu in enumerate(followups):
            q_text = fu.get("q", f"Question {i+1}")
            q_type = fu.get("type", "choice")
            key = f"fu_{i}"

            if q_type == "choice":
                st.session_state.followup_answers[q_text] = st.radio(
                    q_text,
                    ["Yes", "No", "Not sure"],
                    key=key,
                    horizontal=True
                )

            elif q_type == "number":
                min_v = int(fu.get("min", 0))
                max_v = int(fu.get("max", 100))
                default_v = min_v  # ✅ must be >= min_v

                st.session_state.followup_answers[q_text] = st.number_input(
                    q_text,
                    min_value=min_v,
                    max_value=max_v,
                    value=default_v,
                    step=1,
                    key=key
                )

            else:
                st.session_state.followup_answers[q_text] = st.text_input(
                    q_text,
                    key=key
                )

        if st.button("✅ Submit Follow-up"):
            if condition_id:
                final = evaluate_followup(condition_id, st.session_state.followup_answers)
                case["final"] = final

    if case.get("final"):
        st.success(f"✅ Updated Severity: {case['final']['final_severity']}")
        st.info(f"💡 Final Advice: {case['final']['final_advice']}")

# Disclaimer
st.markdown(
    """
    <div class="result-card" style="font-size:18px; font-weight:800;">
    ⚠️ MediBotX does not replace a medical professional.
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------
# PDF Export
# -------------------------
st.markdown("### 📄 Export Report (PDF)")

pdf_bytes = generate_pdf_report(st.session_state.history, st.session_state.current_case)

st.download_button(
    label="⬇️ Download Report (PDF)",
    data=pdf_bytes,
    file_name="MediBotX_Report.pdf",
    mime="application/pdf"
)
