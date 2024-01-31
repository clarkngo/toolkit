import csv
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()
username = os.environ.get('USERNAME')
password = os.environ.get('PASSWORD')
login_url = os.environ.get('ADMIN_D2L_LOGIN')
assignments=["HOP", "HOS", "PE", "TP", "DB", "MP", "CD"]
labels = ["Has Start Date", "Has End Date"]
csv_file_path = "manual_courses.csv"
url_assignments = "https://mycourses.cityu.edu/d2l/lms/dropbox/admin/folders_manage.d2l?ou="
url_quick_edit = "https://mycourses.cityu.edu/d2l/lms/dropbox/admin/folders_quickedit.d2l"
course_selected = 0

replacement_dict = {
    "HOP": "HOS",
    "Hands-On Practice": "Hands-On Skill"
}

any_time = "\d{1,2}:\d{2} [APap][Mm]"
target_time = "11:59 PM"

def setup_web_driver():
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)

# Function to extract digits-only values from a string
def extract_digits(text):
    return ''.join(filter(str.isdigit, text))

def replace_text_in_elements(input_elements, replacement_dict):
    for element in input_elements:
        value = element.get_attribute("value")
        if value:
            for old_text, new_text in replacement_dict.items():
                value = value.replace(old_text, new_text)

            # value = re.sub(r'\d{1,2}:\d{2} [APap][Mm]', target_time, value)

            element.clear()
            element.send_keys(value)

def build_title_digit_dict(checkboxes, assignments):
    title_digit_map = {}
    for checkbox in checkboxes:
        title = checkbox.get_attribute('title')
        value = checkbox.get_attribute('value')

        for prefix in assignments:
            if title.startswith(prefix):
                continue

        if '_' in value:
            _, digits = value.split('_')
            title_digit_map[title] = digits
    return title_digit_map


def select_course_from_csv(csv_file_path):

    # Read the CSV file and display its content
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Get the headers (first row) of the CSV
        data = list(csv_reader)  # Read the remaining rows of data

        # Display the entire CSV content with ordered numbers
        print("CSV Content:")
        print("Ordered Numbers:")
        for i, row in enumerate(data):
            print(f"{i + 1}. {', '.join(row)}")

        # Prompt the user to choose a row by ordered number
        try:
            selected_row_index = int(input("Choose a row (by ordered number): ")) - 1
            if 0 <= selected_row_index < len(data):
                selected_row = data[selected_row_index]
                course_selected = selected_row[2]  # Extract the "id" value
                print(f"Selected 'id' value: {course_selected}")
            else:
                print("Invalid row order.")
        except ValueError:
            print("Invalid input. Please enter a valid row order.")

    print(f"Selected variable: {course_selected}")
    return course_selected

def write_output_for_logs(title_digit_map):
    # Write the map to a CSV file
    with open('output.csv', 'w', newline='') as csvfile:
        fieldnames = ['Title', 'Digits']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for title, digits in title_digit_map.items():
            writer.writerow({'Title': title, 'Digits': digits})

def login_to_d2l(driver):
    driver.get(login_url)
    # Wait for the page to load and locate login fields
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'userName')))
    username_input = driver.find_element(By.ID, 'userName')
    password_input = driver.find_element(By.ID, 'password')

    # Send credentials
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Click the login button
    login_button = driver.find_element(By.XPATH, '//button[text()="Log In"]')
    login_button.click()



course_selected = select_course_from_csv(csv_file_path)

driver = setup_web_driver()
login_to_d2l(driver)

driver.get(url_assignments + course_selected)

checkbox = driver.find_element(By.CLASS_NAME, 'd2l-checkbox')
checkbox.click()
checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input.d2l-checkbox[type="checkbox"]')
# Prepare a map of titles to formatted digits
title_digit_map = build_title_digit_dict(checkboxes, assignments)

write_output_for_logs(title_digit_map)

# Base URL for the Quick Edit page

# Start with the base URL and the 'ou' parameter (replace '13352' with the actual 'ou' value for your use case)
full_url_bulk_edit = f"{url_quick_edit}?ou=" + course_selected

# Add each 'dbl' parameter with the extracted digits to the URL
for digits in title_digit_map.values():
    full_url_bulk_edit += f"&dbl={digits}"

driver.get(full_url_bulk_edit)


# Step 3: Find all matching input elements
input_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
replace_text_in_elements(input_elements, replacement_dict)


# Keep the browser open for inspection (adjust time as needed)
time.sleep(10000)

# Close the WebDriver
driver.quit()
