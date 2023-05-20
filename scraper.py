from selenium import webdriver
import json
import os
import argparse
import pyautogui as pt
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import pyperclip



DRIVER_PATH = r'C:\Users\Asus\Downloads\geckodriver-v0.33.0-win32\geckodriver.exe'
BASE_URL = r'https://platesmania.com/'
DOWNLOAD_DIR = r'E:\Projects\Self\LPR_Data_Scraping\data'

options = Options()
options.binary_location = r''
options.set_preference('browser.download.folderList', 2)
options.set_preference('browser.download.dir', DOWNLOAD_DIR)
driver = webdriver.Firefox(service=Service(DRIVER_PATH), options=options)
driver.maximize_window()


def get_mappings(json_file, key):
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data[key]


def get_vehicle_info(driver, url):

    driver.get(url)

    vehicle_imgs = driver.find_elements(By.CSS_SELECTOR, 'img.img-responsive.center-block')
    plate_imgs = driver.find_elements(By.CSS_SELECTOR, 'img.img-responsive.center-block.margin-bottom-10')
    vehicle_models = driver.find_elements(By.CSS_SELECTOR, 'h4.text-center')

    vehicle_srcs = [img.get_attribute('src') for img in vehicle_imgs if '/m/' in img.get_attribute('src')]

    plate_texts = []
    vehicle_srcs_new = []
    model_names = []

    for i, img in enumerate(plate_imgs):
        plate_text = img.get_attribute('alt')
        if plate_text:
            plate_texts.append(plate_text)
            vehicle_srcs_new.append(vehicle_srcs[i].replace('/m/', '/o/'))
            model_names.append(vehicle_models[i].text)
    
    return vehicle_srcs_new, plate_texts, model_names


def save_image(seconds, filename):

    try:
        time.sleep(seconds)
        pt.hotkey('Ctrl', 's')
        time.sleep(seconds)
        pyperclip.copy(filename)
        pt.write(filename, interval=seconds)
        time.sleep(seconds)
        pt.press('enter')
        time.sleep(seconds)
            
    except Exception as e:
        print(f'FAILED - {e}')


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='json file containing country and their code mappings')
    parser.add_argument('--key', type=str, default='Continent', help='key to be searched inside a json file')
    parser.add_argument('--save-dir', type=str, default=DOWNLOAD_DIR, help='downloaded images save directory')
    args = parser.parse_args()
    
    return args


def main(args):

    vehicles_visited_srcs = []
    sep = '__'
    seconds = 0.1
    counts = {}
    countries = ['Egypt', 'Turkey', 'Iran', 'Iraq', 'Saudi Arabia', 'Yemen', 'Syria', 'Jordan', 'UAE', 'Israel', \
                 'Lebanon', 'Palestinian Authority', 'Oman', 'Kuwait', 'Qatar', 'Bahrain']
                 
    visited_countries = ['Israel', 'Saudi Arabia', 'Palestinian Authority', 'Turkey', 'UAE']

    data = get_mappings(args.file, args.key)

    for continent, country_details in data.items():

        for country, details in country_details.items():
                
            if country in countries and country not in visited_countries:

                print(f'Downloading images for {country}...')

                country_code, total_imgs = details
                country_url = BASE_URL + country_code + '/gallery'
                n_pages = total_imgs // 10

                for page in range(1, n_pages):
                    
                    url = country_url if page == 1 else country_url + '-' + str(page)

                    vehicle_srcs, plate_texts, model_names = get_vehicle_info(driver, url)
                    
                    for i, vehicle_src in enumerate(vehicle_srcs):

                        if vehicle_src not in vehicles_visited_srcs:

                            plate_text = plate_texts[i]
                            model_name = model_names[i]
                            img_name = country + sep + model_name + sep + plate_text
                            img_name = img_name.replace('/', '')

                            counts[img_name] = counts.get(img_name, 0) + 1
                            img_name += sep + str(counts[img_name])
                            
                            time.sleep(seconds)
                            driver.execute_script("window.open('');")
                            driver.switch_to.window(driver.window_handles[1])
                            driver.get(vehicle_src)
                    
                            save_image(seconds=seconds, filename=img_name)

                            vehicles_visited_srcs.append(vehicle_src)
                            
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            driver.back()

                            time.sleep(seconds)

                        else:
                            print('Image already exists... Moving to the next URL')

        country_imgs = [img for img in os.listdir(args.save_dir) if img.startswith(country)]
        print(f'Total {len(country_imgs)} images downloaded for {country}...')

    driver.close()
    
    total_downloaded_imgs = len(os.listdir(args.save_dir))

    print(f'Total {total_downloaded_imgs} images downloaded and saved to {args.save_dir}...')


if __name__ == "__main__":

    args = parse_args()
    main(args)