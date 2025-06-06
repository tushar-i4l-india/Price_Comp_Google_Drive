import streamlit as st
import pandas as pd
from datetime import date, timedelta
from io import BytesIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
import plotly.express as px
import os
import json
import base64
import re
import glob
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

# --- GOOGLE DRIVE AUTHENTICATION USING ENV VARIABLE ---
SERVICE_ACCOUNT_JSON = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
creds = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_JSON,
    scopes=["https://www.googleapis.com/auth/drive.readonly"]
)
drive_service = build('drive', 'v3', credentials=creds)

# --- HELPER FUNCTION: Get Folder ID by Name ---
def get_folder_id(folder_name):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    folders = results.get('files', [])
    if not folders:
        return None
    return folders[0]['id']

# --- HELPER FUNCTION: Get File ID by Name in Folder ---
def get_file_id_in_folder(folder_id, file_name):
    query = f"'{folder_id}' in parents and name = '{file_name}'"
    results = drive_service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    files = results.get('files', [])
    if not files:
        return None
    return files[0]['id']

@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df

# --- Extract Price from the Price String ---
def extract_price(price):
    if isinstance(price, str):
        if "price not found" in price.lower() or "no link" in price.lower() or price.lower().startswith("error:"):
            return None
        match = re.search(r"[\d,.]+", price)
        if match:
            return round(float(match.group().replace(",", "")), 2)
    return None

# --- STREAMLIT UI ---
st.set_page_config(page_title="Competitor Price Comparison Dashboard", layout="wide", menu_items={'Get Help': 'https://insulation4less.co.uk/pages/contact-us',
    'Report a bug': "https://www.insulation4less.co.uk",
    'About': "This app is a price comparison dashboard"})
# Initialize session state
if 'selected_brand' not in st.session_state:
    st.session_state.selected_brand = None
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

st.title("📁 Price Comp Dashboard (Google Drive)")
col1, col2 = st.columns(2)
with col1:
    brands = ["Celotex", "Recticel"]
    st.session_state.selected_brand = st.selectbox("Select Brand", brands)

preview_button = st.button("Preview Data")
if st.session_state.selected_brand:
    
    with col2:
        selected_date = st.date_input("Select Date", value=date.today())
        st.session_state.selected_date = selected_date.strftime("%d-%m-%Y")
    if st.session_state.selected_date:
        expected_file_name = f"{st.session_state.selected_brand}_Prices_{st.session_state.selected_date}.xlsx"
        if preview_button or st.session_state.data_loaded:
            st.session_state.data_loaded = True
            st.write(f"Looking for file: `{expected_file_name}` in `{st.session_state.selected_brand}` folder...")
            folder_id = get_folder_id(st.session_state.selected_brand)
            if folder_id:
                file_id = get_file_id_in_folder(folder_id, expected_file_name)
                if file_id:
                    # Download file
                    request = drive_service.files().get_media(fileId=file_id)
                    file_data = BytesIO()
                    downloader = request.execute()
                    file_data.write(downloader)
                    file_data.seek(0)
                    df = load_data(file_data)
                    # st.session_state.df = df
                    st.success(f"Successfully loaded: {expected_file_name}")
                    st.dataframe(df)
                    # --- Product Selection for charts ----
                    products = df["Product"].unique()
                    st.session_state.selected_product = st.selectbox("Select Product", products)
                    if st.session_state.selected_product:
                        product_data = df[df["Product"] == st.session_state.selected_product]
                        if not product_data.empty:
                            melted_data = product_data.melt(id_vars=["Product", "SKU"], var_name="Competitor", value_name="Price")
                            for column in melted_data.columns:
                                if 'Price' in column:
                                    melted_data[column] = melted_data[column].astype(str).apply(extract_price)
                            melted_data = melted_data.dropna(subset=["Price"])
                            melted_data.sort_values(by="Price", ascending=True, inplace=True)
                            st.write(f"Showing price comparison for `{st.session_state.selected_product}`:")
                            fig = px.bar(
                                melted_data,
                                x="Competitor",
                                y="Price",
                                color="Competitor",
                                title=f"Price Comparison for {st.session_state.selected_product}",
                                text="Price"
                            )
                            st.plotly_chart(fig)

                else:
                    st.error("File not found for the selected date.")
            else:
                st.error(f"{st.session_state.selected_brand} folder not found in Google Drive")
    
    