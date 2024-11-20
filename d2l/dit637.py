from selenium.webdriver.common.by import By
import time
from helper import *
from constants import *

course_selected = select_course_from_csv(CSV_FILE_PATH)

driver = setup_web_driver()
login_to_d2l(driver, LOGIN_URL, USERNAME, PASSWORD)

driver.get(URL_ASSIGNMENTS + course_selected)

checkbox = driver.find_element(By.CLASS_NAME, 'd2l-checkbox')
checkbox.click()
checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input.d2l-checkbox[type="checkbox"]')
# Prepare a map of titles to formatted digits
title_digit_map = build_title_digit_dict(checkboxes, ASSIGNMENTS)



# Step 3: Find all matching input elements
input_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
replace_text_in_elements(input_elements, REPLACEMENT_DICT)


# Keep the browser open for inspection (adjust time as needed)
time.sleep(10000)

# Close the WebDriver
driver.quit()
