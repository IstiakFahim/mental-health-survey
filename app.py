import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
BATCH_NUMBER = 1  # <--- CHANGE THIS TO 2, 3, 4, or 5 FOR THE OTHER APPS

CSV_FILE = f'survey_batch_{BATCH_NUMBER}.csv'
SHEET_NAME = f'Survey_Results_Batch_{BATCH_NUMBER}'
TAB_NAME = 'Result' # Matches the tab name you just created

# --- GOOGLE SHEETS SETUP ---
@st.cache_resource
def get_gspread_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return gspread.authorize(creds)

client = get_gspread_client()

# Open the specific spreadsheet for this batch
sh = client.open(SHEET_NAME)
worksheet = sh.worksheet(TAB_NAME)

# --- LOAD DATA ---
df_questions = pd.read_csv(CSV_FILE)

# Get already answered IDs from Google Sheets to prevent duplicates
existing_records = worksheet.get_all_records()
if existing_records:
    existing_df = pd.DataFrame(existing_records)
    if 'id' in existing_df.columns:
        answered_ids = existing_df['id'].astype(str).tolist()
    else:
        answered_ids = []
else:
    answered_ids = []

# Find rows that haven't been answered yet
remaining_df = df_questions[~df_questions['id'].astype(str).isin(answered_ids)]

st.title(f"📋 Mental Health Labeling Survey (Batch {BATCH_NUMBER})")

if remaining_df.empty:
    st.balloons()
    st.success(f"🎉 All {len(df_questions)} rows in Batch {BATCH_NUMBER} are completed!")
else:
    current_row = remaining_df.iloc[0]
    
    with st.container(border=True):
        st.subheader(f"Case ID: {current_row['id']}")
        st.markdown(f"**Title:** {current_row['Title']}")
        st.write(f"**Body:** {current_row['Body']}")

    st.divider()
    st.write("### Select the most accurate labels:")

    user_name = st.text_input("Enter your name (e.g., fahim_istiak):", placeholder="Your unique ID")

    col1, col2, col3 = st.columns(3)

    with col1:
        cat_options = [current_row['Category'], current_row['Category_2'], current_row['Category_3']]
        selected_cat = st.radio("Best Category?", cat_options, key="cat")

    with col2:
        sub_options = [current_row['Subcategory'], current_row['Subcategory_2'], current_row['Subcategory_3']]
        selected_sub = st.radio("Best Subcategory?", sub_options, key="sub")

    with col3:
        dis_options = [current_row['SpecificDisorder'], current_row['SpecificDisorder_2'], current_row['SpecificDisorder_3']]
        selected_dis = st.radio("Best Disorder?", dis_options, key="dis")

    if st.button("Submit & Next ➡️", type="primary"):
        if not user_name:
            st.error("Please enter your name before submitting!")
        else:
            new_row = [
                str(current_row['id']),
                current_row['Title'],
                current_row['Body'],
                selected_cat,
                selected_sub,
                selected_dis,
                user_name
            ]
            worksheet.append_row(new_row)
            st.success("Saved!")
            st.rerun()

# Sidebar Progress
total = len(df_questions)
done = len(answered_ids)
st.sidebar.write(f"**Batch {BATCH_NUMBER} Progress: {done} / {total}**")
st.sidebar.progress(done / total)
