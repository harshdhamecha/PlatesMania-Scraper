'''
 	@author 	 harsh-dhamecha
 	@email       harshdhamecha10@gmail.com
 	@create date 2023-05-20 08:37:21
 	@modify date 2023-06-03 12:24:56
 	@desc        A script to scrape license plates data from platesmania.com
 '''


from selenium import webdriver
import json
import os
import argparse
import pyautogui as pt
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip



class PlatesManiaScraper():

    def __init__(self, args):

        self.driver = webdriver.Chrome(service=Service(executable_path=args.driver_path))
        self.base_url = args.base_url
        self.countries_code_file = args.countries_code
        self.key = args.key
        self.short_wait = args.short_wait
        self.long_wait = args.long_wait
        self.start_idx = args.start_idx
        self.end_idx = args.end_idx
        self.country = args.country
        self.country_code = self.get_mappings()
        self.last_page = ''
        self.save_dir = args.save_dir
        self.sep = args.sep
        self.count = {}


    def exception_handler(func):

        def inner_function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f'FAILED - {e}')

        return inner_function


    @property
    @exception_handler
    def url_sep(self):
        return '' if len(self.last_page) == 0 else '-'


    @property
    @exception_handler
    def url(self):
        return f'{self.base_url}/{self.country_code}/gallery{self.url_sep}{self.last_page}'


    @exception_handler
    def get_mappings(self):

        with open(self.countries_code_file) as f:
            data = json.load(f)[self.key]
        return data[self.country] if self.country in data else ''


    @exception_handler
    def get_img_srcs(self):
        
        vehicle_imgs = WebDriverWait(self.driver, self.long_wait)\
            .until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img.img-responsive.center-block')))
        return [img.get_attribute('src').replace('/m/', '/o/') for img in vehicle_imgs if '/m/' in img.get_attribute('src')]


    @exception_handler
    def get_plate_texts(self):

        plate_imgs = WebDriverWait(self.driver, self.long_wait)\
            .until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img.img-responsive.center-block.margin-bottom-10')))
        return [img.get_attribute('alt') for img in plate_imgs]


    @exception_handler
    def save_image(self, path):

        time.sleep(self.short_wait)
        pt.hotkey('ctrl', 's')
        time.sleep(self.short_wait)
        pyperclip.copy(path)
        time.sleep(self.short_wait)
        pt.hotkey('ctrl', 'v')
        time.sleep(self.short_wait)
        pt.press('enter')
        time.sleep(self.short_wait)
        

    @exception_handler
    def scrape(self):

        os.makedirs(self.save_dir, exist_ok=True)
        
        for page in range(self.start_idx, self.end_idx):
            
            self.driver.get(self.url)

            img_srcs = self.get_img_srcs()
            plate_texts = self.get_plate_texts()

            for i, img_src in enumerate(img_srcs):
                
                plate_text = plate_texts[i].replace(' ', '-')
                count = str(self.count.get(plate_text, 0) + 1)
                self.count[plate_text] += 1
                
                img_name = f'{self.sep}'.join([self.country, plate_text, count]) + '.jpg'
                path = os.path.join(self.save_dir, img_name)

                self.driver.get(img_src)

                self.save_image(path)

            self.last_page = str(page)


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--driver-path', default='./chromedriver.exe', type=str, help='webdriver path')
    parser.add_argument('--country', default='UAE', type=str, help='country name whose license plates to be scraped')
    parser.add_argument('--countries-code', default='./countries.json', type=str, help='json file containing country and their code mappings')
    parser.add_argument('--key', type=str, default='Country', help='key to be searched inside a json file')
    parser.add_argument('--save-dir', type=str, help='downloaded images save directory')
    parser.add_argument('--base-url', type=str, default='https://platesmania.com', help='base url from which to scrape')
    parser.add_argument('--start-idx', type=int, default=1, help='page from which to start scraping')
    parser.add_argument('--end-idx', type=int, default=100, help='page at which to end scraping')
    parser.add_argument('--short-wait', type=int, default=0.3, help='shorter wait for webdriver')
    parser.add_argument('--long-wait', type=int, default=5, help='longer wait for webdriver')
    parser.add_argument('--sep', type=str, default='_', help='separator for img-name')
    args = parser.parse_args()
    
    return args


def main(args):

    scraper = PlatesManiaScraper(args)
    scraper.scrape()


if __name__ == "__main__":

    args = parse_args()
    main(args)