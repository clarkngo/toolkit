from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
import time
from helper import *
from constants import *

course_selected = select_course_from_csv(CSV_FILE_PATH)
url_disccusions = URL_DISCUSSION_BEGIN + course_selected + URL_DISCUSSION_END

driver = setup_web_driver()
login_to_d2l(driver, LOGIN_URL, USERNAME, PASSWORD)

driver.get(url_disccusions)

# Initialize WebDriverWait
wait = WebDriverWait(driver, 10)

try:
    # Wait for the link element with 'Concept Test' to be present
    concept_test_link = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Concept Test')]")))

    # Find the 'Edit Topic' option. Adjust the XPath according to the actual HTML structure
    edit_topic_xpath = "./ancestor::h3/following-sibling::div//d2l-menu-item[@text='Edit Topic']"
    edit_topic_option = concept_test_link.find_element(By.XPATH, edit_topic_xpath)

    # Click the 'Edit Topic' option
    edit_topic_option.click()

except TimeoutException:
    print("Topic with text 'Concept Test' was not found within the given time.")
except NoSuchElementException:
    print("Edit Topic option was not found for the 'Concept Test' topic.")


time.sleep(10000)
# Close the WebDriver
driver.quit()
