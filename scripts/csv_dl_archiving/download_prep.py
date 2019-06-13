# driver download https://github.com/mozilla/geckodriver/releases
# extracted geckodriver to /usr/local/bin in ubuntu
import os
import sys
import subprocess
import time
from stat import S_ISDIR, ST_CTIME, ST_MODE
from shutil import copytree, rmtree
import pause
from selenium.webdriver import Chrome
from selenium.webdriver.chrome import webdriver as chrome_webdriver
from selenium.webdriver.support.ui import Select

# # relative import to grab user_creds
# sys.path.append('../../user_creds/')
import lendingclub.user_creds.account_info as acc_info

class DriverBuilder():
    # https://stackoverflow.com/questions/45631715/downloading-with-chrome-headless-and-selenium
    def get_driver(self, download_location=None, headless=False):
        driver = self._get_chrome_driver(download_location, headless)
        driver.set_window_size(1400, 700)
        return driver

    def _get_chrome_driver(self, download_location, headless):
        chrome_options = chrome_webdriver.Options()
        if download_location:
            prefs = {'download.default_directory': download_location,
                     'download.prompt_for_download': False,
                     'download.directory_upgrade': True,
                     'safebrowsing.enabled': False,
                     'safebrowsing.disable_download_protection': True}
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
        headless does not allow file download: https://bugs.chromium.org/p/chromium/issues/detail?id=696481
        This method is a hacky work-around until the official chromedriver support for this.
        Requires chrome version 62.0.3196.0 or above.
        """

        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = (
            "POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {
            'behavior': 'allow', 'downloadPath': download_dir}}
        command_result = driver.execute("send_command", params)
        print("response from browser:")
        for key in command_result:
            print("result:" + key + ":" + str(command_result[key]))

def download_csvs(download_path):
    '''
    downloads all loan_info csvs and pmt_history csv
    '''
    print('downloading csvs to {0}'.format(os.path.abspath(download_path)))
    
    # setup constants
    email = acc_info.email_throwaway
    password = acc_info.password_throwaway
    url_dl = "https://www.lendingclub.com/info/download-data.action"
    url_signin = "https://www.lendingclub.com/auth/login"
    url_pmt_hist = "https://www.lendingclub.com/site/additional-statistics"

    d_builder = DriverBuilder()
    driver = d_builder.get_driver(
        download_location=download_path, headless=True)
    
    # sign in
    driver.get(url_signin)
    email_box = driver.find_element_by_xpath(
        '/html/body/div[2]/div[1]/div[2]/form[1]/label[1]/input')
    password_box = driver.find_element_by_xpath(
        '/html/body/div[2]/div[1]/div[2]/form[1]/label[2]/input')

    pause.milliseconds(1000)
    email_box.send_keys(email)
    password_box.send_keys(password)

    button = driver.find_element_by_xpath(
        '/html/body/div[2]/div[1]/div[2]/form[1]/button')
    button.click()
    pause.milliseconds(3000)

    # download loan_info
    driver.get(url_dl)
    download_btn = driver.find_element_by_xpath(
        '//*[@id="currentLoanStatsFileName"]')

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
        selection = Select(select)
        selection.select_by_value(opt_val)
        download_btn.click()
        pause.milliseconds(2000)

    # payment history downloads
    driver.get(url_pmt_hist)

    pmt_history = driver.find_element_by_xpath(
        '/html/body/div[2]/section/div[2]/div/p[2]/a[2]')
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

def get_hashes(path):
    '''
    gets shasum hashes for files to check for file changes
    '''
    print('computing shasum for files in {0}'.format(os.path.abspath(path)))
    hashes = {}
    files = os.listdir(path)
    for file_ in files:
        a = subprocess.check_output(
            'shasum -a 256 {0}'.format(path + '/' + file_), shell=True)
        hashes[file_] = a.split()[0]
    return hashes

def check_file_changes(csv_folders, just_dled_hashes):
    need_to_clean = False
    print('starting to check for file changes comparing what was just downloaded.')
    try:
        previous_dled_hashes = get_hashes(csv_folders[-2][1])

        # compare new download to previous download
        # check for added or deleted files
        dne_files = set(just_dled_hashes.keys()).intersection(
            set(previous_dled_hashes.keys()))
        add_files = set(previous_dled_hashes.keys()).intersection(
            set(just_dled_hashes.keys()))
        if len(just_dled_hashes) != len(previous_dled_hashes):
            need_to_clean = True
            print("Compared to the previous time new csv's were downloaded, the following files were deleted: \n {0}".format(
                dne_files))
            print("Compared to the previous time new csv's were downloaded, the following files are new additions: \n {0}".format(
                add_files))
        else:
            print('No files were added or deleted since previous downloading of csvs')

        # check for shasum256 changes
        changed_files = []
        for key in just_dled_hashes.keys() & previous_dled_hashes.keys():
            if previous_dled_hashes[key] != just_dled_hashes[key]:
                    changed_files.append(key)
                
        if len(changed_files) == 0:
            print('There are no changes to previous downloaded lending club csvs (loan_info and pmt_hist) via shasum256 hashes')
        else:
            need_to_clean = True
            print('Compared to the previous data download, the shasum256 hashes changed for the following files: {0}'.format(
                changed_files))

    except IndexError:
        need_to_clean = True
        print('Could not find previously download directory? This is probably your first time downloading the csvs or the first download to a new path.')

    return need_to_clean

def get_sorted_creationtime_dirs(ppath):
    print('getting folders sorted by creation time in {0}'.format(os.path.abspath(ppath)))
    csv_folders = [os.path.join(ppath, fn) for fn in os.listdir(
        ppath) if fn not in ['archived_csvs', 'working_csvs', 'latest_csvs']]
    csv_folders = [(os.stat(path), path) for path in csv_folders]
    csv_folders = [(stat[ST_CTIME], path)
                   for stat, path in csv_folders if S_ISDIR(stat[ST_MODE])]
    return sorted(csv_folders)

def archiver(archive_flag, ppath, archiver_dir=None):
    archiver_dir = os.path.join(os.path.expanduser(
        '~'), 'projects', 'lendingclub', 'data', 'csvs', 'archived_csvs') if not archiver_dir else archiver_dir
    os.makedirs(archiver_dir, exist_ok=True)
    if archive_flag:
        just_dled = get_sorted_creationtime_dirs(ppath)[-1][1]
        
        newest_folder = os.path.split(just_dled)[1]
        
        copytree(just_dled, os.path.join(archiver_dir, newest_folder))
        
        print('copied {0} to {1}'.format(newest_folder, os.path.abspath(archiver_dir)))

def cleaner(ppath):
    just_dled = os.path.split(get_sorted_creationtime_dirs(ppath)[-1][1])[1]
    keep_dirs = ['archived_csvs', 'working_csvs', just_dled]
    for tree in os.listdir(ppath):
        if tree not in keep_dirs:
            rmtree(os.path.join(ppath, tree))
            print('removing old dirs {0}'.format(tree))
    return just_dled
