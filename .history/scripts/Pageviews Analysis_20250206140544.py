from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import csv
import matplotlib.pyplot as plt

#I used cron to run this script at 2 am

def run_script():
    service = Service("C:/Users/ctu45/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")    
    driver = webdriver.Chrome(service=service)

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
with open('pageviews-20150701-20250205.csv') as csvfile:
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
with open('weekly_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Week', 'Average Page Visits per Day'])
    writer.writerows(relative_values)
