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
        - **Unique Identity:** Use a consistent ID (e.g., `firstname_lastname`) throughout the 600 rows.
        - **Persistence:** If the app times out or you refresh, you must re-enter your name.
        - **Auto-Save:** Progress is saved instantly. You can close the browser and resume later.
        """)

    st.markdown("### 🧠 DSM-5 Data Quality & Labeling Guide")
    st.write("Please read the following definitions. Categorize texts using this hierarchy:")

    st.markdown("""
    **1. Mood Disorders** (Emotional disturbances)
    * **Bipolar Disorders:** Extreme swings between mania and low mood.
        * *Includes: Bipolar 1, Bipolar 2, Cyclothymic Disorder.*
    * **Depressive Disorders:** Persistent sadness or loss of interest.
        * *Includes: Major Depressive, Dysthymia, Seasonal Affective.*

    **2. Personality Disorders** (Long-term rigid patterns)
    * **Cluster A (Odd):** Paranoid, Schizoid, Schizotypal.
    * **Cluster B (Dramatic):** Antisocial, Histrionic, Narcissistic.
    * **Cluster C (Anxious):** Avoidant, Dependent, Obsessive-Compulsive Personality.

    **3. Anxiety Disorders** (Excessive fear or worry)
    * **Phobias:** Social Anxiety, Agoraphobia.
    * **Panic Disorders:** Panic Disorder.
    * **Generalized Anxiety:** Generalized Anxiety Disorder (GAD).

    **4. Sleep Disorders** (Quality/timing issues)
    * **Insomnia Spectrum:** Insomnia.
    * **Other Issues:** Narcolepsy, Sleep Apnea, Restless Legs.

    **5. OCD & Related Disorders** (Rituals and unwanted thoughts)
    * **OCD Spectrum:** OCD, Body Dysmorphia, Hoarding.

    **6. Eating Disorders** (Disturbed eating behaviors)
    * **Restrictive/Compensatory:** Anorexia, Bulimia, Binge-Eating.

    **7. Neurodevelopmental Disorders** (Childhood-onset)
    * **ADHD:** Attention-Deficit/Hyperactivity Disorder.
    * **Autism:** Autism Spectrum Disorder (ASD).

    **8. Schizophrenia Spectrum** (Loss of contact with reality)
    * **Psychotic Disorders:** Schizophrenia, Schizoaffective, Delusional.

    **9. Trauma & Stressor-Related** (Triggered by trauma/stress)
    * **PTSD Spectrum:** Post-Traumatic Stress Disorder (PTSD), Adjustment Disorder.

    **10. Substance-Related & Addictive Disorders**
    * **Substance Use:** Alcohol Use Disorder, Cannabis Use Disorder.
    """)

    st.divider()
    if st.button("✅ I have read the definitions and I'm ready to start", type="primary"):
        st.session_state.agreed = True
        st.rerun()

# --- PAGE 2: THE SURVEY ---
else:
    df_questions = pd.read_csv(CSV_FILE)
    df_questions['id'] = df_questions['id'].astype(str)
    df_questions = df_questions.dropna(subset=['id'])
    
    remaining_df = df_questions[~df_questions['id'].isin(st.session_state.answered_ids)]

    st.title(f"📋 Mental Health Survey (Batch {BATCH_NUMBER})")

    # Sidebar Progress (Forced 600)
    total_fixed = 600
    done = len(st.session_state.answered_ids)
    st.sidebar.write(f"**Progress: {done} / {total_fixed}**")
    st.sidebar.progress(min(done / total_fixed, 1.0))
    if st.sidebar.button("📖 Review Instructions"):
        st.session_state.agreed = False
        st.rerun()

    if remaining_df.empty:
        st.balloons()
        st.success("🎉 Batch Complete!")
    else:
        current_row = remaining_df.iloc[0]
        
        # --- THE TRANSLATION SHIELD ---
        # Forces browser to skip translating this div, stopping "half-half" bugs and crashes
        st.markdown('<div class="notranslate" translate="no">', unsafe_allow_html=True)
        
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

        # --- END SHIELD ---
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Submit & Next ➡️", type="primary"):
            if not user_input:
                st.error("Please enter your name!")
            else:
                success = False
                with st.spinner("Saving to Google Sheets..."):
                    for attempt in range(5):
                        try:
                            worksheet = get_worksheet()
                            new_data = [str(current_row['id']), current_row['Title'], current_row['Body'], cat, sub, dis, user_input]
                            worksheet.append_row(new_data)
                            st.session_state.answered_ids.append(str(current_row['id']))
                            success = True
                            break
                        except:
                            time.sleep((attempt + 1) * 2) 
                
                if success:
                    st.success("Saved!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Google is busy. Wait 15s and try again.")
