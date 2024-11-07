import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_page(url):
    """Fetch webpage content using Selenium."""
    chrome_driver_path = r"C:\driver\chromedriver.exe"  # Update with your Chrome driver path
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        logging.info(f"Navigated to URL: {url}")

        # Wait for product elements to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']"))
        )

        html_content = driver.page_source
        driver.quit()
        return html_content
    except Exception as e:
        logging.error(f"Error fetching page: {str(e)}")
        return None

def extract_product_details(soup):
    """Extract product details from the parsed HTML."""
    products = soup.find_all("div", {"data-component-type": "s-search-result"})
    logging.info(f"Found {len(products)} product elements")

    result = []
    for product in products:
        try:
            product_name = product.find("span", class_="a-size-base-plus a-color-base a-text-normal").text.strip()
            price_text = f"${product.find('span', class_='a-price-whole').text.strip()}"
            rating_text = product.find("span", class_="a-icon-alt").text.strip()
            sales_text = product.find("span", class_="a-size-base a-color-secondary").text.strip()

            result.append({
                "Product Name": product_name,
                "Price": price_text,
                "Rating": rating_text,
                "Sales": sales_text
            })
        except Exception as e:
            logging.warning(f"Incomplete product info: {str(e)}")
            continue

    logging.info(f"Extracted {len(result)} complete product records")
    return result

def scrape_amazon(url, max_pages=5):
    """Scrape product details from Amazon and save to CSV."""
    with open('amazon_products.csv', 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["Product Name", "Price", "Rating", "Sales"])
        writer.writeheader()

        total_products = 0
        for page in range(1, max_pages + 1):
            logging.info(f"Scraping page {page}...")
            page_url = f"{url}&page={page}"
            html_content = fetch_page(page_url)

            if html_content is None:
                logging.warning(f"Skipping page {page} due to error.")
                continue

            soup = BeautifulSoup(html_content, 'html.parser')
            products = extract_product_details(soup)
            writer.writerows(products)
            total_products += len(products)

            logging.info(f"Wrote {len(products)} records to CSV")
            time.sleep(random.uniform(1, 3))  # Delay to avoid being blocked

    logging.info(f"Total products scraped: {total_products}")
    logging.info("Scraping completed. Results saved in amazon_products.csv")

# Main execution
url = "https://www.amazon.in/s?rh=n%3A6612025031&fs=true&ref=lp_6612025031_sar"
scrape_amazon(url)
