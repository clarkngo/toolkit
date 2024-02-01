import time
from constants import *
from helper import *

course_selected = select_course_from_csv(CSV_FILE_PATH)
url = URL_MANAGE_DATES + course_selected

driver = setup_web_driver()
login_to_d2l(driver, LOGIN_URL, USERNAME, PASSWORD)

driver.get(url)

time.sleep(10000)
# Close the WebDriver
driver.quit()

