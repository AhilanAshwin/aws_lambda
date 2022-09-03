from sqlite3 import converters
from tkinter import Image
import streamlit as st
from ws_blaster.utils import open_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from os import listdir, path
import time
import shutil
import pathlib
import re
from PIL import Image
from sys import platform as my_system


class Manage:
    def __init__(self, user_path, wsb_path):
        self.user_path = pathlib.Path(user_path)
        self.ss_path = pathlib.Path(wsb_path)
        self.driver_dict = {}
        self.account_dict = {}
        self.list_dir = {}
        self.new_account = []
        self.available = []  # if len > 1, there is account
        self.not_available = []
        self.exist_account = self.available + self.not_available
        self.screenshot = []

    def get_name(self, name: str):
        """
        Return name in list data type
        """
        name = name.split(',')
        name = [x.strip() for x in name]
        return name

    def get_all_sim_name(self, platform: str, client: str) -> list[str]:
        """
        Return a list of directory of platform
        """
        path_to_client = self.user_path/platform/client
        sim_list = [f for f in listdir(path_to_client)]
        return sim_list

    def add_client_directory(self, platform, client: str):
        """
        Make directory for client.
        Will create a directory in Users directory
        """
        filepath = self.user_path/platform
        new_dir = os.mkdir(str(filepath / client))
        return new_dir

    def get_all_client_dir(self, platform):
        """
        Return a list of client directory name
        """
        path_to_platform = self.user_path/platform
        client_dir = [f for f in listdir(path_to_platform)]
        return client_dir

    def get_all_platform(self):
        """
        Return a list of platform directory name
        """
        path_to_user = self.user_path
        platform_list = [f for f in listdir(path_to_user)]
        return platform_list

    def convert_posix_for_windows(self, the_path):
        '''
        NOTE: For WINDOWS OS only! 
        If Linux, please hash the function.

        Convert Posix to Windows path
        '''
        sub_path = re.sub('\\\\', '\\\\\\\\', the_path)
        expander = 'D:\\\\Desktop\\\\INVOKE\\\\ws_blaster\\\\ahilan-branch\\\\venvAhilan\\\\ws-blaster-prod\\\\'
        return expander + sub_path

    def convert_posix_for_windows_add_acc(self, the_path):
        '''
        TODO: For WINDOWS OS only!
        If Linux, please hash the function.

        Convert Posix to Windows path for adding new account function.
        '''
        sub_path = re.sub('\\\\', '\\', the_path)
        expander = 'D:\\\\Desktop\\\\INVOKE\\\\ws_blaster\\\\ahilan-branch\\\\venvAhilan\\\\ws-blaster-prod\\\\'
        return expander + sub_path

    def checking_banned_or_not(self, sim_list, platform: str, client: str) -> tuple[list, list]:
        """
        Return list of available and not-available simcard.

        Checking whether the simcard is banned/unlinked.  
        """

        for simcard in sim_list:

            # NOTE: System
            if my_system == 'win32':
                path_to_platform = str(self.user_path/platform/client/simcard)
                path_to_platform = self.convert_posix_for_windows(
                    str(path_to_platform))
            else:
                path_to_platform = self.user_path/platform/client/simcard

            driver = open_driver('user-data-dir=' + str(path_to_platform))
            try:
                f = WebDriverWait(driver, 20).until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@title="Search input textbox"]')))
                self.available.append(simcard)
                print("SIMCARD AVAILABLE")

            except:
                # If not avaialble, will found these phrase
                f = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div/div/div[2]/div[1]/div/div[2]/div/canvas')))
                self.not_available.append(simcard)
                print("SIMCARD NOT AVAILABLE")

            driver.quit()

        return (self.available, self.not_available)

    def take_screenshot(self, driver):
        """
        Take the screenshot of the QR code 

        ### NOTE : QR code will be refreshed after 15 seconds
        """
        driver.save_screenshot('./Screenshot/QR_code_1.png')
        ss = 'screenshot'
        self.screenshot.append(ss)

    def get_screenshot(self):
        ss = Image.open('./Screenshot/QR_code_1.png')
        return st.image(ss)

    def create_new_user_file(self, platform: str, client: str, account_name: str):
        """
        Create new file user account in platform file
        """
        if my_system == 'win32':
            path_to_platform = self.user_path/platform/client/account_name
            path_to_platform = self.convert_posix_for_windows(
                str(path_to_platform))
        else:
            path_to_platform = self.user_path / platform / client / account_name

        driver = open_driver('user-data-dir=' + str(path_to_platform), 
                            headless=True)
        self.driver_dict[path_to_platform] = account_name
        return driver

    def deleted_account(self, platform: str, client: str, simcard: str):
        """
        To delete the directory which deleted the account too.
        """
        path_to_account = self.user_path/platform/client/simcard
        shutil.rmtree(path_to_account)
        self.account_dict[client] = 'deleted'

    def get_taken(self, name: str, platform: str, client: str) -> list[str]:
        """
        Return list of the account name, if the account is existed (added)
        """
        name = self.get_name(name)
        sim_list = self.get_all_sim_name(platform, client)
        taken = [x for x in name if x in sim_list]
        return taken
