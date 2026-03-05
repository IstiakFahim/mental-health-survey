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

# --- GOOGLE SHEETS SETUP (With Retry Logic) ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

def get_worksheet():
    client = get_gspread_client()
    # Simple retry logic: if Google is busy, wait and try again
    for i in range(3): 
        try:
            sh = client.open(SHEET_NAME)
            return sh.worksheet(TAB_NAME)
        except:
            time.sleep(2)
    return None

# --- INITIALIZE SESSION STATE ---
# This keeps track of what's done in the app's memory to avoid hitting Google too much
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

# --- LOAD CSV ---
df_questions = pd.read_csv(CSV_FILE)
remaining_df = df_questions[~df_questions['id'].astype(str).isin(st.session_state.answered_ids)]

st.title(f"📋 Mental Health Survey (Batch {BATCH_NUMBER})")

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
    
    # Preserve the name input between submits
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
                
                # Try to write to Google
                try:
                    worksheet.append_row(new_data)
                    # Update memory so we don't have to read from Google again
                    st.session_state.answered_ids.append(str(current_row['id']))
                    st.success("Saved!")
                    time.sleep(0.5) # Small pause to let Google breathe
                    st.rerun()
                except Exception as e:
                    st.error("Google API is rate-limiting us. Please wait 10 seconds and try again.")

# Sidebar
total = len(df_questions)
done = len(st.session_state.answered_ids)
st.sidebar.write(f"**Progress: {done} / {total}**")
st.sidebar.progress(done / total)
