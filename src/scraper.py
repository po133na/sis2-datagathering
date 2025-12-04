import logging
import random
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_arbuz(max_products: int = 50) -> list:
    categories = [
        ("https://arbuz.kz/ru/almaty/catalog/cat/225164-ovoshi_frukty_zelen#/", "Овощи и фрукты"),
        ("https://arbuz.kz/ru/almaty/catalog/cat/225165-frukty#/", "Фрукты"),
        ("https://arbuz.kz/ru/almaty/catalog/cat/225166-ovoshi#/", "Овощи"),
        ("https://arbuz.kz/ru/almaty/catalog/cat/225167-zelen_salaty#/", "Зелень и салаты"),
        ("https://arbuz.kz/ru/almaty/catalog/cat/140597-griby#/", "Грибы"),
        ("https://arbuz.kz/ru/almaty/catalog/cat/225463-yagody#/", "Ягоды"),
        ("https://arbuz.kz/ru/almaty/catalog/cat/225169-svezhie_soki#/", "Свежие соки"),
    ]
    
    logger.info(f"scraping started from {len(categories)} categories)")
    
    results = []
    products_per_category = max_products // len(categories) + 10  
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--window-size=1920,1080',
                '--start-maximized',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='ru-RU',
            timezone_id='Asia/Almaty',
            geolocation={'latitude': 43.238949, 'longitude': 76.945465},
            permissions=['geolocation'],
        )
        
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US', 'en']
            });
            window.chrome = { runtime: {} };
        """)
        
        page = context.new_page()
        page.set_default_timeout(60000) 
        
        try:
            all_links = []
            for cat_url, cat_name in categories:
                if len(all_links) >= max_products:
                    break
                    
                logger.info(f"parsing category {cat_name}")
                links = get_product_links(page, cat_url, products_per_category)
                logger.info(f"found {len(links)} links in {cat_name}")
                all_links.extend(links)
                
                time.sleep(random.uniform(1, 2))
            
            all_links = list(dict.fromkeys(all_links))[:max_products]
            logger.info(f"total unique links: {len(all_links)}")
            
            if not all_links:
                logger.warning("no product links found")
                return results
            
            for i, link in enumerate(all_links):
                if i % 10 == 0:
                    logger.info(f"products scraped: {i}/{len(all_links)}")
                
                try:
                    data = scrape_product(page, link)
                    if data:
                        results.append(data)
                    
                    time.sleep(random.uniform(0.3, 0.8))
                    
                except Exception as e:
                    logger.error(f"failed to scrape {link}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"critical error during scraping: {e}")
        finally:
            context.close()
            browser.close()
    
    logger.info(f"scraped total {len(results)} products")
    return results


def get_product_links(page, url: str, max_products: int = 50) -> list:
    links = []
    
    try:
        logger.info(f"Opening URL: {url}")
        
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_selector('body', timeout=30000)
        logger.info("Page body loaded")
        
        page.wait_for_timeout(7000)
        page.evaluate("window.scrollBy(0, 500)")
        page.wait_for_timeout(2000)
        
        selectors_to_try = [
            '.product-card__link',
            'a[href*="/product/"]',
            '.product-card a',
            '[data-testid="product-card"] a',
            '.catalog-product-card a',
        ]
        
        product_cards = []
        used_selector = None
        for selector in selectors_to_try:
            product_cards = page.query_selector_all(selector)
            if product_cards:
                logger.info(f"found {len(product_cards)} products with selector: {selector}")
                used_selector = selector
                break
        
        if not product_cards:
            html_content = page.content()
            logger.info(f"page HTML length: {len(html_content)}")
            logger.info(f"page title: {page.title()}")
            logger.info(f"current URL: {page.url}")
            return links
        
        while len(links) < max_products:
            product_cards = page.query_selector_all(used_selector)
            
            for card in product_cards:
                if len(links) >= max_products:
                    break
                href = card.get_attribute('href')
                
                if len(links) < 3:
                    logger.info(f"{href}")
                
                if href and href not in links:
                    if href.startswith('/'):
                        href = 'https://arbuz.kz' + href
                    links.append(href)
            
            if len(links) >= max_products:
                break
                
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)
                
                show_more_selectors = [
                    'button:has-text("Показать ещё")',
                    '.arbuz-pagination-show-more',
                    '[class*="show-more"]',
                    '[class*="load-more"]',
                    'button[class*="pagination"]',
                ]
                
                clicked = False
                for selector in show_more_selectors:
                    try:
                        show_more = page.query_selector(selector)
                        if show_more and show_more.is_visible():
                            logger.info(f"clicking load more button: {selector}")
                            show_more.scroll_into_view_if_needed()
                            page.wait_for_timeout(500)
                            show_more.click()
                            page.wait_for_timeout(3000)
                            clicked = True
                            break
                    except:
                        continue
                
                if not clicked:
                    old_count = len(links)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)
                    
                    new_cards = page.query_selector_all(used_selector)
                    if len(new_cards) <= len(product_cards):
                        logger.info("no products available")
                        break
                        
            except Exception as e:
                logger.info(f"error loading more products: {e}")
                break
                
        logger.info(f"collected product links: {len(links)} ")
        return links
        
    except PlaywrightTimeout as e:
        logger.error(f"timeout: {e}")
        return links
    except Exception as e:
        logger.error(f"error: {e}")
        return links


def scrape_product(page, url: str) -> dict | None:
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(2000)
        
        product_name = None
        name_selectors = [
            '.product-card__title',
            'h1',
            '[data-testid="product-title"]',
            '.product-title',
            '.product-name',
        ]
        
        for selector in name_selectors:
            name_element = page.query_selector(selector)
            if name_element:
                product_name = name_element.inner_text().strip()
                if product_name:
                    break
        
        if not product_name:
            logger.warning(f"no products found for {url}")
            return None
        
        
        price = get_price(page)
        
        category = "Unknown"
        breadcrumb_selectors = [
            '.breadcrumb-item a',
            '.breadcrumbs a',
            '[class*="breadcrumb"] a',
        ]
        
        for selector in breadcrumb_selectors:
            breadcrumbs = page.query_selector_all(selector)
            if len(breadcrumbs) > 1:
                category = breadcrumbs[-2].inner_text().strip() if len(breadcrumbs) > 1 else breadcrumbs[0].inner_text().strip()
                break
        
        brand = "Unknown"
        try:
            meta = page.query_selector('meta[property="og:description"]')
            if meta:
                content = meta.get_attribute('content') or ''
                if 'Бренд:' in content:
                    brand = content.split('Бренд:')[1].split('.')[0].strip()
        except:
            pass

        available = True
        unavailable_selectors = [
            '.product-card__unavailable',
            '[class*="unavailable"]',
            '[class*="out-of-stock"]',
        ]
        
        for selector in unavailable_selectors:
            if page.query_selector(selector):
                available = False
                break
        
        return {
            "product_name": product_name,
            "product_url": url,
            "price": price,
            "category": category,
            "brand": brand,
            "available": available,
            "parse_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None


def get_price(page) -> int:
    price_selectors = [
        "span[class*='price--wrapper'] span",
        "[class*='price'] span",
        ".product-price",
        "[data-testid='price']",
    ]
    
    for selector in price_selectors:
        try:
            elements = page.query_selector_all(selector)
            for el in elements:
                price_text = el.inner_text()
                price_text = ''.join(filter(str.isdigit, price_text))
                if price_text and len(price_text) >= 2:  
                    return int(price_text)
        except:
            continue
    
    return 0