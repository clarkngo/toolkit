
import time
from constants import *
from helper import *

# course_selected = select_course_from_csv(CSV_FILE_PATH)
# url = URL_MANAGE_DATES + course_selected

driver = setup_web_driver()
# login_to_d2l(driver, LOGIN_URL, USERNAME, PASSWORD)

username = GH_USERNAME
password = GH_PASSWORD

driver.get("https://classroom.github.com/login")

# Wait for the page to load and locate login fields
username_input = driver.find_element(By.ID, 'login_field')
password_input = driver.find_element(By.ID, 'password')

# Send credentials
username_input.send_keys(username)
password_input.send_keys(password)

# Click the login 
login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @name='commit' and @value='Sign in']")

# login_button = driver.find_element(By.XPATH, '//button[text()="Sign In"]')
login_button.click()

time.sleep(10000)
# Close the WebDriver
driver.quit()
