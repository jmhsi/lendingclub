"""
This module contains functions that assist in downloading and archiving csvs from
lendingclub (loan info and payment history). Selenium is used to download the files.
Other helper functions take care of comparing to any previously downloaded csvs
and archiving when necessary.

TODOS:
selenium can sometimes go too fast and miss some of the download options
I currently get around this by explicitly pausing for 2 seconds near the
problem areas, but should probably create a function to check downloading csvs
with all options in dropdown list.
"""
# %load ../../lendingclub/csv_dl_archiving/download_prep.py
# driver download https://github.com/mozilla/geckodriver/releases
# extracted geckodriver to /usr/local/bin in ubuntu
import os
# import stat
from stat import S_ISDIR, ST_CTIME, ST_MODE
import subprocess
import sys
import time
from datetime import datetime
# from shutil import copytree, rmtree

import pause
from selenium.webdriver import Chrome
from selenium.webdriver.chrome import webdriver as chrome_webdriver
from selenium.webdriver.support.ui import Select
import user_creds.account_info as acc_info
from lendingclub import config


# import to grab user_creds
sys.path.append(config.prj_dir)



class DriverBuilder():
    '''
    helps build chrome driver
    https://stackoverflow.com/questions/45631715/downloading-with-chrome-headless-and-selenium
    '''
    def get_driver(self, download_location=None, headless=False):
        '''
        helps get driver
        '''
        driver = self._get_chrome_driver(download_location, headless)
        driver.set_window_size(1400, 700)
        return driver

    def _get_chrome_driver(self, download_location, headless):
        '''
        Makes the driver with right options
        '''
        chrome_options = chrome_webdriver.Options()
        if download_location:
            prefs = {
                'download.default_directory': download_location,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': False,
                'safebrowsing.disable_download_protection': True
            }
            chrome_options.add_experimental_option('prefs', prefs)
            chrome_options.add_argument("--no-sandbox")

        if headless:
            chrome_options.add_argument("--headless")

        driver_path = '/usr/bin/chromedriver'

        if sys.platform.startswith("win"):
            driver_path += ".exe"

        driver = Chrome(executable_path=driver_path,
                        chrome_options=chrome_options)
        if headless:
            self.enable_download_in_headless_chrome(driver, download_location)
        return driver

    def enable_download_in_headless_chrome(self, driver, download_dir):
        """
        there is currently a "feature" in chrome where
        headless does not allow file download:
        https://bugs.chromium.org/p/chromium/issues/detail?id=696481
        This method is a hacky work-around until the official chromedriver support for this.
        Requires chrome version 62.0.3196.0 or above.
        """

        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = (
            "POST", '/session/$sessionId/chromium/send_command')

        params = {
            'cmd': 'Page.setDownloadBehavior',
            'params': {
                'behavior': 'allow',
                'downloadPath': download_dir
            }
        }
        command_result = driver.execute("send_command", params)
        print("response from browser:")
        for key in command_result:
            print("result:" + key + ":" + str(command_result[key]))


def download_csvs(download_path, pause_len=2500):
    '''
    downloads all loan_info csvs and pmt_history csv
    '''
    print('downloading csvs to {0}'.format(os.path.abspath(download_path)))

    try:
        # setup constants
        email = acc_info.email_throwaway
        password = acc_info.password_throwaway
        url_dl = "https://www.lendingclub.com/info/download-data.action"
        url_signin = "https://www.lendingclub.com/auth/login"
        url_pmt_hist = "https://www.lendingclub.com/site/additional-statistics"

        d_builder = DriverBuilder()
        driver = d_builder.get_driver(download_location=download_path,
                                      headless=True)

        # sign in
        driver.get(url_signin)
        pause.milliseconds(pause_len)
        email_box = driver.find_element_by_name('email')
        password_box = driver.find_element_by_name('password')
        # password_box = driver.find_element_by_xpath(
        #     '/html/body/div[2]/div[1]/div[2]/form[1]/label[2]/input')

        pause.milliseconds(pause_len)
        email_box.send_keys(email)
        password_box.send_keys(password)

        # button = driver.find_element_by_xpath(
        #     '/html/body/div[2]/div[1]/div[2]/form[1]/button')
        button = driver.find_element_by_class_name('form-button--submit')
        button.click()
        pause.milliseconds(pause_len)

        # download loan_info
        driver.get(url_dl)
        # download_btn = driver.find_element_by_xpath(
        #     '//*[@id="currentLoanStatsFileName"]')
        download_btn = driver.find_element_by_id(
            'currentLoanStatsFileNameHandler')

        select = driver.find_element_by_xpath(
            '//*[@id="loanStatsDropdown"]')  # get the select element
        options = select.find_elements_by_tag_name(
            "option")  # get all the options into a list

        options_dict = {}
        for option in options:  # iterate over the options, place attribute value in list
            options_dict[option.get_attribute("value")] = option.text

        for opt_val, text in options_dict.items():
            print("starting download on option {0}, {1}".format(opt_val, text))

            select = driver.find_element_by_xpath(
                '//*[@id="loanStatsDropdown"]')
            # print('found the select dropdown')
            selection = Select(select)
            selection.select_by_value(opt_val)
            # print('set selection to option value {0}: {1}'.format(opt_val, text))
            download_btn.click()
            pause.milliseconds(pause_len)
            # print('got to click download btn')
            # now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            # driver.get_screenshot_as_file('screenshot-%s.png'%now)
            # setup to workaround the center-block button:
            try:
                blocking_btn = driver.find_element_by_class_name(
                    'center-block')
                blocking_btn.click()
                close_btn = driver.find_element_by_class_name('close')
                close_btn.click()
                # print('got through blocking data disclaimer')
            except:
                # print('did not get through blocking data disclaimer')
                pass
            pause.milliseconds(pause_len)

        # payment history downloads
        pause.milliseconds(pause_len)
        driver.get(url_pmt_hist)

        pause.milliseconds(pause_len)
        pmt_history = driver.find_element_by_partial_link_text('All payments')
        pmt_history.click()

        # wait for all downloads to finish
        while True:
            if len(os.listdir(download_path)) != (
                    len(options_dict) + 1):  # +1 for one pmt history file
                time.sleep(5)
                print('waiting for all csv downloads to start')
                continue
            else:
                files = os.listdir(download_path)
                k = 0
                time.sleep(5)
                print('checking/waiting for all csv downloads to finish')
                for filename in files:
                    if 'crdownload' in filename:
                        print('{0} is still downloading'.format(filename))
                        time.sleep(30)
                    else:
                        k += 1
                        #                 print(k)
                if k == len(files):
                    time.sleep(2)
                    break

        print('done downloading')
        driver.close()
        return True
    except Exception as e:
        print(e)
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        driver.get_screenshot_as_file('screenshot-%s.png' % now)


