import re
from bs4 import BeautifulSoup as soup
from colorama import Fore
from playwright.sync_api import sync_playwright
from datetime import datetime
import os

clean_html = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
user_agent = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'


def getTime():
    now = datetime.now()
    dt = now.strftime("%d/%m/%Y %H-%M-%S")
    return dt


def dataPath():
    path = os.path.expanduser(f'~\\Documents\\SkroutzPriceCompare\\')
    return path


def readFile():
    lines = []
    with open('links.txt', 'r', encoding='UTF-8') as file:
        try:
            for line in file.readlines():
                if line.startswith('https://www.skroutz.gr'):
                    lines.append(line)
                else:
                    pass
            return getContent(lines)
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


def getContent(url):
    with sync_playwright() as p:
        if len(url) > 0:
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
            os.system('cls')
            print(Fore.LIGHTRED_EX, 'No links inside the list, populate the list and try again.')
            return p.stop()


def processContent(shopName, price, title, _min):
    path = f'{dataPath()}' + '\\data.txt'
    avg = 0
    prodCount = 0

    print(Fore.LIGHTMAGENTA_EX, f'\n\n{title:^15}')

    print(Fore.LIGHTBLACK_EX, '==========================================')
    print(Fore.LIGHTYELLOW_EX, f'{"Store":<15}{"Price":>15}\n')

    try:
        for x in range(len(price)):
            if price[x] == _min and _min != price[x - 1]:
                print(Fore.LIGHTGREEN_EX, f'{shopName[x]:<15}{price[x]:>15}  <- Lowest Price')
                avg += price[x]
                prodCount += 1
            else:
                print(Fore.LIGHTWHITE_EX, f'{shopName[x]:<15}{price[x]:>15}')
                avg += price[x]
                prodCount += 1
    except IndexError:
        pass
    print(Fore.LIGHTBLACK_EX, '==========================================\n\n')

    if not os.path.isfile(path):
        with (open(path, 'w', encoding='UTF-8')) as _data:

            _data.write(f'==========================================================\n'
                        f'date: {getTime()}\n\n'
                        f'Product: {title}\n'
                        f'Average Price: {avg / prodCount:.2f}\n'
                        f'Lowest price: {_min}\n\n')
    else:
        with (open(path, 'a', encoding='UTF-8')) as data:
            data.write(f'==========================================================\n'
                       f'date: {getTime()}\n\n'
                       f'Product: {title}\n'
                       f'Average Price: {avg / prodCount:.2f}\n'
                       f'Lowest price: {_min}\n\n')


if __name__ == '__main__':
    readFile()
