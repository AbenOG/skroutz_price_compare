import os
import sys
import time
from configparser import ConfigParser
from colorama import Fore
from main import getCfg, dataPath, clear
from playwright.sync_api import sync_playwright



def readConfig():
    with sync_playwright() as p:
        # Here we need to Launch our Chromium browser to save the webpage status.
        # So before we proceed we can check wether the website is up, down, or we do have an internet connection.
        browser = p.chromium.launch_persistent_context(f'{dataPath()}' + '\\browserData')
        page = browser.new_page()
        page_status = page.goto('https://www.skroutz.gr')

    # Init the config parser.
    cfg = ConfigParser()

    # Check if config file exists
    # And if it doesn't create a new cfg file.
    if not os.path.isfile('config.ini'):
        cfg.add_section('config')

        # Set the configuration section option and value.
        cfg.set('config', 'javascript', 'True')
        cfg.set('config', 'bypass_csp', 'True')
        cfg.set('config', 'locale', 'en-US')
        cfg.set('config', 'timezone_id', 'Europe/Athens')
        cfg.set('config', 'headless', 'True')

        try:
            with open('config.ini', 'w') as configfile:
                configfile.write('# This is a standard configuration file.\n'
                                 '# This helps you get around tricky situations and debug issues within a webpage.\n'
                                 '# Javascript : Enables or Disables Javascript.\n'
                                 '# Bypass_csp: Bypasses browsers content security policy in-case you are visiting an unsafe website.\n'
                                 '# Locale: Changes the websites locale and displays it in specified language.\n'
                                 '# Headless: Run the browser in headless mode by default this is Enabled.\n'
                                 '# Timezone ID: This changes the timezone within the website.\n\n')
                cfg.write(configfile)

        # Some OS's like Linux or macOS might need extended permissions to perform this action.
        except PermissionError:
            return print(Fore.LIGHTRED_EX + "Insufficient permissions: \n"
                                            "Please run the script again as an Admin, or give it the appropriate permissions."), sys.exit()

        print(Fore.LIGHTGREEN_EX + 'Configuration generated successfully inside the executable directory ✔\n'
                                   'Proceeding..️\n')
        time.sleep(2)
        readConfig()

    # If the Configuration file exists, read the values and proceed.
    else:
        cfg.read('config.ini', encoding='UTF-8')

        # Check if the page status is either OK or needs captcha verification.
        if page_status.ok or page_status.status == 429:
            js = cfg.getboolean('config', 'javascript')
            bypass_csp = cfg.getboolean('config', 'bypass_csp')
            locale = cfg.get('config', 'locale')
            tmz_id = cfg.get('config', 'timezone_id')
            headless = cfg.getboolean('config', 'headless')

            cfgValues = {
                'js': js,
                'csp': bypass_csp,
                'locale': locale,
                'tmz_id': tmz_id,
                'headless': headless
            }

            # Send warning + helpful instructions if the website blocked users network from too many requests.
            if page_status.status == 429:
                print(Fore.LIGHTRED_EX + '\n!! WARNING !! >[HEADLESS MODE TEMPORARILY DISABLED]<\n'
                                         '========================================================\n'
                                         'Because of the unusual number of requests coming from your network\n'
                                         'Skroutz.gr has blocked your access unless you verify you\'re not a robot\n'
                                         'Headless mode will not work during this phase, usually for about an hour or two.\n'
                                         'For now this is the only way to get through this.\n'
                                         'After you verify and solve the captcha, please press the Enter key button on your keyboard.\n'
                                         'While in this phase, the program will continue starting in windowed mode instead until it goes back to normal.\n')
                print(Fore.LIGHTYELLOW_EX +
                      'Note:\n'
                      'Even after verification, the program will continue to execute in windowed mode.\n'
                      'Headless mode is different than just opening a regular browser.\n'
                      'The only thing you can do during this phase is to wait for it to cooldown.\n')
                input(Fore.LIGHTWHITE_EX + 'Press enter to continue..')
                clear()
                return getCfg(cfgValues, page_status)
            return getCfg(cfgValues, page_status)
        else:
            print(
                Fore.LIGHTRED_EX + 'Site or internet connection Offline, please check your network configuration and try again.')


if __name__ == '__main__':
    readConfig()
