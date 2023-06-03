# PlatesMania-Scraper
A repository to scrape License Plates Data from (platesmania.com)[https://platesmania.com/].   

## Install

1.  Download Webdriver
    - Chrome: [chromedriver](https://chromedriver.chromium.org/downloads) 

2. Set-up Project

    ```
    git clone https://github.com/harshdhamecha/PlatesMania-Scraper.git
    cd PlatesMania-Scraper
    ```

3. Set-up Conda Environment
    ```
    conda create --name scrape --file requirements.txt
    conda activate scrape
    ```

## Usage

```
# Run scraper
python scraper.py --save-dir ./data --country UAE 
```
