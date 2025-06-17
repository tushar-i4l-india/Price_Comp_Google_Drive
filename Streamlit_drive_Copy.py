import streamlit as st 
import pandas as pd 
import os
import plotly.express as px  
from datetime import date, timedelta
import re
import glob
import streamlit.components.v1 as components 
from google.oauth2 import service_account
from googleapiclient.discovery import build
import ast
import json
from io import BytesIO

st.set_page_config(page_title="Price Comparison Dashboard", page_icon=":bar_chart:", layout="wide", menu_items={
    'Get Help': 'https://insulation4less.co.uk/pages/contact-us',
    'Report a bug': "https://www.insulation4less.co.uk",
    'About': "This app is a price comparison dashboard",
})

# --- CONFIGURATION ---
raw_secret = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_JSON = json.loads(ast.literal_eval(f"'''{raw_secret}'''"))
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

def extract_price(price):
    if isinstance(price, str):
        if "price not found" in price.lower() or "no link" in price.lower() or price.lower().startswith("error:"):
            return None
        match = re.search(r"[\d,.]+", price)
        if match:
            return round(float(match.group().replace(",", "")), 2)
        
    return None

def highlight_changes(row):
    styles = []
    for col in website_columns:
        today_price = extract_price(row[col])
        prev_col = col + "_yesterday"

        prev_price_str = df_merged.loc[row.name, prev_col] if prev_col in df_merged.columns else None
        prev_price = extract_price(prev_price_str)

        style = ""
        if today_price is not None and prev_price is not None:
            if today_price > prev_price:
                style = "color: red; font-weight: bold;"
            elif today_price < prev_price:
                style = "color: green; font-weight: bold;"
            elif today_price == prev_price:
                style = "color: blue; font-weight: bold;"
        styles.append(style)
    return styles

if 'selected_brand' not in st.session_state:
    st.session_state.selected_brand = None
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'previous_date_str' not in st.session_state:
    st.session_state.previous_date_str = None

st.sidebar.title("Price Comparison Dashboard 💷")

brands = ["Celotex", "Recticel", "Ecotherm", "Unilin","Core-Products", "Cladco", "Novia", "Powerlon"]
st.session_state.selected_brand = st.sidebar.selectbox("Select Brand", brands)

