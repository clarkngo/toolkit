from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium import webdriver  # Import directly

import time
from helper import *  # Assuming helper.py contains setup_web_driver()
from constants import *  # Assuming constants.py defines LOGIN_URL, USERNAME, PASSWORD

# Setup WebDriver (assuming setup_web_driver() returns a WebDriver instance)
driver = setup_web_driver()

login_url = LOGIN_URL  # Assuming LOGIN_URL is defined in constants.py
username = USERNAME  # Assuming USERNAME is defined in constants.py
password = PASSWORD  # Assuming PASSWORD is defined in constants.py

# Login to D2L
login_to_d2l(driver, login_url, username, password)  # Assuming login_to_d2l handles login logic

# (Optional) Add a short wait to ensure the page loads after login
time.sleep(10000)  # Adjust wait time as needed

# You can now interact with the logged-in page here

# Close the WebDriver
driver.quit()
