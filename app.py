import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
BATCH_NUMBER = 1 
CSV_FILE = f'survey_batch_{BATCH_NUMBER}.csv'
SHEET_NAME = 'Survey_Results_Master'
TAB_NAME = f'Results_{BATCH_NUMBER}'

# --- GOOGLE SHEETS SETUP ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# Load credentials from your JSON file
creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
client = gspread.authorize(creds)

# Open the spreadsheet and the specific tab
sh = client.open(SHEET_NAME)
worksheet = sh.worksheet(TAB_NAME)

# --- LOAD DATA ---
df_questions = pd.read_csv(CSV_FILE)

# Get already answered IDs from Google Sheets to prevent duplicates
existing_records = worksheet.get_all_records()
if existing_records:
    existing_df = pd.DataFrame(existing_records)
    answered_ids = existing_df['id'].astype(str).tolist()
else:
    answered_ids = []

# Find rows that haven't been answered yet
remaining_df = df_questions[~df_questions['id'].astype(str).isin(answered_ids)]

st.title(f"📋 Mental Health Labeling Survey (Batch {BATCH_NUMBER})")

if remaining_df.empty:
    st.balloons()
    st.success(f"🎉 All {len(df_questions)} rows in this batch are completed! You're a hero!")
else:
    # Get the current row
    current_row = remaining_df.iloc[0]
    
    with st.container(border=True):
        st.subheader(f"Case ID: {current_row['id']}")
        st.markdown(f"**Title:** {current_row['Title']}")
        st.write(f"**Body:** {current_row['Body']}")

    st.divider()
    st.write("### Select the most accurate labels:")

    # User Input for Name
    user_name = st.text_input("Enter your name:", placeholder="Who is helping today?")

    # Create 3 columns for the 3 questions
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
            # Prepare the row to append
            new_row = [
                str(current_row['id']),
                current_row['Title'],
                current_row['Body'],
                selected_cat,
                selected_sub,
                selected_dis,
                user_name
            ]
            
            # Append to Google Sheets
            worksheet.append_row(new_row)
            st.success("Saved! Loading next case...")
            st.rerun()

# Sidebar Progress
total = len(df_questions)
done = len(answered_ids)
st.sidebar.write(f"**Batch Progress: {done} / {total}**")
st.sidebar.progress(done / total)