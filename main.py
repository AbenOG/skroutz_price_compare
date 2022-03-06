import re
import sys
import time

from bs4 import BeautifulSoup as soup
from colorama import Fore
from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import platform

clean_html = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
user_agent = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'


def getCfg(cfg):
    clear()
    return readFile(cfg)


def clear():
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        return os.system('clear')
    else:
        return os.system('cls')


def getTime():
    now = datetime.now()
    dt = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt


def dataPath():
    path = os.path.expanduser(f'~\\Documents\\SkroutzPriceCompare\\')
    return path


def readFile(cfg):
    lines = []
    with open('links.txt', 'r', encoding='UTF-8') as file:
        try:
            for line in file.readlines():
                if line.startswith('https://www.skroutz.gr'):
                    lines.append(line)
                else:
                    pass
            return getContent(lines, cfg)
        except FileNotFoundError:
            with open('links.txt', 'w', encoding='UTF-8') as _file:
                _file.write(f'File Auto generated: {getTime()}\n'
                            f'How to use:\n'
                            f'1. Copy the Skroutz product link\n'
                            f'2. Paste\n'
                            f'3. Every new link HAS to be in a new line!\n'
                            f'4. Restart the program and try again\n'
                            f'Note: If the file is not set correctly no data will be displayed during runtime')
            return print(Fore.LIGHTRED_EX,
                         'File (links.txt) not found.\n'
                         'Generated a new one successfully inside the executable path.\n'
                         'Please populate the txt file with links.\n'
                         'Read the file generated for instructions.')


def getContent(url, cfg):
    doneCaptcha = None

    with sync_playwright() as p:
        if len(url) > 0:
            print(Fore.LIGHTGREEN_EX + 'Loading data..\n')
            for x in range(0, len(url)):
                if x == 0 and cfg.get('iscaptcha') and not doneCaptcha:
                    browser = p.chromium.launch_persistent_context(f'{dataPath()}' + '\\browserData',
                                                                   java_script_enabled=cfg.get('js'),
                                                                   bypass_csp=cfg.get('csp'),
                                                                   user_agent=user_agent,
                                                                   locale=cfg.get('locale'),
                                                                   headless=cfg.get('headless'),
                                                                   timezone_id=cfg.get('tmz_id'),
                                                                   no_viewport=True,
                                                                   viewport=None,
                                                                   args=["--window-size=1000,720"],
                                                                   timeout=20000)
                    _page = browser.new_page()
                    _page.goto('https://skroutz.gr')
                    input(Fore.LIGHTRED_EX + 'Please press enter when done verifying the captcha.')
                    doneCaptcha = True

                if x == 0 and cfg.get('iscaptcha') and doneCaptcha:
                    browser.close()
                    browser = p.chromium.launch_persistent_context(f'{dataPath()}' + '\\browserData',
                                                                   java_script_enabled=cfg.get('js'),
                                                                   bypass_csp=cfg.get('csp'),
                                                                   user_agent=user_agent,
                                                                   locale=cfg.get('locale'),
                                                                   headless=cfg.get('headless'),
                                                                   timezone_id=cfg.get('tmz_id'),
                                                                   no_viewport=True,
                                                                   viewport=None,
                                                                   args=["--window-size=600,480"])
                if x == 0 and not cfg.get('iscaptcha'):
                    browser = p.chromium.launch_persistent_context(f'{dataPath()}' + '\\browserData',
                                                                   java_script_enabled=cfg.get('js'),
                                                                   bypass_csp=cfg.get('csp'),
                                                                   user_agent=user_agent,
                                                                   locale=cfg.get('locale'),
                                                                   headless=cfg.get('headless'),
                                                                   timezone_id=cfg.get('tmz_id'))
                if browser:
                    page = browser.new_page()

                    if url[x].endswith('#shops'):
                        page.goto(url[x])
                    else:
                        page.goto(url[x] + "#shops")

                    time.sleep(.35)
                    page.mouse.wheel(0, 2000)
                    time.sleep(.25)
                    page.mouse.wheel(0, 2000)
                    time.sleep(.25)
                    page.mouse.wheel(0, 2000)
                    time.sleep(.25)
                    page.mouse.wheel(0, 2000)
                    time.sleep(.25)
                    page.mouse.wheel(0, 2000)
                    time.sleep(.25)
                    page.mouse.wheel(0, 2000)
                    time.sleep(.25)
                    page.mouse.wheel(0, 2000)
                    time.sleep(.25)
                    content = page.content()

                    s = soup(content, 'html.parser')

                    dominant_price = s.find_all(class_="dominant-price")
                    shop_name = s.find_all(class_="shop-name")
                    product_title = s.find_all("title")

                    shopName = []
                    shopPrice = []
                    productTitle = clean_html.sub('', str(product_title))

                    for names in shop_name:
                        newName = str(names)
                        cleanName = clean_html.sub('', newName)
                        shopName.append(cleanName)

                    for price in dominant_price:
                        newPrice = str(price)
                        cleanPrice = clean_html.sub('', newPrice)
                        try:
                            shopPrice.append(
                                float(cleanPrice.replace('.', '').replace(",", "").replace("€", "")) / 100)

                            _min = min(shopPrice, default=0)
                        except ValueError:
                            break

                    if x == len(url) - 1:
                        page.close()
                        browser.close()
                        p.stop()

                    processContent(shopName, shopPrice, productTitle, _min)
        else:
            clear()
            print(Fore.LIGHTRED_EX + 'No links inside the list, populate the list and try again.')
            return p.stop()


def processContent(shopName, price, title, _min):
    path = f'{dataPath()}' + '\\data.txt'
    avg = 0
    prodCount = 0

    print(Fore.LIGHTMAGENTA_EX + f'\n\n{title:^15}')

    print(Fore.LIGHTBLACK_EX + '===============================================================')
    print(Fore.LIGHTYELLOW_EX + f'{"Store":<22}{"Price":>35}\n')

    try:
        for x in range(len(price)):
            if price[x] == _min and _min != price[x - 1]:
                print(Fore.LIGHTGREEN_EX + f'{shopName[x]:<22}{price[x]:>35}  <- Lowest Price')
                avg += price[x]
                prodCount += 1
            else:
                print(Fore.LIGHTWHITE_EX + f'{shopName[x]:<22}{price[x]:>35}')
                avg += price[x]
                prodCount += 1
    except IndexError:
        pass
    print(Fore.LIGHTBLACK_EX + '===============================================================\n\n')

    try:
        if not os.path.isfile(path):
            with (open(path, 'w', encoding='UTF-8')) as _data:

                _data.write(f'==========================================================\n'
                            f'date: {getTime()}\n\n'
                            f'Product: {title}\n'
                            f'Average Price: {avg / prodCount:.2f} From {prodCount} different stores\n'
                            f'Lowest price: {_min}\n\n')
        else:
            with (open(path, 'a', encoding='UTF-8')) as data:
                data.write(f'==========================================================\n'
                           f'date: {getTime()}\n\n'
                           f'Product: {title}\n'
                           f'Average Price: {avg / prodCount:.2f} From {prodCount} different stores\n'
                           f'Lowest price: {_min}\n\n')
    except ZeroDivisionError:
        return print(Fore.LIGHTRED_EX + 'Zero division error, meaning no products were added.\n'
                                        '1. The website is offline or your internet connection dropped.\n'
                                        '2. The website thinks you are a robot due to many requests and requires further manual verification\n'
                                        '3. The links you provided are invalid.\n'
                                        'If number 2 is true, rerun the program and solve the captcha.'), sys.exit()
