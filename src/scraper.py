import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

logging.basicConfig(level=logging.INFO)

def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def get_product_links(url, max_products=50):
    driver = create_driver()
    links = []
    
    try:
        driver.get(url)
        time.sleep(3)
        
        for _ in range(5):
            products = driver.find_elements(By.CLASS_NAME, "product-card__link")
            for p in products:
                href = p.get_attribute("href")
                if href and href not in links and len(links) < max_products:
                    links.append(href)
            
            try:
                btn = driver.find_element(By.CLASS_NAME, "arbuz-pagination-show-more")
                if btn.is_displayed():
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(2)
                else:
                    break
            except:
                break
                
        logging.info(f'Collected links: {len(links)}')
        return links
    finally:
        driver.quit()

def scrape_product(url):
    driver = create_driver()
    
    try:
        driver.get(url)
        time.sleep(2)
        
        name = driver.find_element(By.CLASS_NAME, "product-card__title").text.strip()
        
        try:
            price_element = driver.find_element(By.XPATH, "//span[contains(@class, 'price--wrapper')]")
            price = int(price_element.text.replace("₸", "").replace(" ", "").strip())
        except:
            price = 0
        
        try:
            category = driver.find_elements(By.CSS_SELECTOR, ".breadcrumb-item a")[0].text
        except:
            category = "Unknown"
        
        try:
            meta = driver.find_element(By.XPATH, "//meta[@property='og:description']").get_attribute("content")
            brand = "Unknown"
            if "Brand:" in meta:
                brand = meta.split("Brand:")[1].split(".")[0].strip()
        except:
            brand = "Unknown"
        
        try:
            available = True
            driver.find_element(By.CLASS_NAME, "product-card__unavailable")
            available = False
        except:
            pass
        
        return {
            'product_name': name,
            'product_url': url,
            'price': price,
            'category': category,
            'brand': brand,
            'available': available,
            'parse_date': datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f'Error: {e}')
        return None
    finally:
        driver.quit()

def scrape_arbuz(max_products=120):
    url = "https://arbuz.kz/ru/almaty/catalog/cat/225164-ovoshi_frukty_zelen#/"
    
    product_links = get_product_links(url, max_products)
    all_data = []
    
    for link in product_links:
        data = scrape_product(link)
        if data:
            all_data.append(data)
        time.sleep(1)
    
    logging.info(f'Collected Products: {len(all_data)}')
    return all_data

if __name__ == "__main__":
    products = scrape_arbuz(max_products=10)
    print(f"Collected Products: {len(products)}")
    if products:
        print("Example:", products[0])