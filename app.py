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
    
    st.info("### ⚙️ Technical Instructions")
    st.markdown("""
    1. **Unique Identity:** In the **'Enter your name:'** section, use a consistent ID (e.g., `fahim_istiak`). Use this same ID for all 600 rows.
    2. **Input Persistence:** Your name is saved as you work. If the app **times out** or you **refresh (F5)**, you must re-enter your name.
    3. **Auto-Save & Resume:** Progress saves instantly on "Submit." The app resumes where you left off if you close the browser.
    4. **Ownership:** This link is for **you only**. Do not share it to avoid data conflicts.
    5. **Submission:** Click **"Submit & Next ➡️"** to save and load the next case.
    """)

    st.warning("### 🧠 DSM-5 Data Quality & Labeling Guide")
    st.markdown("""
    Please read each text carefully. You must select the Category, Subcategory, and Specific Disorder that best fits the primary issue described. **According to the DSM-5 manual, the mental health conditions follow this hierarchy:**

    * **1. Mood Disorders:** Bipolar (1, 2, Cyclothymic) and Depressive (Major, Dysthymia, Seasonal).
    * **2. Personality Disorders:** Cluster A (Odd), Cluster B (Dramatic), Cluster C (Anxious/Perfectionism).
    * **3. Anxiety Disorders:** Panic, Phobias, and Generalized Anxiety (GAD).
    * **4. Sleep Disorders:** Insomnia, Narcolepsy, Apnea, Restless Legs.
    * **5. OCD & Related:** OCD (Rituals), Body Dysmorphia, Hoarding.
    * **6. Eating Disorders:** Anorexia, Bulimia, Binge-Eating.
    * **7. Neurodevelopmental:** ADHD and Autism (ASD).
    * **8. Schizophrenia & Psychotic:** Schizophrenia, Schizoaffective, Delusional Disorder.
    * **9. Trauma & Stressor:** PTSD and Adjustment Disorder.
    * **10. Substance-Related:** Alcohol and Cannabis Use Disorders.
    """)

    st.write("---")
    if st.button("I have read the instructions and I agree to start", type="primary"):
        st.session_state.agreed = True
        st.rerun()

# --- PAGE 2: THE SURVEY ---
else:
    df_questions = pd.read_csv(CSV_FILE)
    remaining_df = df_questions[~df_questions['id'].astype(str).isin(st.session_state.answered_ids)]

    st.title(f"📋 Mental Health Survey (Batch {BATCH_NUMBER})")

    # Sidebar
    total = len(df_questions)
    done = len(st.session_state.answered_ids)
    st.sidebar.write(f"**Progress: {done} / {total}**")
    st.sidebar.progress(done / total)
    if st.sidebar.button("Show Instructions Again"):
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
            cat = st.radio("Category?", [current_row['Category'], current_row['Category_2'], current_row['Category_3']], key="cat")
        with col2:
            sub = st.radio("Subcategory?", [current_row['Subcategory'], current_row['Subcategory_2'], current_row['Subcategory_3']], key="sub")
        with col3:
            dis = st.radio("Disorder?", [current_row['SpecificDisorder'], current_row['SpecificDisorder_2'], current_row['SpecificDisorder_3']], key="dis")

        if st.button("Submit & Next ➡️", type="primary"):
            if not user_input:
                st.error("Please enter your name!")
            else:
                worksheet = get_worksheet()
                if worksheet:
                    new_data = [str(current_row['id']), current_row['Title'], current_row['Body'], cat, sub, dis, user_input]
                    try:
                        worksheet.append_row(new_data)
                        st.session_state.answered_ids.append(str(current_row['id']))
                        st.success("Saved!")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Google API is busy. Wait 10s and try again.")