def get_hashes(path):
    '''
    gets shasum hashes for files to check for file changes
    '''
    print('computing shasum for files in {0}'.format(os.path.abspath(path)))
    hashes = {}
    files = os.listdir(path)
    for file_ in files:
        sha = subprocess.check_output('shasum -a 256 {0}\
                                      '.format(path + '/'
                                               + file_),
                                      shell=True)
        hashes[file_] = sha.split()[0]
    return hashes


def check_file_changes(compare_dir, just_dled_hashes):
    '''
    Checks for sha differences for downloaded vs archived csvs
    '''
    need_to_clean = False
    print(
        'starting to check for file changes comparing what was just downloaded.'
    )
    print('looking for previous downloads at {0}'.format(compare_dir))
    try:
        previous_dled_hashes = get_hashes(compare_dir[1])

        # compare new download to previous download
        # check for added or deleted files
        dne_files = set(just_dled_hashes.keys()).intersection(
            set(previous_dled_hashes.keys()))
        add_files = set(previous_dled_hashes.keys()).intersection(
            set(just_dled_hashes.keys()))
        if len(just_dled_hashes) != len(previous_dled_hashes):
            need_to_clean = True
            print("Compared to the previous time new csv's were downloaded, \
                      the following files were deleted: \n {0}".format(
                          dne_files))
            print("Compared to the previous time new csv's were downloaded, \
                      the following files are new additions: \n {0}".format(
                          add_files))
        else:
            print(
                'No files were added or deleted since previous downloading of csvs'
            )

        # check for shasum256 changes
        changed_files = []
        for key in just_dled_hashes.keys() & previous_dled_hashes.keys():
            if previous_dled_hashes[key] != just_dled_hashes[key]:
                changed_files.append(key)

        if len(changed_files) == 0:
            print('There are no changes to previous downloaded lending club \
                      csvs (loan_info and pmt_hist) via shasum256 hashes')
        else:
            need_to_clean = True
            print('Compared to the previous data download, the shasum256 \
            hashes changed for the following files: {0}'.format(changed_files))

    except IndexError:
        need_to_clean = True
        print('Could not find previously download directory? This is \
                  probably your first time downloading the csvs or the \
                  first download to a new path.')

    return need_to_clean


def get_newest_creationtime_dir(ppath):
    '''returns path of newest dir by creation time in ppath'''
    print('getting folders sorted by creation time in {0}'.format(
        os.path.abspath(ppath)))
    csv_folders = [
        os.path.join(ppath, fn) for fn in os.listdir(ppath)
        if fn not in ['archived_csvs', 'working_csvs', 'latest_csvs']
    ]
    csv_folders = [(os.stat(path), path) for path in csv_folders]
    csv_folders = [(stat[ST_CTIME], path) for stat, path in csv_folders
                   if S_ISDIR(stat[ST_MODE])]
    return sorted(csv_folders)[-1]


# def archiver(archive_flag, ppath, archiver_dir=None):
#     '''will archive dirs if told to'''
#     archiver_dir = os.path.join(
#         os.path.expanduser('~'), 'projects', 'lendingclub', 'data', 'csvs',
#         'archived_csvs') if not archiver_dir else archiver_dir
#     os.makedirs(archiver_dir, exist_ok=True)
#     if archive_flag:
#         just_dled = get_sorted_creationtime_dirs(ppath)[-1][1]

#         newest_folder = os.path.split(just_dled)[1]

#         copytree(just_dled, os.path.join(archiver_dir, newest_folder))

#         print('copied {0} to {1}'.format(newest_folder,
#                                          os.path.abspath(archiver_dir)))


# def cleaner(ppath):
#     '''
#     cleans the ppath of every dir except archived_csvs
#     '''
#     just_dled = os.path.split(get_sorted_creationtime_dirs(ppath)[-1][1])[1]
#     keep_dirs = ['archived_csvs']  # , 'working_csvs', just_dled]
#     for tree in os.listdir(ppath):
#         if tree not in keep_dirs:
#             rmtree(os.path.join(ppath, tree), onerror=handle_error)
#             print('removing old dirs {0}'.format(tree))
#     return just_dled




# def handle_error(func, path, exc_info):
#     '''
#     Error handler function
#     It will try to change file permission and call the calling function again,
#     From https://thispointer.com/python-how-to-delete-a-directory-recursively-using-shutil-rmtree/
#     '''
#     print('Handling Error for file ', path)
#     print(exc_info)
#     # Check if file access issue
#     if not os.access(path, os.W_OK):
#         print('Hello')
#         # Try to change the permision of file
#         os.chmod(path, stat.S_IWUSR)
#         # call the calling function again
#         func(path)
