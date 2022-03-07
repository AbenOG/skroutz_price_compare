import itertools
import re
import sys
import time
from bs4 import BeautifulSoup as soup
from colorama import Fore
from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import platform
import threading

# This Regex will clean the tags from HTML code.
clean_html = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
user_agent = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'


def animate(done):
    for c in itertools.cycle(['.', '..', '...', '....']):
        if done():
            break
        sys.stdout.write(Fore.LIGHTCYAN_EX + '\rProcessing Information ' + c)
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write('\rDone!     ')


def getCfg(cfg, page_status):
    clear()
    return readFile(cfg, page_status)


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
    # This serves as a browser data folder.
    # Stores all the browsers' information, so it doesn't run as incognito everytime.
    # Why? Because when the status returns 429 and the user solves the captcha, the browser will not remember
    # Hence why we need to store our data.
    path = os.path.expanduser(f'~\\Documents\\SkroutzPriceCompare\\')
    return path


def readFile(cfg, page_status):
    lines = []

    # Open the links file and check all the lines that start with "https://www.skroutz.gr"
    # Then append them to the "lines" list created above.
    try:
        with open('links.txt', 'r', encoding='UTF-8') as file:
            for line in file.readlines():
                if line.startswith('https://www.skroutz.gr'):
                    lines.append(line)
                else:
                    pass
            return getContent(lines, cfg, page_status)

    # If the links.txt file is not found, it will create a new one and exit the script.
    except FileNotFoundError:
        with open('links.txt', 'w', encoding='UTF-8') as _file:
            _file.write(f'File Auto generated: {getTime()}\n'
                        f'How to use:\n'
                        f'1. Copy the Skroutz product link\n'
                        f'2. Paste\n'
                        f'3. Every new link HAS to be in a new line!\n'
                        f'4. "Don\'t Leave any whitespaces inbetween.\n'
                        f'5. Restart the program and try again\n'
                        f'Note: If the file is not set correctly no data will be displayed during runtime')
    return print(Fore.RED +
                 'File "links.txt" not found.\n'
                 'Created a new one successfully inside the executable path.\n'
                 'Please populate the txt file with links.\n'
                 'Read the file generated for instructions.'), sys.exit()


def getContent(url, cfg, page_status):
    # The script then proceeds to init playwright
    # The "X" holds the number of the URLs fetched from the script above.
    # If the "X" Equals to 0 then we initialize our browser for the first time.
    # If the "X" > 0 we just need to switch pages and go to the next one after each iteration.
    if len(url) > 0:
        # Actual non-sense.
        # But it's fancy...
        done = False
        t1 = threading.Thread(target=animate, args=(lambda: done,))
        t1.start()
        with sync_playwright() as p:
            for x in range(len(url)):
                # First we need to verify the captcha.
                # So if the status code returns 429 that means that the website is expecting us to do so.
                # Once done, proceed as usual.
                if x == 0 and page_status.status == 429:
                    browser = p.chromium.launch_persistent_context(f'{dataPath()}' + '\\browserData',
                                                                   java_script_enabled=cfg.get('js'),
                                                                   bypass_csp=cfg.get('csp'),
                                                                   user_agent=user_agent,
                                                                   locale=cfg.get('locale'),
                                                                   headless=False,
                                                                   timezone_id=cfg.get('tmz_id'),
                                                                   no_viewport=True,
                                                                   viewport=None,
                                                                   args=["--window-size=1000,720"])
                    _page = browser.new_page()
                    _page.goto('https://skroutz.gr')
                    input(Fore.LIGHTGREEN_EX + 'Please press enter when done verifying the captcha.')

                if x == 0 and page_status.ok:
                    browser = p.chromium.launch_persistent_context(f'{dataPath()}' + '\\browserData',
                                                                   java_script_enabled=cfg.get('js'),
                                                                   bypass_csp=cfg.get('csp'),
                                                                   user_agent=user_agent,
                                                                   locale=cfg.get('locale'),
                                                                   headless=cfg.get('headless'),
                                                                   timezone_id=cfg.get('tmz_id'))
                if browser:
                    page = browser.new_page()

                    # In this case we need to add "shops" in the end of the link
                    # Due to a JS script that takes you down to the store list.
                    # It is necessary for this to work.
                    if url[x].endswith('#shops'):
                        page.goto(url[x])
                    else:
                        page.goto(url[x] + "#shops")

                    # This part is where the browser scrolls down and waits 0.35 seconds for each scroll.
                    # This way it fetches way more stores.
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

                    # Init the HTML parser.
                    s = soup(content, 'html.parser')

                    # We store the values using HTML classes as the target.
                    # So "Dominant-price" is an HTML class that holds the value of the price tag.
                    # You can figure the rest by reading the variable names.

                    dominant_price = s.find_all(class_="dominant-price")
                    shop_name = s.find_all(class_="shop-name")
                    product_title = s.find_all("title")

                    shopName = []
                    shopPrice = []
                    productTitle = clean_html.sub('', str(product_title))

                    # Here we extract the values found, store them in a variable, clear the HTML tags,
                    # Then we append each to its respected list created above.
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
                            # Sometimes it throws a value error when it tries to grab more prices than there are shops.
                            # Because for each product there is a store selling the product, and each product has a price.
                            # If it gets more prices than it gets products or shops respectively then it throws a value error.
                            # So it's optimal to break the script and proceed.
                            break
                    # Finally, if we iterate to the end of the list, close the browsers and pages.
                    # Else we get an I/O error and a warning that we left them open (apparently he doesn't like that).
                    if x == len(url) - 1:
                        page.close()
                        browser.close()
                        p.stop()
                        done = True
                        t1.join()

                    processContent(shopName, shopPrice, productTitle, _min)
    else:
        clear()
        print(Fore.RED + 'Invalid OR No links inside the list, populate the list and try again.')
        return sys.exit()


def processContent(shopName, price, title, _min):
    path = f'{dataPath()}' + '\\data.txt'
    avg = 0
    prodCount = 0

    # Here we display all the content to the end user.
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

    # Here we save everything to our data file created in "dataPath".
    # There we can analyze further how many stores sell the "X" product, the average price, and the lowest price.
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
        return print(Fore.RED + 'Zero division error, meaning no products were added.\n'
                                '1. The website is offline or your internet connection dropped.\n'
                                '2. The website thinks you are a robot due to many requests and requires further manual verification\n'
                                '3. The links you provided are invalid.\n'
                                'If number 2 is true, rerun the program and solve the captcha.'), sys.exit()
