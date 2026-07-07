

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
print(df.to_string ())

df.to_json(
    "D:\Data\Data Engineering\OrinabijiDiscounts\Python-Libraries_Programming\disc.json",
    orient="records",
    force_ascii=False,
    indent=4
)

import pandas as pd
import pyodbc

def main():

    user = 'DESKTOP-3QJN7S3' + "\)" + "user"  # sql server user name
    user_rep = user.replace(")", "")

    conn = pyodbc.connect("Driver={SQL Server};"
                              "Server=DESKTOP-3QJN7S3;"  # Server name
                              f"uid={user_rep}"
                              "Database=Data_Model;"  # selected database
                              "Trusted_Connection=yes;")

    cursor = conn.cursor()


    data = pd.read_sql_query('''select 8 from Data_Model.dbo.orinabiji''', conn)


    if data is None:
        pass
    else:
        try:
            cursor.execute('''create table Data_Model.dbo.orinabiji (product_name nvarchar(max), price float, url nvarchar(max))''')
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"{e}")



    for index, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO Data_Model.dbo.orinabiji (product_name, price, url)
                VALUES (?, ?, ?)
            ''', row['title'], row['price'], row['full_url'])
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting row {index + 1}: {e}")

    # Close the cursor and connection
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()



from flask import Flask, render_template
import pyodbc

app = Flask(__name__)


def get_products():
    conn = pyodbc.connect(
        "Driver={SQL Server};"
        "Server=DESKTOP-3QJN7S3;"
        "Database=Data_Model;"
        "Trusted_Connection=yes;"
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT product_name, price, url
        FROM Data_Model.dbo.orinabiji
    """)

    products = cursor.fetchall()

    conn.close()

    return products


@app.route("/")
def home():
    products = get_products()
    return render_template("D:\Data\Data Engineering\OrinabijiDiscounts\index.html", products=products)


if __name__ == "__main__":
    app.run(debug=True)
