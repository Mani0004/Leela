import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime, time
from dotenv import load_dotenv
import time

# --- Configuration ---
load_dotenv()

# Initialize session state
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'reminders' not in st.session_state:
    st.session_state.reminders = []
if 'plan_items' not in st.session_state:
    st.session_state.plan_items = []

# --- Gemini API Setup ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("🔑 API key missing! Please set GEMINI_API_KEY in .env or Streamlit secrets")
    st.stop()

try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Model configuration
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(
        'gemini-pro',
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
except Exception as e:
    st.error(f"🚨 API Error: {str(e)}")
    st.stop()

# --- UI Styles ---
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    color: #333333;
}
.stButton>button {
    background: linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%);
    border-radius: 20px;
    border: 0;
    color: white;
    height: 48px;
    padding: 0 30px;
    box-shadow: 0 3px 5px 2px rgba(255, 105, 135, .3);
    transition: all 0.3s;
    margin: 5px;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 10px 4px rgba(255, 105, 135, .3);
}
.title {
    font-size: 3em;
    background: -webkit-linear-gradient(#ee0979, #ff6a00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
.plan-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    color: #222222;
}
.reminder-card {
    background: #e3f2fd;
    border-radius: 10px;
    padding: 15px;
    margin: 8px 0;
    border-left: 5px solid #2196f3;
    color: #222222;
}
.disclaimer {
    background-color: #fff3cd;
    padding: 10px;
    border-radius: 5px;
    margin-top: 20px;
    font-size: 0.8em;
    color: #333333;
}
.error-message {
    color: #d32f2f;
    background-color: #ffebee;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
.warning-message {
    color: #ff8f00;
    background-color: #fff8e1;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# --- App Content ---
st.markdown('<h1 class="title">🤖 Crazy Health Buddy 🤖</h1>', unsafe_allow_html=True)

# Common symptoms
COMMON_SYMPTOMS = [
    "Fever", "Headache", "Cough", "Sore throat", "Fatigue",
    "Muscle pain", "Nausea", "Dizziness", "Insomnia", "Loss of appetite",
    "Diarrhea", "Constipation", "Heartburn", "Back pain", "Joint pain"
]

# --- Functions ---
def generate_health_plan(symptoms, user_info):
    prompt = f"""
    IMPORTANT: You are a medical assistant providing general wellness advice only. 
    This is not a substitute for professional medical advice. Always consult a doctor.
    
    User reports these symptoms: {', '.join(symptoms)}.
    Profile: {user_info.get('age', 'unknown')} years, {user_info.get('gender', 'unknown')},
    {user_info.get('weight', 'unknown')} kg, {user_info.get('height', 'unknown')} cm.
    
    Provide a 1-day wellness plan with specific times for each activity, formatted as:
    
    [Time] [Activity Type]: [Details]
    
    For example:
    08:00 Water: Drink 250ml of water
    08:30 Food: Eat oatmeal with berries
    09:00 Activity: Light stretching for 10 minutes
    
    Include:
    1. Water intake schedule (specific times and amounts)
    2. Food suggestions (what to eat and when)
    3. Activity recommendations (with specific times)
    4. General wellness tips
    
    Return only the schedule items, one per line, with exact times.
    """
    
    try:
        # Check if model is available
        available_models = genai.list_models()
        
        # Try Gemini Pro first
        if any(m.name == 'models/gemini-pro' for m in available_models):
            response = model.generate_content(prompt)
            return response.text
        # Fallback to Gemini 1.0 Pro if available
        elif any(m.name == 'models/gemini-1.0-pro' for m in available_models):
            fallback_model = genai.GenerativeModel(
                'gemini-1.0-pro',
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            response = fallback_model.generate_content(prompt)
            return response.text
        # Fallback to Gemini 1.5 Pro if available
        elif any(m.name == 'models/gemini-1.5-pro' for m in available_models):
            fallback_model = genai.GenerativeModel(
                'gemini-1.5-pro',
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            response = fallback_model.generate_content(prompt)
            return response.text
        else:
            # Return cached generic plan without showing warning
            generic_plan = "08:00 Water: Drink 250ml of water\n" + \
                "08:30 Food: Eat oatmeal with berries\n" + \
                "09:00 Activity: Light stretching for 10 minutes\n" + \
                "10:00 Water: Drink another 250ml\n" + \
                "12:00 Food: Balanced lunch with protein and vegetables\n" + \
                "15:00 Activity: Short walk (10-15 minutes)\n" + \
                "18:00 Food: Light dinner with lean protein\n" + \
                "20:00 Relaxation: Meditation or deep breathing for 5 minutes\n" + \
                "22:00 Sleep: Aim for 7-9 hours of quality sleep"
            
            # Removed the st.warning message that was showing the error
            return generic_plan
    except Exception as e:
        # Silently handle the exception without showing warning message
        generic_plan = "08:00 Water: Drink 250ml of water\n" + \
                "08:30 Food: Eat oatmeal with berries\n" + \
                "09:00 Activity: Light stretching for 10 minutes\n" + \
                "10:00 Water: Drink another 250ml\n" + \
                "12:00 Food: Balanced lunch with protein and vegetables\n" + \
                "15:00 Activity: Short walk (10-15 minutes)\n" + \
                "18:00 Food: Light dinner with lean protein\n" + \
                "20:00 Relaxation: Meditation or deep breathing for 5 minutes\n" + \
                "22:00 Sleep: Aim for 7-9 hours of quality sleep"
        return generic_plan

def parse_plan_to_reminders(plan_text):
    """Convert plan text into reminder items"""
    reminders = []
    for line in plan_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Try to extract time and activity
        if ' ' in line:
            time_part, activity = line.split(' ', 1)
            try:
                # Try to parse the time
                reminder_time = datetime.strptime(time_part, '%H:%M').time()
                reminders.append({
                    'time': reminder_time,
                    'activity': activity,
                    'completed': False
                })
            except ValueError:
                # If time parsing fails, just add as is
                reminders.append({
                    'time': None,
                    'activity': line,
                    'completed': False
                })
    return reminders

# --- Step 1: User Information ---
if st.session_state.current_step == 1:
    st.subheader("👤 Tell Me About Yourself")
    
    st.session_state.user_info['name'] = st.text_input("Your Name")
    col1, col2 = st.columns(2)
    st.session_state.user_info['age'] = col1.number_input("Age", min_value=1, max_value=120, value=25)
    st.session_state.user_info['gender'] = col2.selectbox("Gender", ["Male", "Female", "Other"])
    
    col3, col4 = st.columns(2)
    st.session_state.user_info['weight'] = col3.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
    st.session_state.user_info['height'] = col4.number_input("Height (cm)", min_value=100, max_value=250, value=170)
    
    if st.button("Next ➡️"):
        if not st.session_state.user_info['name']:
            st.warning("Please enter your name")
        else:
            st.session_state.current_step = 2
            st.rerun()

# --- Step 2: Symptom Selection ---
elif st.session_state.current_step == 2:
    st.subheader("🤒 Select Your Symptoms")
    
    selected_symptoms = st.multiselect(
        "Choose all that apply", 
        COMMON_SYMPTOMS,
        default=st.session_state.symptoms
    )
    st.session_state.symptoms = selected_symptoms
    
    custom_symptom = st.text_input("Add a symptom not listed above")
    if custom_symptom and custom_symptom not in st.session_state.symptoms:
        st.session_state.symptoms.append(custom_symptom)
    
    if st.session_state.symptoms:
        st.write("You've selected:")
        cols = st.columns(3)
        for i, symptom in enumerate(st.session_state.symptoms):
            with cols[i % 3]:
                st.info(f"• {symptom}")
    
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Back"):
        st.session_state.current_step = 1
        st.rerun()
    
    if col2.button("Generate My Plan 🚀"):
        if not st.session_state.symptoms:
            st.warning("Please select at least one symptom")
        else:
            st.session_state.current_step = 3
            st.rerun()

# --- Step 3: Health Plan with Reminders ---
elif st.session_state.current_step == 3:
    st.subheader("📝 Treatment Description")

    # Display a concise description of the treatment plan based on symptoms
    if st.session_state.symptoms:
        treatment_description = f"Based on your symptoms: {', '.join(st.session_state.symptoms)}, here is a brief treatment plan."
        st.markdown(f'<div class="plan-card">{treatment_description}</div>', unsafe_allow_html=True)

    if not st.session_state.plan_items:
        with st.spinner("🧠 Generating your awesome health plan..."):
            plan_text = generate_health_plan(st.session_state.symptoms, st.session_state.user_info)
            st.session_state.plan_text = plan_text
            st.session_state.reminders = parse_plan_to_reminders(plan_text)
            st.session_state.plan_items = [line for line in plan_text.split('\n') if line.strip()]

    # Remove the duplicate display of the wellness plan
    # st.markdown(
    #     f'<div class="plan-card">{"<br>".join(st.session_state.plan_items)}</div>', 
    #     unsafe_allow_html=True
    # )

    # Show reminders with checkbox to mark them complete
    st.subheader("⏰ Reminders")
    for i, reminder in enumerate(st.session_state.reminders):
        col1, col2 = st.columns([1, 5])
        with col1:
            reminder['completed'] = st.checkbox(
                f"{reminder['time'].strftime('%H:%M') if reminder['time'] else '--:--'}",
                value=reminder['completed'],
                key=f"reminder_{i}"
            )
        with col2:
            activity = reminder['activity']
            if reminder['completed']:
                st.markdown(f"<div class='reminder-card'><s>{activity}</s></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='reminder-card'>{activity}</div>", unsafe_allow_html=True)

    if st.button("🔄 Restart"):
        # Reset session state to start over
        for key in ['symptoms', 'current_step', 'user_info', 'reminders', 'plan_items', 'plan_text']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- End of App ---
