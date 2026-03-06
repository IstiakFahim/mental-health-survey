import streamlit as st
import pandas as pd
import gspread
import time
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
BATCH_NUMBER = 1  # <--- CHANGE THIS FOR EACH APP (2, 3, 4, 5)
CSV_FILE = f'survey_batch_{BATCH_NUMBER}.csv'
SHEET_NAME = f'Survey_Results_Batch_{BATCH_NUMBER}'
TAB_NAME = 'Result'

# --- GOOGLE SHEETS SETUP ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

def get_worksheet():
    client = get_gspread_client()
    # Retry connecting to the sheet
    for i in range(3): 
        try:
            sh = client.open(SHEET_NAME)
            return sh.worksheet(TAB_NAME)
        except:
            time.sleep(2)
    return None

# --- INITIALIZE SESSION STATE ---
if 'agreed' not in st.session_state:
    st.session_state.agreed = False

if 'answered_ids' not in st.session_state:
    worksheet = get_worksheet()
    if worksheet:
        try:
            records = worksheet.get_all_records()
            st.session_state.answered_ids = [str(r['id']) for r in records if 'id' in r]
        except:
            st.session_state.answered_ids = []
    else:
        st.session_state.answered_ids = []

# --- PAGE 1: INSTRUCTIONS & AGREEMENT ---
if not st.session_state.agreed:
    st.title("📋 Annotation Instructions & Guidelines")
    
    with st.expander("⚙️ Technical Rules (Click to expand)", expanded=True):
        st.markdown("""
        1. **Unique Identity:** In the **'Enter your name:'** section, use a consistent ID (e.g., `fahim_istiak`). Use this same ID for all 600 rows.
        2. **Input Persistence:** Your name is saved as you work. If the app **times out** or you **refresh (F5)**, you must re-enter your name.
        3. **Auto-Save & Resume:** Progress saves instantly on "Submit." The app resumes where you left off if you close the browser.
        4. **Ownership:** This link is for **you only**. Do not share it to avoid data conflicts.
        5. **Submission:** Click **"Submit & Next ➡️"** to save and load the next case.
        """)

    st.markdown("### 🧠 DSM-5 Data Quality & Labeling Guide")
    st.write("Please read the following definitions carefully. They follow the DSM-5 mental health hierarchy:")

    # Descriptive Hierarchical List
    st.markdown("""
    **1. Mood Disorders** (Conditions affecting your emotional state)
    * **Bipolar Disorders:** Extreme swings between high energy (mania) and low mood.
        * *Includes: Bipolar 1, Bipolar 2, Cyclothymic.*
    * **Depressive Disorders:** Intense, long-lasting feelings of sadness or loss of interest.
        * *Includes: Major Depressive, Dysthymia, Seasonal Affective.*

    **2. Personality Disorders** (Long-term, rigid patterns of behavior and thinking)
    * **Cluster A (Odd/Eccentric):** Characterized by social awkwardness and social withdrawal (Paranoid, Schizoid, Schizotypal).
    * **Cluster B (Dramatic/Emotional):** Characterized by intense emotions and impulsive behavior (Antisocial, Histrionic, Narcissistic).
    * **Cluster C (Anxious/Fearful):** Characterized by high levels of anxiety and fear (Avoidant, Dependent, Obsessive-Compulsive Personality).

    **3. Anxiety Disorders** (Persistent, excessive fear or worry)
    * **Panic & Phobias:** Sudden terror or fear triggered by specific objects/social situations.
    * **Generalized Anxiety (GAD):** Constant, non-stop worry about various daily things.

    **4. Sleep Disorders** (Problems with sleep quality, timing, and amount)
    * **Insomnia Spectrum:** Constant difficulty falling asleep or staying asleep.
    * **Other Issues:** Sudden sleep (Narcolepsy), breathing issues (Apnea), or leg discomfort.

    **5. OCD & Related Disorders** (Repetitive thoughts and "checking" rituals)
    * **Obsessions & Compulsions:** Unwanted rituals used to reduce anxiety (OCD, Body Dysmorphia, Hoarding).

    **6. Eating Disorders** (Serious disturbances in eating behavior)
    * **Weight & Food Issues:** Extreme food restriction or lack of control over eating.

    **7. Neurodevelopmental Disorders** (Conditions appearing in early childhood)
    * **ADHD & Autism:** Focus issues, hyperactivity, or challenges with social communication.

    **8. Schizophrenia Spectrum** (A break from reality)
    * **Psychotic Disorders:** Seeing or hearing things that aren't there (hallucinations) or holding false beliefs (delusions).

    **9. Trauma & Stressor-Related** (Triggered by a traumatic life event)
    * **PTSD & Adjustment:** Long-term trauma symptoms or extreme difficulty handling major life changes.

    **10. Substance-Related** (Problems related to drug or alcohol use)
    * **Addictive Disorders:** Compulsive use of substances despite them causing major life problems.
    """)

    st.divider()
    if st.button("✅ I have read the definitions and I'm ready to start", type="primary"):
        st.session_state.agreed = True
        st.rerun()

