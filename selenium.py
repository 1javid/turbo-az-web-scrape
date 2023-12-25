from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm

chrome_browser = webdriver.Chrome()

# Get all product links from all pages
product_links = []

for page_number in range(1, 32):
    url = f"https://turbo.az/autos?page={page_number}&q%5Bbarter%5D=0&q%5Bcrashed%5D=1&q%5Bcurrency%5D=azn&q%5Bengine_volume_from%5D=&q%5Bengine_volume_to%5D=&q%5Bfor_spare_parts%5D=0&q%5Bloan%5D=0&q%5Bmake%5D%5B%5D=4&q%5Bmileage_from%5D=&q%5Bmileage_to%5D=&q%5Bmodel%5D%5B%5D=&q%5Bmodel%5D%5B%5D=172&q%5Bonly_shops%5D=&q%5Bpainted%5D=1&q%5Bpower_from%5D=&q%5Bpower_to%5D=&q%5Bprice_from%5D=&q%5Bprice_to%5D=&q%5Bregion%5D%5B%5D=&q%5Bsort%5D=&q%5Bused%5D=&q%5Byear_from%5D=&q%5Byear_to%5D="
    chrome_browser.get(url)

    # Find all product links on the current page
    product_divs = chrome_browser.find_elements(By.CLASS_NAME, 'products-i')
    for product_div in product_divs:
        product_link = product_div.find_element(By.CLASS_NAME, 'products-i__link').get_attribute('href')
        product_links.append(product_link)

# List to store car information
car_info_list = []

progress_bar = tqdm(total=len(product_links), desc="Processing Car Cards", dynamic_ncols=True)

for car_card_url in product_links:
    try:
        chrome_browser.get(car_card_url)

        if "Axtardığınız elan tapılmadı!" in chrome_browser.page_source:
            continue

        properties = chrome_browser.find_elements(By.CSS_SELECTOR, '.product-properties__i')

        car_info = {}
        for prop in properties:
            label = prop.find_element(By.CLASS_NAME, 'product-properties__i-name').text
            value = prop.find_element(By.CLASS_NAME, 'product-properties__i-value').text
            car_info[label] = value

            azn_price_element = chrome_browser.find_element(By.CLASS_NAME, 'product-price__i--bold')

            if "AZN" in azn_price_element.text:
                azn_price = azn_price_element.text
            else:
                azn_price = chrome_browser.find_element(By.CLASS_NAME, 'product-price__i').text.split('≈')[-1].strip()

            car_info['Qiymət'] = azn_price

        car_info_list.append(car_info)

        progress_bar.update(1)

        time.sleep(4)

    except TimeoutException as e:
        print(f"Timeout occurred for {car_card_url}. Skipping to the next car card.")

chrome_browser.quit()

df = pd.DataFrame(car_info_list)

df.to_csv('car_information.csv', index=False)
