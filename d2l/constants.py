
from dotenv import load_dotenv
import os

ASSIGNMENTS=["HOP", "HOS", "PE", "TP", "DB", "MP", "CD"]
LABELS=["Has Start Date", "Has End Date"]
URL_ASSIGNMENTS="https://mycourses.cityu.edu/d2l/lms/dropbox/admin/folders_manage.d2l?ou="
URL_QUICK_EDIT="https://mycourses.cityu.edu/d2l/lms/dropbox/admin/folders_quickedit.d2l"
URL_DISCUSSION_BEGIN="https://mycourses.cityu.edu/d2l/le/"
URL_DISCUSSION_END="/discussions/List?dst=1"
URL_MANAGE_DATES="https://mycourses.cityu.edu/d2l/lms/manageDates/date_manager.d2l?fromCMC=1&ou="
URL_CONTENT="https://mycourses.cityu.edu/d2l/le/lessons/"

COURSES_GH_CL=["IS312","DS484","AI500","CS519","CY640","DIT62"]
COURSE_SELECTED = 0

REPLACEMENT_DICT = {
    "HOP": "HOS",
    "Hands-On Practice": "Hands-On Skill"
}

ANY_TIME = "\d{1,2}:\d{2} [APap][Mm]"
TARGET_TIME = "11:59 PM"

# Load environment variables
load_dotenv()
USERNAME = os.environ.get('USERNAME')
PASSWORD = os.environ.get('PASSWORD')
GH_USERNAME = os.environ.get('GH_USERNAME')
GH_PASSWORD = os.environ.get('GH_PASSWORD')
LOGIN_URL = os.environ.get('ADMIN_D2L_LOGIN')
CSV_FILE_PATH = os.environ.get('CSV_COURSE_PATH')
