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

# --- PAGE 1: INSTRUCTIONS ---
if not st.session_state.agreed:
    st.title("📋 Annotation Instructions & Guidelines")
    
    with st.expander("⚙️ Technical Rules", expanded=True):
        st.markdown("- **Identity:** Use a consistent ID. \n- **Persistence:** Re-enter name if you refresh.\n- **Auto-Save:** Saves on 'Submit'.")

    st.markdown("### 🧠 DSM-5 Labeling Guide")
    st.markdown("""
    **1. Mood Disorders:** Bipolar (1, 2, Cyclothymic), Depressive (Major, Dysthymia, Seasonal).
    **2. Personality Disorders:** Cluster A (Odd), Cluster B (Dramatic), Cluster C (Anxious).
    **3. Anxiety Disorders:** Phobias, Panic, Generalized Anxiety (GAD).
    **4. Sleep Disorders:** Insomnia, Narcolepsy, Apnea, Restless Legs.
    **5. OCD & Related:** OCD, Body Dysmorphia, Hoarding.
    **6. Eating Disorders:** Anorexia, Bulimia, Binge-Eating.
    **7. Neurodevelopmental:** ADHD, Autism (ASD).
    **8. Schizophrenia & Psychotic:** Schizophrenia, Schizoaffective, Delusional.
    **9. Trauma & Stressor:** PTSD, Adjustment Disorder.
    **10. Substance-Related:** Alcohol, Cannabis.
    """)

    st.divider()
    if st.button("✅ I Agree & Start", type="primary"):
        st.session_state.agreed = True
        st.rerun()

# --- PAGE 2: THE SURVEY (Translation-Protected) ---
else:
    df_questions = pd.read_csv(CSV_FILE)
    df_questions['id'] = df_questions['id'].astype(str)
    df_questions = df_questions.dropna(subset=['id'])
    remaining_df = df_questions[~df_questions['id'].isin(st.session_state.answered_ids)]

    st.title(f"📋 Mental Health Survey (Batch {BATCH_NUMBER})")

    # Sidebar Progress (Fixed at 600)
    total_expected = 600
    done = len(st.session_state.answered_ids)
    st.sidebar.write(f"**Progress: {done} / {total_expected}**")
    st.sidebar.progress(min(done / total_expected, 1.0))
    if st.sidebar.button("📖 Review Instructions"):
        st.session_state.agreed = False
        st.rerun()

    if remaining_df.empty:
        st.balloons()
        st.success("🎉 Batch Complete!")
    else:
        current_row = remaining_df.iloc[0]
        
        # BLOCK TRANSLATION HERE TO PREVENT REMOVECHILD ERROR
        st.markdown('<div translate="no">', unsafe_allow_html=True)
        
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

        st.markdown('</div>', unsafe_allow_html=True) # Close protection div

        if st.button("Submit & Next ➡️", type="primary"):
            if not user_input:
                st.error("Please enter your name!")
            else:
                success = False
                with st.spinner("Saving..."):
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
                    st.error("Google is busy. Wait 15s and retry.")
