import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
import json
import re

def extract_meta_info(soup):
    meta_title = soup.find('title').text if soup.find('title') else ''
    meta_description = ''
    if soup.find('meta', attrs={'name': 'description'}):
        meta_description = soup.find('meta', attrs={'name': 'description'})['content']
    return meta_title, meta_description

# Function to extract social media links
def extract_social_media_links(soup):
    social_links = {}
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'facebook.com' in href:
            social_links['facebook'] = href
        elif 'twitter.com' in href:
            social_links['twitter'] = href
        elif 'instagram.com' in href:
            social_links['instagram'] = href
        elif 'linkedin.com' in href:
            social_links['linkedin'] = href
    return social_links

# Function to extract tech stack and category using regex and common patterns
def extract_tech_stack_and_category(soup, scripts):
    tech_stack = set()
    category = "Unknown"

    # Detecting common CMS, frameworks, and libraries
    cms_patterns = {
        'WordPress': 'wp-content|wp-',
        'Joomla': 'joomla',
        'Drupal': 'drupal',
        'Magento': 'magento'
    }
    
    js_frameworks_patterns = {
        'React': 'react',
        'Angular': 'angular',
        'Vue.js': 'vue',
        'jQuery': 'jquery'
    }

    for cms, pattern in cms_patterns.items():
        if re.search(pattern, str(soup), re.IGNORECASE):
            tech_stack.add(cms)
    
    for framework, pattern in js_frameworks_patterns.items():
        if re.search(pattern, str(scripts), re.IGNORECASE):
            tech_stack.add(framework)

    # Attempt to detect category based on meta tags or page content
    if soup.find('meta', attrs={'name': 'category'}):
        category = soup.find('meta', attrs={'name': 'category'})['content']
    elif soup.find('meta', attrs={'property': 'og:type'}):
        category = soup.find('meta', attrs={'property': 'og:type'})['content']
    elif 'ecommerce' in str(soup).lower() or 'shop' in str(soup).lower():
        category = 'E-commerce'
    elif 'blog' in str(soup).lower():
        category = 'Blog'
    
    return ', '.join(tech_stack), category

# Function to extract other information using Selenium
def extract_with_selenium(url):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    driver.get(url)
    
    website_language = driver.execute_script("return document.documentElement.lang") or "Unknown"
    
    # Extract scripts content for tech stack detection
    scripts = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    
    driver.quit()
    return website_language, scripts

# Function to save to MySQL
def save_to_mysql(data):
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='1234',
        database='web_info_db'
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO website_info (url, social_media_links, tech_stack, meta_title, meta_description, payment_gateways, website_language, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data['url'], json.dumps(data['social_media_links']), data['tech_stack'], data['meta_title'], data['meta_description'], data['payment_gateways'], data['website_language'], data['category']
    ))
    conn.commit()
    cursor.close()
    conn.close()

# Main function to process a list of websites
def main(websites):
    for url in websites:
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            meta_title, meta_description = extract_meta_info(soup)
            social_media_links = extract_social_media_links(soup)
            website_language, scripts = extract_with_selenium(url)
            tech_stack, category = extract_tech_stack_and_category(soup, scripts)
            payment_gateways = "Unknown"  # Modify this as per actual extraction logic
            
            # Print extracted data for verification
            print("URL:", url)
            print("Meta Title:", meta_title)
            print("Meta Description:", meta_description)
            print("Social Media Links:", social_media_links)
            print("Tech Stack:", tech_stack)
            print("Payment Gateways:", payment_gateways)
            print("Website Language:", website_language)
            print("Category:", category)
            print("\n" + "="*50 + "\n")
            
            data = {
                'url': url,
                'social_media_links': social_media_links,
                'tech_stack': tech_stack,
                'meta_title': meta_title,
                'meta_description': meta_description,
                'payment_gateways': payment_gateways,
                'website_language': website_language,
                'category': category
            }
            save_to_mysql(data)
            print(f"Data extracted and saved for {url}")
        except Exception as e:
            print(f"Failed to process {url}: {e}")

# Function to retrieve and display data from MySQL
def fetch_data():
    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='1234',
            database='web_info_db'
        )
        cursor = conn.cursor()

        # Execute the SELECT query
        cursor.execute("SELECT * FROM website_info")

        # Fetch all rows from the executed query
        rows = cursor.fetchall()

        # Print the column names
        column_names = [desc[0] for desc in cursor.description]
        print(column_names)

        # Print each row
        for row in rows:
            # Parse JSON fields
            social_media_links = json.loads(row[2]) if row[2] else {}
            print({
                "id": row[0],
                "url": row[1],
                "social_media_links": social_media_links,
                "tech_stack": row[3],
                "meta_title": row[4],
                "meta_description": row[5],
                "payment_gateways": row[6],
                "website_language": row[7],
                "category": row[8]
            })

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    websites = [
        "https://www.linkedin.com",
        "https://www.facebook.com",
        "https://www.twitter.com",
        "https://www.instagram.com",
        "https://www.github.com",
        "https://www.medium.com",
        "https://www.reddit.com",
        "https://www.wikipedia.org",
        "https://www.amazon.com",
        "https://www.ebay.com",
    ]
    main(websites)
    fetch_data()