# --- PAGE 2: THE SURVEY ---
else:
    df_questions = pd.read_csv(CSV_FILE)
    remaining_df = df_questions[~df_questions['id'].astype(str).isin(st.session_state.answered_ids)]

    st.title(f"📋 Mental Health Survey (Batch {BATCH_NUMBER})")

    # Sidebar Progress
    total = len(df_questions)
    done = len(st.session_state.answered_ids)
    st.sidebar.write(f"**Progress: {done} / {total}**")
    st.sidebar.progress(done / total)
    if st.sidebar.button("📖 Review Instructions"):
        st.session_state.agreed = False
        st.rerun()

    if remaining_df.empty:
        st.balloons()
        st.success("🎉 All rows in this batch are completed!")
    else:
        current_row = remaining_df.iloc[0]
        
        with st.container(border=True):
            st.subheader(f"Case ID: {current_row['id']}")
            st.markdown(f"**Title:** {current_row['Title']}")
            st.write(f"**Body:** {current_row['Body']}")

        st.divider()
        
        if 'user_name' not in st.session_state:
            st.session_state.user_name = ""
        
        user_input = st.text_input("Enter your name:", value=st.session_state.user_name)
        st.session_state.user_name = user_input

        col1, col2, col3 = st.columns(3)
        with col1:
            cat = st.radio("Step 1: Category?", [current_row['Category'], current_row['Category_2'], current_row['Category_3']], key="cat")
        with col2:
            sub = st.radio("Step 2: Subcategory?", [current_row['Subcategory'], current_row['Subcategory_2'], current_row['Subcategory_3']], key="sub")
        with col3:
            dis = st.radio("Step 3: Disorder?", [current_row['SpecificDisorder'], current_row['SpecificDisorder_2'], current_row['SpecificDisorder_3']], key="dis")

        if st.button("Submit & Next ➡️", type="primary"):
            if not user_input:
                st.error("Please enter your name!")
            else:
                success = False
                # --- RETRY LOGIC FOR GOOGLE API ---
                with st.spinner("Saving to Google Sheets..."):
                    for attempt in range(5): # Try 5 times
                        try:
                            worksheet = get_worksheet()
                            new_data = [str(current_row['id']), current_row['Title'], current_row['Body'], cat, sub, dis, user_input]
                            worksheet.append_row(new_data)
                            
                            st.session_state.answered_ids.append(str(current_row['id']))
                            success = True
                            break # Exit the retry loop if successful
                        except Exception as e:
                            # Wait longer each time (Exponential Backoff)
                            wait_time = (attempt + 1) * 2 
                            time.sleep(wait_time)
                
                if success:
                    st.success("Saved!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Google is very busy right now. Please wait 15 seconds and click Submit again.")

