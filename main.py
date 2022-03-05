import re
from bs4 import BeautifulSoup as soup
from colorama import Fore
from playwright.sync_api import sync_playwright
from datetime import datetime
import os


def getTime():
    now = datetime.now()
    dt = now.strftime("%d/%m/%Y %H-%M-%S")
    return dt


def dataPath():
    path = os.path.expanduser(f'~\\Documents\\SkroutzPriceCompare\\')
    return path


def readFile():
    lines = []
    try:
        with open('links.txt', 'r') as file:
            for line in file.readlines():
                if not line.startswith(r'https://www.skroutz.gr'):
                    pass
                else:
                    lines.append(line)
        return getContent(lines)
    except FileNotFoundError:
        with open('links.txt', 'w') as _file:
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


clean_html = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
user_agent = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'


def getContent(url):
    wordcount = 0
    for line in url:
        if line.startswith('https://www.skroutz.gr'):
            wordcount += 1
        else:
            pass
    if wordcount >= 1:
        with sync_playwright() as p:
            for x in range(0, len(url)):
                if x == 0:
                    browser = p.chromium.launch_persistent_context(f'{dataPath()}' + '\\browserData',
                                                                   java_script_enabled=True,
                                                                   bypass_csp=True, user_agent=user_agent,
                                                                   locale="el-GR",
                                                                   headless=True, timezone_id='Europe/Athens')
                    page = browser.new_page()

                    page.goto(url[x] + "#shops")
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
                            pass

                    if x == len(url) - 1:
                        page.close()
                        browser.close()
                        p.stop()

                    processContent(shopName, shopPrice, productTitle, _min)
                else:
                    pass

    else:
        return print(Fore.LIGHTRED_EX,
                     "The file is not populated with links, please read the instructions and try again.")


def processContent(shopName, price, title, _min):
    path = f'{dataPath()}' + '\\data.txt'
    avg = 0

    print(Fore.LIGHTMAGENTA_EX, f'\n\n{title:^15}')

    print(Fore.LIGHTBLACK_EX, '==========================================')
    print(Fore.LIGHTYELLOW_EX, f'{"Store":<15}{"Price":>15}\n')

    try:
        for x in range(len(price)):
            if price[x] == _min and _min != price[x - 1]:
                print(Fore.LIGHTGREEN_EX, f'{shopName[x]:<15}{price[x]:>15}  <- Lowest Price')
                # avg += price[x]
            else:
                print(Fore.LIGHTWHITE_EX, f'{shopName[x]:<15}{price[x]:>15}')
                # avg += price[x]
    except IndexError:
        pass
    print(Fore.LIGHTBLACK_EX, '==========================================\n\n')

    if not os.path.isfile(path):
        with (open(path, 'w')) as _data:
            _data.write(f'\n==========================================================\n'
                        f'date: {getTime()}\n\n'
                        f'Product: {title}\n'
                        f'Average Price: {avg / 4}\n'
                        f'Lowest price: {_min}\n'
                        f'==========================================================\n')
    else:
        with (open(path, 'a')) as data:
            data.write(f'\n==========================================================\n'
                       f'date: {getTime()}\n\n'
                       f'Product: {title}\n'
                       f'Average Price: {avg / 4}\n'
                       f'Lowest price: {_min}\n'
                       f'==========================================================\n')


if __name__ == '__main__':
    readFile()
