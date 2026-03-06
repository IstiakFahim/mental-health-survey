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
        - **Persistence:** If you refresh or the app times out, you must re-enter your name.
        - **Auto-Save:** Progress is saved instantly. You can close the browser and resume later.
        - **Ownership:** This link is yours alone. Do not share it.
        """)

    st.markdown("### 🧠 DSM-5 Data Quality & Labeling Guide")
    st.write("Please read the following definitions to ensure accurate labeling according to the DSM-5 hierarchy:")

    # High-quality descriptive list
    st.markdown("""
    **1. Mood Disorders** (Disturbances in emotional state)
    * **Bipolar Disorders:** Fluctuations between extreme highs (mania) and lows (depression).
        * *Includes: Bipolar 1, Bipolar 2, Cyclothymic.*
    * **Depressive Disorders:** Persistent feelings of sadness, emptiness, or loss of interest.
        * *Includes: Major Depressive, Dysthymia, Seasonal Affective.*

    **2. Personality Disorders** (Long-term, rigid patterns of thinking and behaving)
    * **Cluster A:** Odd or eccentric behaviors (Paranoid, Schizoid, Schizotypal).
    * **Cluster B:** Dramatic, emotional, or erratic behaviors (Antisocial, Histrionic, Narcissistic).
    * **Cluster C:** Anxious or fearful behaviors (Avoidant, Dependent, Obsessive-Compulsive Personality).

    **3. Anxiety Disorders** (Excessive fear, worry, or dread)
    * **Panic & Phobias:** Intense episodes of fear or specific triggers (Panic Disorder, Agoraphobia, Social Anxiety).
    * **Generalized Anxiety (GAD):** Persistent, non-stop worry about various daily activities.

    **4. Sleep Disorders** (Issues with the quality, timing, or amount of sleep)
    * **Insomnia Spectrum:** Constant difficulty falling or staying asleep.
    * **Other Conditions:** Narcolepsy (sudden sleep), Sleep Apnea (breathing issues), Restless Legs.

    **5. OCD & Related Disorders** (Repetitive thoughts and "checking" behaviors)
    * **Obsessions & Compulsions:** Unwanted rituals to reduce anxiety (OCD, Body Dysmorphia, Hoarding).

    **6. Eating Disorders** (Abnormal or disturbed eating habits)
    * **Weight & Food Issues:** Extreme restriction of food or loss of control over eating (Anorexia, Bulimia, Binge-Eating).

    **7. Neurodevelopmental Disorders** (Conditions that begin in childhood)
    * **ADHD:** Problems with focus, sitting still, or acting without thinking.
    * **Autism (ASD):** Challenges with social communication and repetitive behaviors.

    **8. Schizophrenia Spectrum** (Loss of contact with reality)
    * **Psychotic Disorders:** Experiencing hallucinations (seeing/hearing things) or delusions (false beliefs).
        * *Includes: Schizophrenia, Schizoaffective, Delusional Disorder.*

    **9. Trauma & Stressor-Related** (Results from a stressful or traumatic life event)
    * **PTSD & Adjustment:** Long-term trauma symptoms or difficulty coping with major life changes.

    **10. Substance-Related** (Problems related to the use of drugs or alcohol)
    * **Addictive Disorders:** Compulsive use of substances despite negative consequences (Alcohol, Cannabis).
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

    # Sidebar
    total = len(df_questions)
    done = len(st.session_state.answered_ids)
    st.sidebar.write(f"**Progress: {done} / {total}**")
    st.sidebar.progress(done / total)
    if st.sidebar.button("📖 Read Instructions Again"):
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
