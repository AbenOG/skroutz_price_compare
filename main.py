import re
from bs4 import BeautifulSoup as soup
from colorama import Fore
from playwright.sync_api import sync_playwright
from time import sleep


def readFile(path):
    try:
        with open(file=path, mode='r') as file:
            line = []
            for lines in file.readlines():
                line.append(lines)
            return getContent(line)
    except FileNotFoundError:
        return print('The file specified does not exist.')


clean_html = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
user_agent = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'


def getContent(url):
    with sync_playwright() as p:
        for x in range(0, len(url)):
            if x == 0:
                browser = p.chromium.launch_persistent_context(r'C:\Users\aben\Downloads\temp',
                                                               java_script_enabled=True,
                                                               bypass_csp=True, user_agent=user_agent,
                                                               locale="el-GR",
                                                               headless=True, timezone_id='Europe/Athens')
                page = browser.new_page()

            page.goto(url[x])
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
                    shopPrice.append(float(cleanPrice.replace('.', '').replace(",", "").replace("€", "")) / 100)

                    _min = min(shopPrice, default=0)

                except ValueError:
                    pass

            if x == len(url) - 1:
                page.close()
                browser.close()
                p.stop()

            processContent(shopName, shopPrice, productTitle, _min)


def processContent(shopName, price, title, _min):
    print(Fore.LIGHTMAGENTA_EX, f'\n\n{title:^15}')

    print(Fore.LIGHTBLACK_EX, '==========================================')
    print(Fore.LIGHTYELLOW_EX, f'{"Store":<15}{"Price":>15}\n')

    try:
        for x in range(len(price)):
            if price[x] == _min and _min != price[x - 1]:
                print(Fore.LIGHTGREEN_EX, f'{shopName[x]:<15}{price[x]:>15}  <- Lowest Price')

            else:
                print(Fore.LIGHTWHITE_EX, f'{shopName[x]:<15}{price[x]:>15}')
    except IndexError:
        pass
    print(Fore.LIGHTBLACK_EX, '==========================================\n\n')


if __name__ == '__main__':
    readFile(r"C:\Users\aben\Documents\test\links.txt")
