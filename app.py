
"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://2nabiji.ge/ge/search?searchId=64c19575b3118b3676d26898"

SCROLL_ROUNDS = 15
SCROLL_PAUSE_MS = 1500

def scrape_products(url: str) -> list:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )

        print(f"Opening {url} …")
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_selector("a[class*='ProductCard_title']", timeout=15_000)

        prev_count = 0
        for i in range(SCROLL_ROUNDS):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(SCROLL_PAUSE_MS)

            cur_count = page.locator("a[class*='ProductCard_title']").count()
            print(f"  scroll {i+1}: {cur_count} products visible")

            if cur_count == prev_count:
                print("  No new items — stopping early.")
                break
            prev_count = cur_count

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Each product card is a container — find them all
    cards = soup.select("div[class*='ProductCard_container']")

    results = []
    for card in cards:
        title_tag = card.select_one("a[class*='ProductCard_title']")
        price_tag = card.select_one("a[class*='ProductCard_productInfo__price'] span")

        title = title_tag.get_text(strip=True) if title_tag else ""
        price = price_tag.get_text(strip=True) if price_tag else ""
        href  = title_tag.get("href", "") if title_tag else ""

        results.append({
            "title": title,
            "price": price,
            "full_url": "https://2nabiji.ge" + href,
        })

    return results

items = scrape_products(URL)
df = pd.DataFrame(items)

df.to_json(
    "products.json",
    orient="records",
    force_ascii=False,
    indent=4
)


import requests
from bs4 import BeautifulSoup

url = "https://2nabiji.ge/ge/search?searchId=64c19575b3118b3676d26898"

reqsponse = requests.get(url)
soup = BeautifulSoup(reqsponse.text, 'html.parser')

content = soup.find("div", class_="Layout_contentWrapper__1Mzbi")

if content:
    main = content.find("main", class_="fit")
    print(main)


print(url.status_code)
print(url.content)


from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

import sys

sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto("https://2nabiji.ge/ge/search?searchId=64c19575b3118b3676d26898")
    page.wait_for_selector("div.ProductCard_container__7IE0M")

    soup = BeautifulSoup(page.content(), "html.parser")

    browser.close()

products = soup.find_all("div", class_="ProductCard_container__7IE0M")

for product in products:
    title = product.find("span", title=True)
    print(title)


"""
from flask import Flask, jsonify, send_file   
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

# ✅ Initialize app FIRST (before routes!)
app = Flask(__name__)

URL = "https://2nabiji.ge/ge/search?searchId=64c19575b3118b3676d26898"
SCROLL_ROUNDS = 15
SCROLL_PAUSE_MS = 1500

def scrape_products(url: str) -> list:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        print(f"Opening {url} …")
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_selector("a[class*='ProductCard_title']", timeout=15_000)
        prev_count = 0
        for i in range(SCROLL_ROUNDS):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(SCROLL_PAUSE_MS)
            cur_count = page.locator("a[class*='ProductCard_title']").count()
            print(f"  scroll {i+1}: {cur_count} products visible")
            if cur_count == prev_count:
                print("  No new items — stopping early.")
                break
            prev_count = cur_count
        html = page.content()
        browser.close()
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div[class*='ProductCard_container']")
    results = []
    for idx, card in enumerate(cards, start=1):
        title_tag = card.select_one("a[class*='ProductCard_title']")
        price_tag = card.select_one("a[class*='ProductCard_productInfo__price'] span")
        title = title_tag.get_text(strip=True) if title_tag else ""
        price = price_tag.get_text(strip=True) if price_tag else ""
        href  = title_tag.get("href", "") if title_tag else ""
        results.append({
            "id": idx,
            "title": title,
            "price": price,
            "full_url": "https://2nabiji.ge" + href,
        })
    return results

# ✅ ROUTES defined AFTER app is created
@app.route('/')
def home():
    return send_file('index.html')

@app.route('/api/products')
def get_products():
    items = scrape_products(URL)
    return jsonify(items)

# ✅ Only run if executed directly (not when imported by gunicorn)
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)


