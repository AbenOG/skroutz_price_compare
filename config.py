import os
import sys
import time
from configparser import ConfigParser
from colorama import Fore
from main import getCfg


def readConfig():
    cfg = ConfigParser()

    if not os.path.isfile('config.ini'):
        cfg.add_section('config')

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
        except PermissionError:
            return print(Fore.LIGHTRED_EX + "Insufficient permissions: \n"
                                            "Please run the script again as an Admin, or give it the appropriate permissions."), sys.exit()
        except:
            return print(
                Fore.LIGHTRED_EX + 'An unexpected error occurred, please check your entries and try again.'), sys.exit()

        print(Fore.LIGHTGREEN_EX + 'Configuration generated successfully inside the executable directory ✔\n'
                                   'Proceeding..️\n')
        time.sleep(2)
        readConfig()
    else:
        cfg.read('config.ini', encoding='UTF-8')

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

        return getCfg(cfgValues)


if __name__ == '__main__':
    readConfig()
