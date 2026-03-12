import streamlit as st
import pandas as pd
import gspread
import time
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
BATCH_NUMBER = 1  # <--- CHANGE THIS FOR EACH APP (2, 3, 4, 5)
CSV_FILE = f'survey_batch_new_{BATCH_NUMBER}.csv'
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
    # Wrap everything in a translation shield to prevent crashes
    st.markdown('<div class="notranslate" translate="no">', unsafe_allow_html=True)
    
    st.title("📋 Annotation Instructions & Guidelines")
    
    with st.expander("⚙️ Technical Rules (Click to expand)", expanded=True):
        st.markdown("""
        - **Unique Identity:** In the 'Enter your name:' section, use a consistent ID (e.g., fahim_istiak). Use this same ID for all 600 rows.
        - **Input Persistence:** Your name is saved as you work. If the app times out or you refresh (F5), you must re-enter your name.
        - **Auto-Save & Resume:** Progress saves instantly on "Submit." The app resumes where you left off if you close the browser.
        - **Ownership:** This link is for you only. Do not share it to avoid data conflicts.
        - **Submission:** Click "Submit & Next ➡️" to save and load the next case.
        """)

    st.markdown("### 🧠 DSM-5 Data Quality & Labeling Guide")
    
    st.markdown("#### **Categories:**")
    st.markdown("""
    - **Personality Disorders** (Long-term patterns of thinking and behaving that are very different from what society expects and can cause problems in relationships and daily life.)
    - **Mood Disorders** (Conditions that mainly affect a person’s emotional state, such as feeling extremely sad or having unusual mood changes.)
    - **Anxiety Disorders** (Disorders where a person feels excessive fear, worry, or nervousness that interferes with daily activities.)
    - **Sleep Disorders** (Problems related to sleeping, such as difficulty falling asleep, staying asleep, or having poor sleep quality.)
    - **Obsessive-Compulsive & Related Disorders** (Conditions involving unwanted repetitive thoughts and behaviors that a person feels driven to perform.)
    - **Eating Disorders** (Serious conditions involving unhealthy eating habits and strong concerns about body weight or shape.)
    - **Neurodevelopmental Disorders** (Conditions that begin in childhood and affect brain development, learning, behavior, or social skills.)
    - **Schizophrenia Spectrum & Psychotic Disorders** (Disorders that affect how a person thinks and perceives reality, sometimes causing hallucinations or delusions.)
    - **Trauma & Stressor-Related Disorders** (Conditions that develop after experiencing or witnessing very stressful or traumatic events.)
    - **Substance-Related & Addictive Disorders** (Problems caused by the harmful use of substances like alcohol or drugs, or addiction to certain behaviors.)
    """)

    st.markdown("#### **Sub Categories:**")
    st.markdown("""
    - **Bipolar Disorders** (Conditions involving extreme mood swings between high energy or mania and deep depression.)
    - **Insomnia Spectrum** (Sleep-related conditions where a person has ongoing difficulty falling asleep, staying asleep, or getting restful sleep.)
    - **Depressive Disorders** (Conditions characterized by long-lasting sadness, low motivation, and loss of interest in daily activities.)
    - **Cluster A – Odd/Eccentric** (Personality patterns where people may appear unusual, suspicious, or socially distant.)
    - **OCD Spectrum** (Conditions involving intrusive thoughts and repetitive behaviors that a person feels compelled to perform.)
    - **Restrictive/Compensatory Disorders** (Eating-related conditions where people severely restrict food or use unhealthy methods to control weight.)
    - **Cluster C – Anxious/Fearful** (Personality patterns marked by strong anxiety, fear of criticism, or dependence on others.)
    - **Cluster B – Dramatic/Emotional** (Personality patterns involving intense emotions, impulsive behavior, and unstable relationships.)
    - **Phobias** (Strong and irrational fears of specific objects, situations, or activities.)
    - **Panic Disorders** (Conditions where a person experiences sudden and repeated panic attacks with intense fear and physical symptoms.)
    - **Psychotic Disorders** (Serious conditions where a person may lose touch with reality, such as experiencing hallucinations or delusions.)
    - **PTSD Spectrum** (Conditions that develop after experiencing or witnessing traumatic events and can cause distressing memories and anxiety.)
    - **ADHD** (A condition affecting attention, impulse control, and activity levels, often starting in childhood.)
    - **Generalized Anxiety Disorder** (A condition involving constant and excessive worry about everyday situations.)
    - **Substance Use Disorders** (Conditions where the repeated use of drugs or alcohol leads to dependence and problems in daily life.)
    - **Autism Spectrum Disorders** (Neurodevelopmental conditions affecting communication, social interaction, and behavior patterns.)
    """)

    st.markdown("#### **Specific Disorders:**")
    st.markdown("""
    - **Bipolar 1 Disorder** (A mood disorder with severe manic episodes and often periods of depression.)
    - **Panic Disorder** (A condition where a person experiences sudden and repeated panic attacks with intense fear.)
    - **Attention-Deficit/Hyperactivity Disorder (ADHD)** (A condition involving difficulty with attention, impulsivity, and hyperactivity.)
    - **Schizoid Personality Disorder** (A personality pattern where a person prefers being alone and shows little interest in social relationships.)
    - **Obsessive-Compulsive Personality Disorder** (A personality condition marked by extreme perfectionism, control, and rigid rules.)
    - **Generalized Anxiety Disorder (GAD)** (A condition involving constant and excessive worry about everyday life.)
    - **Post-Traumatic Stress Disorder (PTSD)** (A condition that develops after experiencing or witnessing a traumatic event.)
    - **Insomnia** (A sleep disorder where a person has ongoing difficulty falling or staying asleep.)
    - **Persistent Depressive Disorder (Dysthymia)** (A long-lasting form of depression with ongoing low mood.)
    - **Schizotypal Personality Disorder** (A personality pattern involving unusual thinking, beliefs, and social discomfort.)
    - **Social Anxiety Disorder** (A condition where a person has intense fear of social situations and being judged by others.)
    - **Anorexia Nervosa** (An eating disorder where a person severely restricts food due to fear of gaining weight.)
    - **Major Depressive Disorder** (A serious condition involving persistent sadness and loss of interest in activities.)
    - **Cyclothymic Disorder** (A mood disorder with frequent mood swings between mild highs and lows.)
    - **Agoraphobia** (A fear of places or situations where escape may feel difficult or help may not be available.)
    - **Body Dysmorphic Disorder** (A condition where a person becomes overly focused on perceived flaws in their appearance.)
    - **Autism Spectrum Disorder (ASD)** (A developmental condition affecting communication, behavior, and social interaction.)
    - **Bipolar 2 Disorder** (A mood disorder with depressive episodes and milder manic episodes called hypomania.)
    - **Binge-Eating Disorder** (An eating disorder involving frequent episodes of eating large amounts of food uncontrollably.)
    - **Narcissistic Personality Disorder** (A personality condition involving an inflated sense of self-importance and need for admiration.)
    - **Seasonal Affective Disorder** (A type of depression that occurs during certain seasons, usually in winter.)
    - **Obsessive-Compulsive Disorder** (A disorder with intrusive thoughts and repetitive behaviors done to reduce anxiety.)
    - **Sleep Apnea** (A sleep disorder where breathing repeatedly stops and starts during sleep.)
    - **Narcolepsy** (A sleep disorder causing excessive daytime sleepiness and sudden sleep attacks.)
    - **Antisocial Personality Disorder** (A personality pattern involving disregard for rules, laws, and the rights of others.)
    - **Avoidant Personality Disorder** (A personality condition involving extreme fear of rejection and social avoidance.)
    - **Hoarding Disorder** (A condition where a person has difficulty discarding possessions, leading to clutter.)
    - **Schizoaffective Disorder** (A condition combining symptoms of schizophrenia with mood disorder symptoms.)
    - **Alcohol Use Disorder** (A condition where a person has difficulty controlling alcohol use despite negative effects.)
    - **Restless Legs Syndrome** (A condition causing uncomfortable sensations in the legs and an urge to move them, especially at night.)
    - **Bulimia Nervosa** (An eating disorder involving binge eating followed by behaviors like vomiting or excessive exercise.)
    - **Schizophrenia** (A serious mental disorder affecting thinking, perception, and behavior.)
    - **Dependent Personality Disorder** (A personality condition where a person feels a strong need to rely on others for decisions and support.)
    - **Histrionic Personality Disorder** (A personality pattern involving excessive attention-seeking and emotional expression.)
    - **Paranoid Personality Disorder** (A personality condition involving strong distrust and suspicion of others.)
    - **Cannabis Use Disorder** (A condition where frequent cannabis use leads to dependence and life problems.)
    - **Delusional Disorder** (A condition where a person strongly believes things that are not based in reality.)
    - **Adjustment Disorder** (A condition where a person has difficulty coping with a stressful life change or event.)
    """)

    st.markdown('</div>', unsafe_allow_html=True)
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
            cat = st.radio("Step 1: Category?", [current_row['Category'], current_row['Category_2'], current_row['Category_3'], current_row['Category_4'], current_row['Category_5']], key="cat")
        with col2:
            sub = st.radio("Step 2: Subcategory?", [current_row['Subcategory'], current_row['Subcategory_2'], current_row['Subcategory_3'], current_row['Subcategory_4'], current_row['Subcategory_5']], key="sub")
        with col3:
            dis = st.radio("Step 3: Disorder?", [current_row['SpecificDisorder'], current_row['SpecificDisorder_2'], current_row['SpecificDisorder_3'], current_row['SpecificDisorder_4'], current_row['SpecificDisorder_5']], key="dis")

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
