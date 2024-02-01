
from dotenv import load_dotenv
import os

ASSIGNMENTS=["HOP", "HOS", "PE", "TP", "DB", "MP", "CD"]
LABELS = ["Has Start Date", "Has End Date"]
URL_ASSIGNMENTS = "https://mycourses.cityu.edu/d2l/lms/dropbox/admin/folders_manage.d2l?ou="
URL_QUICK_EDIT = "https://mycourses.cityu.edu/d2l/lms/dropbox/admin/folders_quickedit.d2l"
URL_DISCUSSION_BEGIN = "https://mycourses.cityu.edu/d2l/le/"
URL_DISCUSSION_END = "/discussions/List?dst=1"
URL_MANAGE_DATES= "https://mycourses.cityu.edu/d2l/lms/manageDates/date_manager.d2l?fromCMC=1&ou="

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
LOGIN_URL = os.environ.get('ADMIN_D2L_LOGIN')
CSV_FILE_PATH = os.environ.get('CSV_COURSE_PATH')
