import requests
from bs4 import BeautifulSoup
import os
import re

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")
    else:
        print(f"Folder '{folder_name}' already exists.")

def fetch_page_content(url):
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

def extract_table_data(soup):
    
    table_data = []
    tables = soup.find_all('table')  # Get all tables

    if not tables:
        print("No tables found on the page!")
        return table_data

    print(f"{len(tables)} table(s) found on the page!")
    for table in tables:
        for row in table.find_all('tr'):
            cols = [clean_text(col.get_text()) for col in row.find_all(['td', 'th'])]
            if cols:
                table_data.append(cols)
    return table_data

def clean_text(text):
    
    return re.sub(r'\s+', ' ', text).strip()

def save_table_data(table_data, file_path):
   
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for row in table_data:
                file.write("\t".join(row) + "\n")
        print(f"Table data saved to '{file_path}'.")
    except IOError as e:
        print(f"Error saving table data: {e}")

def download_file(url, file_path):
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Downloaded '{file_path}'.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

def get_image_url(soup):
   
    image_tag = soup.find('img', class_='block margin-auto loaded')
    if image_tag and image_tag.get('src'):
        img_url = image_tag['src']
        print(f"Product image URL found: {img_url}")  # Debug message
        return img_url
    else:
        print("No image tag found with the specified class.")  # Debug message
    return None

def get_datasheet_url():
    
    return 'https://cdn.sick.com/media/pdf/8/08/408/dataSheet_WTB4FP-22161120A00_1222998_en.pdf'

def main():
   
    url = 'https://www.sick.com/in/en/catalog/products/detection-sensors/photoelectric-sensors/w4/wtb4fp-22161120a00/p/p661408?tab=detail'
    
  
    folder_name = 'product_details'
    create_folder(folder_name)

   
    page_content = fetch_page_content(url)
    if not page_content:
        return

    soup = BeautifulSoup(page_content, 'html.parser')

    table_data = extract_table_data(soup)
    if table_data:
        table_file_path = os.path.join(folder_name, 'table_data.txt')
        save_table_data(table_data, table_file_path)
    else:
        print("No table data extracted.")

   
    image_url = get_image_url(soup)
    if image_url:
        if not image_url.startswith('http'):
            image_url = requests.compat.urljoin(url, image_url)
        img_ext = os.path.splitext(image_url)[1].split('?')[0]
        img_ext = img_ext if img_ext else '.jpg'  # Default to .jpg if no extension
        image_filename = f"product_image{img_ext}"
        image_path = os.path.join(folder_name, image_filename)
        download_file(image_url, image_path)
    else:
        print("Product image URL not found.")

    
    datasheet_url = get_datasheet_url()
    if datasheet_url:
        datasheet_filename = 'product_datasheet.pdf'
        datasheet_path = os.path.join(folder_name, datasheet_filename)
        download_file(datasheet_url, datasheet_path)
    else:
        print("Product datasheet URL not found.")

if __name__ == "__main__":
    main()
