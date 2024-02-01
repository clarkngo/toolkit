from datetime import datetime, timedelta
import holidays
import os

def generate_date_ranges(start_date, weeks):
    # Create a directory to store the text files if it doesn't exist
    if not os.path.exists("txt_files"):
        os.makedirs("txt_files")
        
    date_format = "%m/%d"
    start_date = datetime.strptime(start_date, date_format)
    current_year = str(datetime.now().year)

    # Initialize US holidays
    us_holidays = holidays.UnitedStates(years=start_date.year)

    for week in range(weeks):
        end_date = start_date + timedelta(days=6)
        avail_date = start_date - timedelta(days=3)
        week_dates = [start_date + timedelta(days=i) for i in range(7)]

        # Check if any day within the week is a US holiday
        week_holidays = [us_holidays[date] for date in week_dates if date in us_holidays]

        date_range = f"{start_date.strftime(date_format)} - {end_date.strftime(date_format)}"

        # Create a .txt file for each week
        with open(f"txt_files/s{week + 1}.txt", "w") as start_file:
            start_file.write(str(avail_date.strftime(date_format)) +"/" + current_year)

        with open(f"txt_files/e{week + 1}.txt", "w") as end_file:
            end_file.write(str(end_date.strftime(date_format)) +"/" + current_year)

        start_date = end_date + timedelta(days=1)

# User input
start_date_input = input("Enter the starting date (MM/DD): ")
weeks_to_generate = 10  #

# Generate and save the .txt files
generate_date_ranges(start_date_input, weeks_to_generate)
