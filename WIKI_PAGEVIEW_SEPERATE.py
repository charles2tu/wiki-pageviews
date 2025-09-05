from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import csv
import matplotlib.pyplot as plt
import datetime
import os

search_terms = ['flu', 'influenza', 'Influenza A virus', 'Symptoms of influenza', 'Influenza symptoms', 
                   'Type A influenza', 'Flu treatment', '1918-1920 flu', 'Influenza vaccine', 'cough']
def run_script():
    # C:/Users/ctu45/Downloads/chromedriver-win64 (1)/chromedriver-win64/chromedriver.exe
    download_dir = os.getcwd()

    # Set up Chrome options to change the default download directory
    chrome_options = Options()
    prefs = {
        "download.default_directory": download_dir,  # Set download directory to current working directory
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize the Chrome driver with the options and service pointing to your ChromeDriver
    service = Service("C:/Users/ctu45/Downloads/chromedriver-win64 (1)/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    pageviews_url = 'https://pageviews.wmcloud.org/?project=en.wikipedia.org&platform=all-access&agent=user&redirects=0&range=latest-20&pages='
    search_terms = ['flu', 'influenza', 'Influenza A virus', 'Symptoms of influenza', 'Influenza symptoms', 
                   'Type A influenza', 'Flu treatment', '1918-1920 flu', 'Influenza vaccine', 'cough']
    driver.get(pageviews_url + '|'.join(search_terms))
    
    settings_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="range-input"]'))
    )
    settings_button.click()
    time.sleep(1)
    
    all_time_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[7]/div[1]/ul/li[6]'))
    )
    all_time_button.click()
    time.sleep(1)
    
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[2]/div/div/button'))
    )
    download_button.click()
    time.sleep(1)
    
    csv_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[2]/div/div/ul/li[1]/a'))
    )
    csv_button.click()
    time.sleep(10)
    driver.quit()

if __name__ == '__main__':
    run_script()

# Create a dictionary to store data for each search term
term_data = {}
today_str = datetime.date.today().strftime("%Y%m%d")
today_number = int(today_str) - 1
with open(f'pageviews-20150701-{today_number}.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    header = next(reader)  # Skip header row
    
    # Initialize dictionary only with requested search terms
    search_terms_lower = [term.lower() for term in search_terms]
    for term in header[1:]:  # Skip the date column
        if term.lower() in search_terms_lower:
            term_data[term] = []

    # Process each row
    current_week = []
    current_date = None
    day_count = 0
    
    # Get indices of columns we want to process
    valid_indices = [i for i, term in enumerate(header[1:], 1) if term.lower() in search_terms_lower]

    for row in reader:
        date = row[0]
        if current_date is None:
            current_date = date

        # If we're still within the same week (7 days)
        if day_count < 7:
            if not current_week:
                current_week = [[date], [[] for _ in range(len(valid_indices))]]
            
            # Add values only for requested terms
            for list_idx, csv_idx in enumerate(valid_indices):
                try:
                    value = int(row[csv_idx]) if row[csv_idx].strip() else 0
                    current_week[1][list_idx].append(value)
                except (ValueError, TypeError):
                    current_week[1][list_idx].append(0)
            
            day_count += 1
        
        # When we have 7 days of data, calculate weekly average
        if day_count == 7:
            # Calculate weekly averages for each term
            for term_idx, term_values in enumerate(current_week[1]):
                term_name = header[valid_indices[term_idx]]
                weekly_avg = sum(term_values) / 7
                term_data[term_name].append((current_week[0][0], weekly_avg))
            
            # Reset for next week
            current_week = []
            day_count = 0

# Plotting
plt.figure(figsize=(15, 8))
for term, data in term_data.items():
    dates = [d[0] for d in data]
    values = [d[1] for d in data]
    plt.plot(dates, values, label=term, marker='.')

plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.title('Weekly Average Page Views by Search Term')
plt.xlabel('Date')
plt.ylabel('Average Daily Views')
plt.tight_layout()
plt.grid(True)
plt.show()

# Save all terms to a single CSV file
with open('weekly_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    
    # Write header with only requested terms
    header_row = ['Week'] + list(term_data.keys())
    writer.writerow(header_row)
    
    # Get all unique dates
    all_dates = sorted(set(date for term in term_data.values() for date, _ in term))
    
    # Write data for each date
    for date in all_dates:
        row = [date]
        for term in term_data.keys():
            # Find the value for this term and date
            value = next((value for d, value in term_data[term] if d == date), '')
            row.append(value)
        writer.writerow(row)