import time
import csv
from bs4 import BeautifulSoup
import re
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# Initialize Selenium WebDriver for Chromium
def initialize_webdriver():
    # Set the options for Chromium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Ensure it runs in headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Use the Service to specify the chromedriver path
    service = Service("/usr/bin/chromedriver")
    
    # Initialize the WebDriver with the service and options
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

# Step 1: Function to extract card URLs from the Pokémon set page using Selenium and scrolling
def get_card_urls(set_url, driver):
    driver.get(set_url)

    # Scroll to the bottom of the page to load all cards
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down to the bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for new cards to load
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Now get all the card URLs
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    card_urls = []
    
    try:
        # Find all <a> tags inside the <td class="title">
        card_rows = soup.find_all('tr')  # Each row is a card entry
        
        for row in card_rows:
            link = row.find('a', href=True)  # Find the first <a> tag
            if link:
                href = link['href']
                # Ensure the URL starts correctly with a slash or full URL
                if href.startswith('/'):
                    card_url = "https://www.pricecharting.com" + href
                else:
                    card_url = href
                card_urls.append(card_url)
                print(f"Found card URL: {card_url}")
    
    except Exception as e:
        print(f"Error while scraping card URLs: {e}")
    
    return card_urls



def get_card_data(card_url):
    response = requests.get(card_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    card_data = {'Raw Price': None, 'PSA 8': None, 'PSA 9': None, 'PSA 10': None, 'Card URL': card_url}
    try:
        # Find the price table inside the div with id='full-prices'
        price_section = soup.find('div', id='full-prices')
        if not price_section:
            print(f"Price section not found on the page: {card_url}")
            return None
        
        # Get the rows from the price table
        price_rows = price_section.find_all('tr')
        
        for row in price_rows:
            columns = row.find_all('td')
            if len(columns) > 1:
                label = columns[0].text.strip()
                price = columns[1].text.strip()

                # Ignore the '-' values
                if price == '-':
                    continue

                if 'Ungraded' in label:
                    card_data['Raw Price'] = float(price.replace('$', '').replace(',', ''))
                elif 'Grade 8' in label:
                    card_data['PSA 8'] = float(price.replace('$', '').replace(',', ''))
                elif 'Grade 9' in label:
                    card_data['PSA 9'] = float(price.replace('$', '').replace(',', ''))
                elif 'PSA 10' in label:
                    card_data['PSA 10'] = float(price.replace('$', '').replace(',', ''))

        print(f"Card Data for {card_url}: {card_data}")

    except Exception as e:
        print(f"Error while scraping data for {card_url}: {e}")

    return card_data


# Step 3: Function to calculate profitability based on a conservative grade distribution
def calculate_profitability(card_data, grading_cost=25, selling_fee_percent=0.15):
    if None in (card_data['PSA 8'], card_data['PSA 9'], card_data['PSA 10'], card_data['Raw Price']):
        return None  # If any of the PSA prices or raw price are missing, skip this card
    
    # Conservative/hopeful grade distribution
    psa_10_count = 3
    psa_9_count = 3
    psa_8_count = 4

    # Calculate total expected revenue
    total_revenue = (
        psa_10_count * card_data['PSA 10'] +
        psa_9_count * card_data['PSA 9'] +
        psa_8_count * card_data['PSA 8']
    )

    # Calculate total cost (raw card price + grading fees)
    total_cost = 10 * card_data['Raw Price'] + 10 * grading_cost

    # Calculate selling fees
    selling_fee = total_revenue * selling_fee_percent

    # Calculate profit
    expected_profit = total_revenue - total_cost - selling_fee
    return expected_profit

# Step 4: Function to extract set name from URL
def extract_set_name(set_url):
    """Extracts the set name from the URL to use for CSV file naming."""
    set_name = re.sub(r'https://www.pricecharting.com/console/', '', set_url).title()
    return set_name

# Step 5: Main function to scrape the set page, process each card, calculate profitability, and save to CSV
def analyze_pokemon_set(set_url):
    # Initialize the WebDriver
    driver = initialize_webdriver()

    # Step 1: Get all card URLs from the set page using Selenium and scroll
    card_urls = get_card_urls(set_url, driver)

    # Close the WebDriver once done
    driver.quit()

    # Step 2: Prepare CSV file
    set_name = extract_set_name(set_url)
    csv_filename = f"{set_name}.csv"
    
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Card URL', 'Raw Price', 'PSA 8 Price', 'PSA 9 Price', 'PSA 10 Price', 'Expected Profit'])
        
        # Step 3: For each card, get PSA prices, raw price, and calculate profitability
        for card_url in card_urls:
            try:
                card_data = get_card_data(card_url)
                if card_data:
                    profit = calculate_profitability(card_data)
                    if profit is not None:
                        writer.writerow([
                            card_data['Card URL'], 
                            card_data['Raw Price'], 
                            card_data['PSA 8'], 
                            card_data['PSA 9'], 
                            card_data['PSA 10'], 
                            round(profit, 2)
                        ])
                        print(f"Expected Profit for {card_url}: ${profit:.2f}")
                    else:
                        print(f"Skipping {card_url} due to missing price data.")
            except Exception as e:
                print(f"Error processing card {card_url}: {e}")

    print(f"Data saved to {csv_filename}")

# Example entry point
if __name__ == "__main__":
    set_url = "https://www.pricecharting.com/console/pokemon-temporal-forces"
    analyze_pokemon_set(set_url)

