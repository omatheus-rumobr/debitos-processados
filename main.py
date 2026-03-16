import undetected_chromedriver as uc
from dotenv import load_dotenv
from time import sleep
import json
import os

load_dotenv()

VERSAO_CHROME = int(os.getenv('VERSAO_CHROME'))
URL_BASE = os.getenv('URL_BASE')

driver = uc.Chrome(version_main=VERSAO_CHROME)

try:
    driver.get(URL_BASE)
    driver.maximize_window()
    
    sleep(30)
    
    cookies = driver.get_cookies()
    
    with open('cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=4, ensure_ascii=False)
    
    print(f"Cookies salvos em cookies.json ({len(cookies)} cookies encontrados)")
    
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']
    
    sleep(5)

finally:
    driver.quit()