if st.session_state.selected_brand:
    selected_date = st.sidebar.date_input("Select Date", value=date.today())

    if selected_date:
        # selecte_date_obj = datetime.strptime(selected_date, "%d-%m-%Y")
        st.session_state.selected_date = selected_date.strftime("%d-%m-%Y")
        previous_date_obj = selected_date - timedelta(days=1)
        previous_date = previous_date_obj.strftime("%d-%m-%Y") 
        
        folder_id = get_folder_id(st.session_state.selected_brand)
        if folder_id:
            expected_file_name = f"{st.session_state.selected_brand}_Prices_{st.session_state.selected_date}.xlsx"
            current_file_id = get_file_id_in_folder(folder_id, expected_file_name)

            previous_file_name = f"{st.session_state.selected_brand}_Prices_{previous_date}.xlsx"
            previous_file_id = get_file_id_in_folder(folder_id, previous_file_name)

            if current_file_id:
                request = drive_service.files().get_media(fileId=current_file_id)
                file_data = BytesIO()
                downloader = request.execute()
                file_data.write(downloader)
                file_data.seek(0)
                df = load_data(file_data)

                if previous_file_id:
                    request = drive_service.files().get_media(fileId=previous_file_id)
                    file_data = BytesIO()
                    downloader = request.execute()
                    file_data.write(downloader)
                    file_data.seek(0)
                    prev_df = load_data(file_data)
                    
                if st.sidebar.button("Preview Data") or st.session_state.data_loaded:
                    st.session_state.data_loaded = True
                    tab1, tab2, tab3 = st.tabs(["🗃 Data", ":bar_chart: Price Comparison", ":chart_with_upwards_trend: Price Trend (Average Price)"])
                    with tab1:
                        st.write(f"### Price list for `{st.session_state.selected_brand}`")
                        website_columns = df.columns[2:]
                        try:
                            df_merged = df.merge(prev_df, on=["SKU", "Product"], how="left", suffixes=("_today", "_yesterday"))
                            df_display = df_merged[["SKU", "Product"] + [col + "_today" for col in website_columns]].copy()
                            rename_dict = {col + "_today": col for col in website_columns}
                            df_display.rename(columns=rename_dict, inplace=True)
                            styled_df = df_display.style.apply(highlight_changes, axis=1, subset=website_columns)
                            for col in website_columns:
                                df_display[col] = df_display[col].astype(str)
                                df_display[col + "_Arrow"] = ""
                                for index, row in df_display.iterrows():
                                    today_price = extract_price(row[col])
                                    prev_col = col + "_yesterday"
                                    prev_price_str = df_merged.loc[index, prev_col] if prev_col in df_merged.columns else None
                                    prev_price = extract_price(prev_price_str)
                                    if today_price is not None and prev_price is not None:
                                        if today_price > prev_price:
                                            df_display.at[index, col + "_Arrow"] = "🔺"
                                        elif today_price < prev_price:
                                            df_display.at[index, col + "_Arrow"] = "🔻"
                            for col in website_columns:
                                df_display[col] = df_display[col] + " " + df_display[col + "_Arrow"]
                                df_display.drop(columns=[col + "_Arrow"], inplace=True)
                            st.dataframe(styled_df, hide_index=True, height=600)
                        except:
                            st.dataframe(df, hide_index=True, height=600)

                    with tab2:
                        products = df["Product"].unique()
                        st.session_state.selected_product = st.sidebar.selectbox("Select Product", products)
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
                                    text="Price",
                                    color_discrete_sequence=px.colors.qualitative.Prism
                                )
                                fig.update_layout(
                                    title_font_size=22,
                                    title_font_family="Arial",
                                    plot_bgcolor="#f9f9f9",
                                    paper_bgcolor="#f9f9f9",
                                    font=dict(
                                        family="Arial",
                                        size=14,
                                        color="#333333"
                                    ),
                                    xaxis=dict(
                                        title="Competitor",
                                        titlefont_size=16,
                                        tickfont_size=12
                                    ),
                                    yaxis=dict(
                                        title="Price (£)",
                                        titlefont_size=16,
                                        tickfont_size=12
                                    ),
                                    margin=dict(l=40, r=40, t=60, b=40)
                                )
                                fig.update_traces(
                                    texttemplate='£%{text:.2f}',
                                    textposition='inside'
                                )
                                st.plotly_chart(fig, use_container_width= True)

                    # with tab3:
                    #     folder_path = brand_directory
                    #     file_pattern = os.path.join(folder_path, f"{st.session_state.selected_brand}_Prices_*.xlsx")
                    #     all_files = sorted([f for f in glob.glob(file_pattern)])
                    #     combined_df = []
                    #     for file in all_files:
                    #         date = datetime.strptime(file.split("_")[-1].replace(".xlsx", ""), "%d-%m-%Y")
                    #         df = pd.read_excel(file, dtype=str)
                    #         df.columns = df.columns.str.strip().str.lower()
                    #         df["date"] = date
                    #         combined_df.append(df)
                    #     if combined_df:
                    #         df_all = pd.concat(combined_df, ignore_index=True)
                    #         df_long = df_all.melt(id_vars=["sku", "product", "date"],
                    #                               var_name="website", value_name="price")
                    #         df_long["price_numeric"] = df_long["price"].astype(str).apply(extract_price)
                    #         df_long = df_long.dropna(subset=["price"])
                    #         selected_product = st.session_state.selected_product
                    #         avg_price_trend = df_long[df_long["product"] == selected_product].groupby("date")["price_numeric"].mean().reset_index()
                    #         avg_price_trend["product"] = selected_product
                    #         st.write(f"📈 Average Price Trend for `{selected_product}` over time: ")
                    #         fig = px.line(avg_price_trend, x="date", y="price_numeric", title=f"Average Price Trend for {selected_product}", hover_data= ["price_numeric"], 
                    #                       markers=True, labels={"date": "Date", "price_numeric": "Price in £"}, hover_name="product")
                    #         st.plotly_chart(fig)
                else:
                    
                    components.html(
                        """
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                        * {box-sizing: border-box;}
                        body {font-family: Verdana, sans-serif;}
                        .mySlides {display: none;}
                        img {vertical-align: middle; width: 100%; border-radius: 10px;}

                        /* Slideshow container */
                        .slideshow-container {
                            max-width: 800px;
                            position: relative;
                            margin: auto;
                            padding-top: 40px;
                        }

                        /* Title text (top of image) */
                        .title-text {
                            color: #ffffff;
                            font-size: 24px;
                            font-weight: bold;
                            padding: 12px;
                            position: absolute;
                            top: 0;
                            width: 100%;
                            text-align: center;
                            background-color: rgba(0, 0, 0, 0.5);
                            border-top-left-radius: 10px;
                            border-top-right-radius: 10px;
                        }

                        /* Dots */
                        .dot {
                            height: 15px;
                            width: 15px;
                            margin: 0 2px;
                            background-color: #bbb;
                            border-radius: 50%;
                            display: inline-block;
                            transition: background-color 0.6s ease;
                        }

                        .active {
                            background-color: #717171;
                        }

                        .fade {
                            animation-name: fade;
                            animation-duration: 1.5s;
                        }

                        @keyframes fade {
                            from {opacity: 0.001} 
                            to {opacity: 1}
                        }

                        </style>
                        </head>
                        <body>

                        <div class="slideshow-container">

                            <div class="mySlides fade">
                                <div class="title-text">Celotex</div>
                                <img src="https://www.building-supplies-online.co.uk/cdn/shop/files/walls_-_external_wall_insulation_-_timber_frame_walls_1.png?v=1737114043&width=1946">
                            </div>
                            
                            <div class="mySlides fade">
                                <div class="title-text">Recticel</div>
                                <img src="https://www.building-supplies-online.co.uk/cdn/shop/files/Eurothane_20gp_11_1.jpg">
                            </div>

                            <div class="mySlides fade">
                                <div class="title-text">Ecotherm</div>
                                <img src="//build4less.co.uk/cdn/shop/files/Untitleddesign-2024-03-22T094324.755_64d98e44-6e84-46e8-8385-f6acb6837e9f.png?v=1711108001&width=1946">
                            </div>

                        </div>
                        <br>

                        <div style="text-align:center">
                            <span class="dot"></span> 
                            <span class="dot"></span> 
                            <span class="dot"></span> 
                        </div>

                        <script>
                        let slideIndex = 0;
                        showSlides();

                        function showSlides() {
                            let i;
                            let slides = document.getElementsByClassName("mySlides");
                            let dots = document.getElementsByClassName("dot");
                            for (i = 0; i < slides.length; i++) {
                                slides[i].style.display = "none";  
                            }
                            slideIndex++;
                            if (slideIndex > slides.length) {slideIndex = 1}    
                            for (i = 0; i < dots.length; i++) {
                                dots[i].className = dots[i].className.replace(" active", "");
                            }
                            slides[slideIndex-1].style.display = "block";  
                            dots[slideIndex-1].className += " active";
                            setTimeout(showSlides, 6000); // Change image every 2 seconds
                        }
                        </script>

                        </body>
                        </html>
                        """,
                        height=650,
                    )
            else:
                st.markdown(
                            """
                            <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
                                <p style="background-color: #FFDDDD; color: red; padding: 15px; font-size: 18px; font-weight: bold; border-radius: 10px;">
                                    ❌ Data for the selected date is not available. 
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        else:
            st.markdown(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
                <p style="background-color: #FFDDDD; color: red; padding: 15px; font-size: 18px; font-weight: bold; border-radius: 10px;">
                    ❌ Selected Brand is not available right now. 
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
