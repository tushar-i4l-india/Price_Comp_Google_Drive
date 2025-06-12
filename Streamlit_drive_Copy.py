import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import re
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


load_dotenv()

def scrape_i4l(url):
    try:
        print(f"Processing URL {url}")
        time.sleep(3)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = re.compile("exc_vat_price"))  
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_b4l(url):
    try:
        print(f"Processing URL {url}")
        time.sleep(3)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_div = soup.find("div", class_ = "price__regular")
        price_element = price_div.find("span", class_ = re.compile("exc_vat_price"))
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_bso(url):
    try:
        print(f"Processing URL {url}")
        time.sleep(3)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = re.compile("exc_vat_price"))  # Replace with actual class or ID
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
# Function to scrape ex-VAT price from Insulation Superstore
def scrape_insulation_superstore(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("strong", class_ = re.compile("ex-vat"))  
        if price_element:
            return price_element.text.strip()
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_materialmarket(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_elements = soup.find("span", class_ = "c-product-information__price col l12 s6") 
        price_element = price_elements.find("span")["data-product-price-single-unit"]
        if price_element:
            if "xr4165" in url or "xr4200" in url:
                price_element = round(float(price_element)*12, 2)
                return f"£{price_element}"
            elif "thermaclass" in url:
                price_element = round(float(price_element)*16, 2)
                return f"£{price_element}"
            else:
                return f"£{price_element}"
        return 'Price Not Found'
    except AttributeError:
        return f"POA or Product 'out of stock'"
    except Exception as e:
        return f'Error: {str(e)}'
    
def scrape_tradeinsulation(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find("p", class_ = "price") 
        price_elements = price_tag.find_all("span", class_ = "woocommerce-Price-amount amount")
        if len(price_elements) == 2:
            price_element = price_elements[1].text.strip()
        else:
            price_element = price_elements[0].text.strip()
        if price_element:
            if "165mm" in url or "200mm-celotex" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*12, 2)
                return f'£{price_element}'
            elif "thermaclass" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            else:
                return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationwholesale(url):
    print(f"Processing URL {url}")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    try:
        price_element = soup.find_all("span", class_ = "woocommerce-Price-amount amount")[2].text.strip()
        if price_element:
            if "xr4165" in url or "xr4200" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*12, 2)
                return f'£{price_element}'
            elif "thermaclass" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationhub(url):
    print(f"Processing URL {url}")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.quit() 
    try:
        price_div = soup.find("div", class_ = "price-wrapper")
        price_elements = price_div.find_all("span", class_ = "woocommerce-Price-amount amount")
        if len(price_elements) > 2:
            price_element = price_elements[2].text.strip()
            old_price = float(price_elements[0].text.strip().replace("£", ""))
            return f"{price_element} presale price: £{round(old_price/1.2, 2)}"
        else:
            price_element = price_elements[1].text.strip()
            if price_element:
                if "xr4165" in url or "xr4200" in url:
                    price_element = price_element.replace("£", "")
                    price_element = round(float(price_element)*12, 2)
                    return f'£{price_element}'
                elif "thermaclass" in url and "90mm" in url:
                    price_element = price_element.replace("£", "")
                    price_element = round(float(price_element)*96, 2)
                    return f'£{price_element}'
                elif "thermaclass" in url and "115mm" in url:
                    price_element = price_element.replace("£", "")
                    price_element = round(float(price_element)*80, 2)
                    return f'£{price_element}'
                elif "thermaclass" in url and "140mm" in url:
                    price_element = price_element.replace("£", "")
                    price_element = round(float(price_element)*64, 2)
                    return f'£{price_element}'
                elif "cw4100" in url:
                    price_element = price_element.replace("£", "")
                    price_element = round(float(price_element)*6, 2)
                    return f'£{price_element}'   
                elif "cw4050" in url:
                    price_element = price_element.replace("£", "")
                    price_element = round(float(price_element)*11, 2)
                    return f'£{price_element}'    
                elif "cw4075" in url:
                    price_element = price_element.replace("£", "")
                    price_element = round(float(price_element)*8, 2)
                    return f'£{price_element}'               
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_online_insulation_sales(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("small", class_ = re.compile("ex-vat")).text.split()[0].strip()
        if price_element:
            if "thermaclass" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

# Function to scrape ex-VAT price from Building Materials
def scrape_building_materials(url, series):
    try:
        print(f"Processing URL {url}")
        driver = webdriver.Chrome()
        driver.get(url)  
        thickness_div = driver.find_element(By.ID, "attribute1999")
        if thickness_div:
            thickness_div.click()
            time.sleep(5)
            select = Select(thickness_div)
            for option in select.options:
                select.select_by_visible_text(option.text)
                if option.text == "Choose an Option...":
                    continue
                updated_html = driver.page_source
                s1 = BeautifulSoup(updated_html, "html.parser") 
                title = s1.find("h1", class_ = re.compile("page-title")).text.strip() 
                if series in title:
                    price_element = s1.find_all("span", class_ = "price-wrapper")[1].text.strip().split()[0]
                    break
        if price_element:
            if "CW4085" in title:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'
    finally:
        driver.quit()

def scrape_planetinsulation(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = "price-item price-item--sale price-item--last").text.strip()
        if price_element:
            if "thermaclass" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationonline(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        time.sleep(3)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", class_ = "woocommerce-Price-amount amount").text.strip()
        if price_element:
            if "xr4110" in url:
                price_element = price_element.replace("£", "").replace(",", "")
                price_element = round(float(price_element)/10, 2)
                return f'£{price_element}'
            elif "xr4130" in url:
                price_element = price_element.replace("£", "").replace(",", "")
                price_element = round(float(price_element)/9, 2)
                return f'£{price_element}'
            elif "pl4025" in url:
                price_element = price_element.replace("£", "").replace(",", "")
                price_element = round(float(price_element)/26, 2)
                return f'£{price_element}'
            elif "pl4040" in url:
                price_element = price_element.replace("£", "").replace(",", "")
                price_element = round(float(price_element)/22, 2)
                return f'£{price_element}'
            elif "pl4050" in url:
                price_element = price_element.replace("£", "").replace(",", "")
                price_element = round(float(price_element)/18, 2)
                return f'£{price_element}'  
            elif "pl4060" in url:
                price_element = price_element.replace("£", "").replace(",", "")
                price_element = round(float(price_element)/16, 2)
                return f'£{price_element}'
            elif "pl4065" in url:
                price_element = price_element.replace("£", "").replace(",", "")
                price_element = round(float(price_element)/14, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationshop(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("div", class_ = "product-price").text.split()[1].strip()
        if price_element == "Price:":
            price_elements = soup.find("div", class_ = "product-price").text.split()[2].strip()
            if "165mm" in url or "200mm" in url:
                price_elements = price_elements.replace("£", "")
                price_elements = round(float(price_elements)*2, 2)
                return f'£{price_elements}'
            elif "thermaclass" in url or "85mm" in url:
                price_elements = price_elements.replace("£", "")
                price_elements = round(float(price_elements)*16, 2)
                return f'£{price_elements}'
            return price_elements
        else: 
            if "165mm" in url or "200mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*2, 2)
                return f'£{price_element}'
            elif "thermaclass" in url or "85mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_directinsulation(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("span", attrs={"data-hook": "formatted-primary-price"}).text.strip() 
        if price_element:
            if "xr4110" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)/11, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationbee(url):
    print(f"Processing URL {url}")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    try:
        price_element = soup.find("span", id = "price-old").text.split()[0].strip()
        if price_element:
            if "200mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*12, 2)
                return f'£{price_element}'
            elif "85mm" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'                
            return price_element
        return 'Price Not Found'
    except AttributeError:
        return f'POA or OOS'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_insulationuk(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("strong", class_ = "price__current js-price-without-vat").text.split()[0].strip()
        if price_element:
            if "xr4200" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*12, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

def scrape_diybuildingsupplies(url):
    try:
        print(f"Processing URL {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.find("strong", class_ = "price__current").text.split()[0].strip() 
        if price_element:
            if "thermaclass" in url:
                price_element = price_element.replace("£", "")
                price_element = round(float(price_element)*16, 2)
                return f'£{price_element}'
            return price_element
        return 'Price Not Found'
    except Exception as e:
        return f'Error: {str(e)}'

df = pd.read_excel("Celotex & Recticel Links.xlsx", sheet_name="Celotex")

result_data = []
for index, row in df.iterrows():
    sku = row["SKU"]
    product = row["Products"]
    series = row["Series"]
    scraped_prices = {
        "I4L": scrape_i4l(row["I4L"]) if pd.notna(row["I4L"]) else 'N/L',
        "B4L": scrape_b4l(row["B4L"]) if pd.notna(row["B4L"]) else 'N/L',
        "BSO": scrape_bso(row["BSO"]) if pd.notna(row["BSO"]) else 'N/L',
        "Insulation Superstore": scrape_insulation_superstore(row["Insulation Superstore"]) if pd.notna(row["Insulation Superstore"]) else 'N/L',
        "Materials Market": scrape_materialmarket(row["Materials Market"]) if pd.notna(row["Materials Market"]) else 'N/L',
        "Trade Insulations": scrape_tradeinsulation(row["Trade Insulations"]) if pd.notna(row["Trade Insulations"]) else 'N/L',
        "Insulation Wholesale": scrape_insulationwholesale(row["Insulation Wholesale"]) if pd.notna(row["Insulation Wholesale"]) else 'N/L',
        "Insulation Hub": scrape_insulationhub(row["Insulation Hub"]) if pd.notna(row["Insulation Hub"]) else 'N/L',
        "InsulationUK": scrape_insulationuk(row["InsulationUK"]) if pd.notna(row["InsulationUK"]) else 'N/L',
        "Online Insulation Sales": scrape_online_insulation_sales(row["Online Insulation Sales"]) if pd.notna(row["Online Insulation Sales"]) else 'N/L',
        "Building Materials": scrape_building_materials(row["Building Materials"], series) if pd.notna(row["Building Materials"]) else 'N/L',
        "Insulation Online": scrape_insulationonline(row["Insulation Online"]) if pd.notna(row["Insulation Online"]) else 'N/L',
        "Planet Insulation": scrape_planetinsulation(row["Planet Insulation"]) if pd.notna(row["Planet Insulation"]) else 'N/L',
        "Insulation Shop": scrape_insulationshop(row["Insulation Shop"]) if pd.notna(row["Insulation Shop"]) else 'N/L',
        "Building Materials Direct": scrape_directinsulation(row["Building Materials Direct"]) if pd.notna(row["Building Materials Direct"]) else 'N/L',
        "Insulation Bee": scrape_insulationbee(row["Insulation Bee"]) if pd.notna(row["Insulation Bee"]) else 'N/L',
        "DIY Building supplies": scrape_diybuildingsupplies(row["DIY Building supplies"]) if pd.notna(row["DIY Building supplies"]) else 'N/L'
    }
    
    result_data.append({"SKU": sku, "Product": product, **scraped_prices})
        
result_df = pd.DataFrame(result_data)
current_date = datetime.now().strftime("%d-%m-%Y")  # Format: DD-MM-YYYY
output_file_name = f"Celotex_Prices_{current_date}.xlsx"
result_df.to_excel(output_file_name, index=False)
#----------- Upload the file to Google Drive --------------
# ---- Setup constants ----

SERVICE_ACCOUNT_JSON = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
SCOPES = ['https://www.googleapis.com/auth/drive.file']
folder_id = '135ijCCm3bx5WiuMryoI_kGaysTLPvoTz' 

# Authenticate
def authenticate_with_service_account():
    credentials = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_JSON,
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
    return service

# ---- Upload file to Google Drive ----
service = authenticate_with_service_account()
file_metadata = {'name': output_file_name, 'parents': [folder_id]}
media = MediaFileUpload(output_file_name, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
print(f"Uploaded file: {file.get('id')}")
os.remove(output_file_name)