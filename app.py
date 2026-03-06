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
        1. **Unique Identity:** In the **'Enter your name:'** section, use a consistent ID (e.g., `fahim_istiak`). Use this same ID for all 600 rows.
        2. **Input Persistence:** Your name is saved as you work. If the app **times out** or you **refresh (F5)**, you must re-enter your name.
        3. **Auto-Save & Resume:** Progress saves instantly on "Submit." The app resumes where you left off if you close the browser.
        4. **Ownership:** This link is for **you only**. Do not share it to avoid data conflicts.
        5. **Submission:** Click **"Submit & Next ➡️"** to save and load the next case.
        """)

    st.markdown("### 🧠 DSM-5 Data Quality & Labeling Guide")
    st.write("Please read the definitions below. You must categorize each text using this hierarchy:")

    # --- COMPLETE HIERARCHICAL LIST (All 10 Categories, 16 Subcategories, 38 Disorders) ---
    st.markdown("""
**1. Mood Disorders** *(Conditions affecting emotional state)*  
* **Bipolar Disorders:** Extreme swings between high energy (mania) and low mood.  
    * *Includes: Bipolar I Disorder, Bipolar II Disorder, Cyclothymic Disorder.*  
* **Depressive Disorders:** Intense, long-lasting sadness or loss of interest.  
    * *Includes: Major Depressive Disorder, Persistent Depressive Disorder (Dysthymia), Seasonal Affective Disorder.*

---

**2. Personality Disorders** *(Long-term rigid behavior patterns)*  
* **Cluster A – Odd/Eccentric:** Social withdrawal and distorted thinking.  
    * *Includes: Paranoid Personality Disorder, Schizoid Personality Disorder, Schizotypal Personality Disorder.*  
* **Cluster B – Dramatic/Emotional:** Intense emotions and impulsive behavior.  
    * *Includes: Antisocial Personality Disorder, Histrionic Personality Disorder, Narcissistic Personality Disorder.*  
* **Cluster C – Anxious/Fearful:** High anxiety and perfectionistic traits.  
    * *Includes: Avoidant Personality Disorder, Dependent Personality Disorder, Obsessive-Compulsive Personality Disorder.*

---

**3. Anxiety Disorders** *(Persistent fear or excessive worry)*  
* **Phobias:** Fear of specific objects or social situations.  
    * *Includes: Social Anxiety Disorder, Agoraphobia.*  
* **Panic Disorders:** Sudden, intense episodes of terror.  
    * *Includes: Panic Disorder.*  
* **Generalized Anxiety:** Chronic worry about everyday life.  
    * *Includes: Generalized Anxiety Disorder (GAD).*

---

**4. Sleep Disorders** *(Problems with sleep quality or timing)*  
* **Insomnia Spectrum:** Difficulty falling or staying asleep.  
    * *Includes: Insomnia Disorder.*  
* **Other Sleep Issues:** Physical or neurological sleep disruptions.  
    * *Includes: Narcolepsy, Sleep Apnea, Restless Legs Syndrome.*

---

**5. OCD & Related Disorders** *(Repetitive thoughts and behaviors)*  
* **OCD Spectrum:** Unwanted thoughts and repetitive rituals to reduce anxiety.  
    * *Includes: Obsessive-Compulsive Disorder, Body Dysmorphic Disorder, Hoarding Disorder.*

---

**6. Eating Disorders** *(Serious disturbances in eating behavior)*  
* **Restrictive/Compensatory Eating Patterns:** Extreme restriction or binge-purge behavior.  
    * *Includes: Anorexia Nervosa, Bulimia Nervosa, Binge-Eating Disorder.*

---

**7. Neurodevelopmental Disorders** *(Conditions appearing in early childhood)*  
* **ADHD:** Problems with attention, hyperactivity, and impulsivity.  
* **Autism Spectrum Disorders:** Difficulty with social communication and repetitive behaviors.  
    * *Includes: Autism Spectrum Disorder (ASD).*

---

**8. Schizophrenia Spectrum** *(Break from reality)*  
* **Psychotic Disorders:** Hallucinations or delusions.  
    * *Includes: Schizophrenia, Schizoaffective Disorder, Delusional Disorder.*

---

**9. Trauma & Stressor-Related Disorders** *(Triggered by traumatic experiences)*  
* **PTSD Spectrum:** Emotional distress following trauma or major life events.  
    * *Includes: Post-Traumatic Stress Disorder (PTSD), Adjustment Disorder.*

---

**10. Substance-Related & Addictive Disorders**  
* **Substance Use Disorders:** Compulsive use of substances despite harmful consequences.  
    * *Includes: Alcohol Use Disorder, Cannabis Use Disorder.*
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
                with st.spinner("Saving to Google Sheets..."):
                    # TRY 5 TIMES TO BEAT THE "API BUSY" ERROR
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
                    st.error("Google is busy. Please wait 15 seconds and try again.")


