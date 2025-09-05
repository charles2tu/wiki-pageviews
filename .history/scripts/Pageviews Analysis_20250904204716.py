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
import os
from datetime import datetime
from datetime import timedelta
import tempfile


  # e.g. 20250903

#I used cron to run this script at 2 am
yesterday_str = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")

def run_script():
    # today_str = datetime.today().strftime("%Y%m%d")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # points to wiki/
    download_dir = os.path.join(base_dir, "csv_downloads")
    os.makedirs(download_dir, exist_ok=True)
    file_name = os.path.join(download_dir,f'pageviews-20150701-{yesterday_str}.csv')
    if os.path.exists(file_name):
        os.remove(file_name)
    # Chrome options for custom download path
    chrome_prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    opts = Options()
    opts.add_experimental_option("prefs", chrome_prefs)
    driver = webdriver.Chrome(options=opts)

    pageviews_url = 'https://pageviews.wmcloud.org/?project=en.wikipedia.org&platform=all-access&agent=user&redirects=0&range=latest-20&pages='
    search_terms = ['flu', 'influenza', 'Influenza A virus', 'Symptoms of influenza', 'Influenza symptoms', 'Type A influenza', 'Flu treatment', '1918-1920 flu', 'Influenza vaccine', 'cough']
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

combined_rows = []
#filename = 'insert file name here'
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
download_dir = os.path.join(base_dir, "csv_downloads")

# build full path to your file
file_name = os.path.join(download_dir,f'pageviews-20150701-{yesterday_str}.csv')
with open(file_name) as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    counter = 0
    for row in reader:
        print(row)
        splitrow = row[0].split(',')
        if counter >= 1:
            splitrow[1] = int(splitrow[1])
        combined_rows.append(splitrow)
        print(splitrow)
        counter += 1
arranged = sorted(combined_rows[1:], key=lambda x: x[1])
counter = 0
total = 0
for row in arranged:
    total += row[1]
    counter += 1
mean = int((total / counter + 1) // 1)
median = arranged[len(arranged) // 2][1]
relative_values = []
i = 1
pair = []
sum = 0
for row in combined_rows[1:]:
    if i == 1:
        pair.append(row[0])
        print(pair)
    sum += row[1]
    if i == 7:
        pair.append(sum / 7)
        relative_values.append(pair)
        pair = []
        i = 0
        sum = 0
    i += 1
print(mean)
dates = []
values = []
counter = 0
month_list = []
for row in relative_values:
    if row[0][5:7] not in month_list:
        month_list.append(row[0][5:7])
        dates.append(row[0])
    else:
        dates.append(' ' * counter)
    values.append(row[1])
    counter += 1
plt.plot(dates, values)
plt.tick_params(axis='x', labelrotation=90)
plt.show()
print(mean)
print(median)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # wiki/
weekly_dir = os.path.join(base_dir, "weekly_data")
os.makedirs(weekly_dir, exist_ok=True)

# Date-stamped filename to keep history
weekly_csv = os.path.join(weekly_dir, f"weekly_data_{yesterday_str}.csv")
if os.path.exists(weekly_csv):
    os.remove(weekly_csv)
with open(weekly_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Week", "Average Page Visits per Day"])
    writer.writerows(relative_values)

print(f"Wrote: {weekly_csv}")
