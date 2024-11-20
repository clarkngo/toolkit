
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

# from github import Github

# # Initialize GitHub instance with your personal access token
# g = Github("")

# def test_github_connection(github_instance):
#     try:
#         # Attempt to fetch authenticated user details
#         user = github_instance.get_user()
#         print(f"Successfully connected to GitHub. Authenticated as {user.login}.")
#         return True
#     except Exception as e:
#         print(f"Failed to connect to GitHub: {e}")
#         return False

# def create_classroom_repos(github_instance, org_name, repos):
#     # Fetch the organization
#     org = github_instance.get_organization(org_name)
    
#     for repo_name in repos:
#         try:
#             # Create a new repository within the organization
#             repo = org.create_repo(name=repo_name,
#                                    private=True,  # Set to False if you want the repo to be public
#                                    description=f"Repository for {repo_name}")
#             print(f"Repository created: {repo.html_url}")
#         except Exception as e:
#             print(f"Failed to create repository {repo_name}: {e}")

# if __name__ == "__main__":
#     if test_github_connection(g):
#         org_name = "your_org_or_username_here"
#         classroom_repos = ["classroom1", "classroom2", "classroom3"]
#         create_classroom_repos(g, org_name, classroom_repos)
