import time
import logging
import subprocess
import tempfile
import os
from getpass import getpass

from selenium import webdriver

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(logging.StreamHandler())


def main(username, password, url, youtube_dl_params):
    """Download video from crunchyroll.

    :param username: Username for the account
    :type username: str
    :param password: Password for the account
    :type password: str
    :param url: URL to the video or series overview page
    :type url: str
    :param youtube_dl_params: extra space seperated parameters accepted by youtube_dl
    :type youtube_dl_params: str
    """
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
    command = [
        'youtube-dl', url, '--user-agent', '{}'.format(agent), '-u', username, '-p',
        password, '--cookies', cookie_file_name, '-f', 'best'
    ]
    command.extend(youtube_dl_params.split(' '))
    command_debug = command.copy()
    command_debug[5] = '******'
    command_debug[7] = '******'
    LOGGER.debug(command_debug)
    driver.close()
    subprocess.run(command)


def create_cookie_file(cookies, cookie_file):
    """Take a list of webdriver cookie dictionaries and create a netscape cookie file.

    :param cookies: Webdriver cookie dictionary.
    :type cookies: dict
    :param cookie_file: file object to make a netscape cookie file opened with 'w'
    :type cookie_file: file
    """
    cookie_file.write('# Netscape HTTP Cookie File\n\n')
    for cookie in cookies:
        fix_crunchyroll_cookie_issues(cookie)
        cookie_file.write(cookie_dict_to_cookie_line(cookie))
    cookie_file.close()
    return cookie_file.name


def fix_crunchyroll_cookie_issues(cookie):
    """Fix the cookie issues encountered by youtube_dl.

    :param cookie: single cookie received from chromedriver
    :type cookie: dictionary
    """
    fix_issues(cookie)
    delete_bad_cookies(cookie)


def fix_issues(cookie):
    """Fix issues caused by specific cookies by changing their values.

    :param cookie: single cookie received from chromedriver
    :type cookie: dictionary
    """
    cookie_issues_list = [
        '__qca', '_ga', '_gat', '_gid'
    ]
    for issue in cookie_issues_list:
        if issue == cookie['name']:
            cookie['httpOnly'] = True


def delete_bad_cookies(cookie):
    """Effectively delete bad cookies.

    Deletion of bad cookies is done by replacing their domain to a '#' so that when it's written
    to the cookie_file it's considered a comment.
    :param cookie: single cookie received from chromedriver
    :type cookie: dictionary
    """
    bad_cookies_list = [
        'ajs_user_id', 'ajs_group_id', 'ajs_anonymous_id'
    ]
    for bad_cookie in bad_cookies_list:
        if cookie['name'] == bad_cookie:
            cookie['domain'] = '#'


def cookie_dict_to_cookie_line(cookie):
    """Convert a cookie dictionary to a netscape cookie line.

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
    """Ensure a dict has all the keys by populating it with empty values (Destructive method).

    :param flawed_dict: dictionary possibly containing missing fields.
    :param keys: Tuple of required keys.
    :return: dictionary with all the keys.
    """
    for key in keys:
        if key not in flawed_dict:
            flawed_dict[key] = ''
    return flawed_dict


if __name__ == '__main__':
    # Change directory to download to ~/Downloads
    os.chdir('{home}/Downloads/'.format(home=os.getenv('HOME')))
    USERNAME = input('Username: ')
    PASSWORD = getpass('Password: ')
    URL = input('URL: ')
    YOUTUBE_DL_PARAMS = input('Input extra youtube_dl params as space seperated values: ')
    main(USERNAME, PASSWORD, URL, YOUTUBE_DL_PARAMS)
