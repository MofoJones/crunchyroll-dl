import time
import logging
import subprocess
import tempfile
from selenium import webdriver

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())


def main():
    username = input('Username: ')
    password = input('Password: ')
    url = input('URL: ')
    youtube_dl_params = input('youtube_dl params: ')

    driver = webdriver.Chrome()
    driver.get('http://www.crunchyroll.com/login')
    while "Just a moment" in driver.title:
        LOGGER.info('Waiting for Cloudflare.')
        time.sleep(1)

    cookie_tempfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
    cookies = driver.get_cookies()
    cookie_file_name = create_cookie_file(cookies, cookie_tempfile)
    LOGGER.debug(cookie_file_name)
    agent = driver.execute_script("return navigator.userAgent")
    LOGGER.debug(agent)
    arguments = '{} --verbose --user-agent "{}" -u {} -p {} --cookies {} ' \
                '-f best'.format(
                    url, agent, username, password, cookie_file_name
                )
    command = ['youtube-dl', arguments + youtube_dl_params]
    LOGGER.debug(command)
    subprocess.Popen(command)
    input('press enter to quit')
    driver.close()


def create_cookie_file(cookies, cookie_file):
    """
    Take a list of webdriver cookie dictionaries and create a
    netscape cookie file.
    """
    cookie_file.write('# Netscape HTTP Cookie File')
    for cookie in cookies:
        fix_crunchyroll_cookie_issues(cookie)
        cookie_file.write(cookie_dict_to_cookie_line(cookie))
    cookie_file.close()
    return cookie_file.name


def fix_crunchyroll_cookie_issues(cookie):
    """
    Fix the cookie issues encountered by youtube_dl.
    :param cookie: single cookie received from chromedriver
    :type cookie: dictionary
    """
    cookie_issues_list = ['__qca', '_ga', '_gid']
    for issue in cookie_issues_list:
        if issue == cookie['name']:
            cookie['httpOnly'] = True


def cookie_dict_to_cookie_line(cookie):
    """
    Convert a cookie dictionary to a netscape cookie line.
    :param cookie: dictionary of cookies as obtained from
    selenium.webdriver.get_cookies()
    :return: string in the format of a line in the cookie file.
    """
    keys = ('domain', 'httpOnly', 'path', 'secure', 'expiry', 'name', 'value')
    cookie = populate_dict_with_missing_keys(cookie, keys)
    cookie_line = "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
        cookie['domain'],
        str(cookie['httpOnly']).upper(),
        cookie['path'],
        str(cookie['secure']).upper(),
        cookie['expiry'],
        cookie['name'],
        cookie['value']
    )
    return cookie_line


def populate_dict_with_missing_keys(flawed_dict, keys):
    """
    Ensure a dict has all the keys by populating it
    with empty values. (Destructive method)
    :param flawed_dict: dictionary possibly containing missing fields.
    :param keys: Tuple of required keys.
    :return: dictionary with all the keys.
    """
    for key in keys:
        if not key in flawed_dict:
            flawed_dict[key] = ''
    return flawed_dict


if __name__ == '__main__':
    main()
