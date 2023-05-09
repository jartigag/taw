#!/usr/bin/env python3
#
# ┌== Recommended installation ==========================================================================┐
#
#  Dependencies 'matplotlib', 'pyyaml' and 'tabulate' will be installed in a Python virtual environment:
#
# $ pipenv install
#
# └======================================================================================================┘
#
# ┌== Usage =========================================┐
#
# Print hours per project worked in the current week:
#
# $ pipenv run ./TAW.py
#
# Print hours per project worked in the last 3 weeks:
#
# $ pipenv run ./TAW.py -2,-1,0
#
# └==================================================┘
#
# More info: https://github.com/jartigag/taw

author  = "@jartigag"
version = '1.1wip'
date    = '2023-05-10'

TAW_DIRS = ["taw/", "taw/_aparcados/"]

TOTAL_WORKING_HOURS_EACH_WEEK = {
    **{i: 41 for i in range(1, 25)},  # rest of the year
    25: 36.5,                         # from June 20th to June 26th
    **{i: 35 for i in range(26, 37)}, # from June 27th to September 11th
    **{i: 41 for i in range(37, 53)}, # rest of the year
}

from datetime import datetime, timedelta
from math import ceil
from pathlib import Path
import re
import sys
from tabulate import tabulate
import yaml

def quote_hours_in_yaml_header(filename):
    """Because in YAML v1.1, HH:MM formatted data is misinterpreted (https://en.wikipedia.org/wiki/Sexagesimal#YAML)"""
    try:
        # extracted from https://stackoverflow.com/q/57168926:
        filedescriptor = open(filename)
        pointer        = filedescriptor.tell()
        if filedescriptor.readline() != '---\n':
          filedescriptor.seek(pointer)
          return ''
        readline               = iter(filedescriptor.readline, '')
        readline               = iter(readline.__next__, '---\n')
        header_lines           = ''.join(readline)
        lines_with_hhmm_quoted = re.sub(r'(\d{2}):(\d{2})', r'"\1:\2"', header_lines)
        return lines_with_hhmm_quoted
    except Exception as e:
        print(filename,e)

def convert_hhmm_to_decimal_hour(hhmm_string):
    splitted_hhmm_string = hhmm_string.split(':')
    hours, minutes       = int(splitted_hhmm_string[0]), int(splitted_hhmm_string[1])
    return hours + minutes/60

def working_days_of_a_specific_week(week_number=0):
    today     = datetime.today().date()
    days_list = [today + timedelta(days=i) for i in range(0-today.weekday()+7*week_number, 5-today.weekday()+7*week_number)]
    return days_list

def ascii_bar(value, max_value, max_bar_length):
    # extracted from https://alexwlchan.net/2018/ascii-bar-charts/:
    increment             = max_value / max_bar_length
    # The ASCII block elements come in chunks of 8, so we work out how many fractions of 8 we need:
    # (https://en.wikipedia.org/wiki/Block_Elements)
    bar_chunks, remainder = divmod(int(value * 8 / increment), 8)
    bar                   = ['█'] * bar_chunks
    # Then add the fractional part. The Unicode code points for block elements are (8/8), (7/8), (6/8), ...,
    # so we need to work backwards.
    if remainder > 0:
        bar.append( chr(ord('█') + (8 - remainder)) )
    # Add spaces until end of bar length:
    bar += [" "]*(max_bar_length-len(bar))
    # Add 5 marks (one for each day):
    for beginning_day_position in range(0,len(bar),ceil(max_bar_length/5)):
        bar[beginning_day_position] = "."
    return bar

if __name__ == "__main__":

    # Create the nested dictionary to store the worked hours:
    hours_per_project = {}
    for dir in TAW_DIRS:
        if Path(dir).is_dir():
            for subdir in Path(dir).iterdir():
                project = subdir.name
                if subdir.is_dir() and re.match(r"^\w+\s\(.*-.*\)$", project):
                #example: "OPOR1 (OP23-006)", "INTE (TAW-001)", "PROYX (PR21-042)", "PROYZ (PR21-040)"
                    hours_per_project[project] = {}
        else:
            print(f'[!] Folder "{dir}" not found')
            sys.exit(-1)
    hours_per_project = {k: hours_per_project[k] for k in sorted(hours_per_project.keys(), key=lambda x: x.split()[1].strip('()')) }
    #example: Sort by keys OP23-006, PR21-040, PR21-042, TAW-001

    # Get the command line arguments:
    args = sys.argv[1:]
    plot = False
    if not args:
        weeks = [0]
    else:
        try:
            weeks = [int(x) for x in args[0].split(',')]
            if len(args)>2:
                plot = True
                import matplotlib.pyplot as plt
        except ValueError:
            print("The provided week numbers must be integers separated by commas")
            exit()

    # Set the dates on which worked hours will be added:
    contemplated_dates = []
    for week in weeks:
        contemplated_dates += working_days_of_a_specific_week(week_number=week)

    for week in weeks:
        # Set the dates for which to sum the worked hours:
        contemplated_dates = working_days_of_a_specific_week(week_number=week)

        # Iterate through the files of each project and add both the worked hours and the annotations to the dictionary:
        for project in hours_per_project:
            for date in contemplated_dates:
                hours_per_project[project][date] = {'hours': 0, 'notes': set()}
            for dir in TAW_DIRS:
                if Path(dir+project).is_dir():
                    for filename in Path(dir+project).iterdir():
                        if filename.is_file() and filename.suffix==".md":
                            try:
                                date_in_filename = datetime.strptime(filename.name.split()[0], "%Y-%m-%d").date()
                            except ValueError:
                                continue
                            if date_in_filename in contemplated_dates:
                                data = yaml.safe_load(quote_hours_in_yaml_header(filename))
                                date = data['date']
                                if date in contemplated_dates:
                                    duration = convert_hhmm_to_decimal_hour(data['endTime']) - convert_hhmm_to_decimal_hour(data['startTime'])
                                    hours_per_project[project][date]['hours'] += duration
                                    hours_per_project[project][date]['notes'].add(data['title'])

        # Convert the dictionary into a list of rows for the table:
        table_rows = []
        if len(hours_per_project)>0:
            max_num_chars_project_name = len( max(hours_per_project.keys(), key=len) )
            for project in hours_per_project:
                hours_row = [f"┌-{project}{' '*( max_num_chars_project_name-len(project) )}-┐"]
                notes_row = [""]
                for date in contemplated_dates:
                    if hours_per_project[project][date]['hours']>0:
                        hours_row.append(hours_per_project[project][date]['hours'])
                        unified_notes = ". ".join(hours_per_project[project][date]['notes'])
                        if len(unified_notes)>30:
                            notes_row.append("\n".join(hours_per_project[project][date]['notes']))
                        else:
                            notes_row.append(unified_notes)
                    else:
                        hours_row.append("-")
                        notes_row.append("")
                if any(h!='-' for h in hours_row[1:]): # excluding the first element of the row, which is the project name
                    table_rows.append(hours_row)
                    TOTAL_WORKING_HOURS_EACH_WEEK = 41
                    total_hours_row               = sum(filter(lambda x: x != '-', hours_row[1:]))
                    total_hours_row_str           = "{:04.1f}".format(total_hours_row)
                    percent_str                   = "{:04.1f}".format(total_hours_row/TOTAL_WORKING_HOURS_EACH_WEEK*100)
                    notes_row[0]                  = f"||{''.join(ascii_bar(total_hours_row, TOTAL_WORKING_HOURS_EACH_WEEK, max_num_chars_project_name))}||"
                    table_rows.append(notes_row)                                                                    # 15 chars =        len(______________)
                    table_rows.append([f"└-{total_hours_row_str} h ({percent_str} %){' '*( max_num_chars_project_name-15 )}-┘"]) #example: "09.5 h (22.4 %)"

            # Print the table:
            print("\n", tabulate(table_rows, headers=['Project'] + [str(date) for date in contemplated_dates], numalign='right'))

    # Visualize the weeks graphically:
    # TODO: Represent the percentage of hours for each project compared to the total working hours per week using bars,
    #       indexing each sum on the first day of each week
    # TODO: Stack the bars in the graph so that each week adds up to 100%
    if plot:
        projects         = list(hours_per_project.keys())
        project_data     = [[hours_per_project[project][date]['hours'] for date in contemplated_dates] for project in projects]
        plt.figure(figsize=(20, 12))
        plt.bar(contemplated_dates, project_data[0], label=projects[0])
        for i in range(1, len(projects)):
            plt.bar(contemplated_dates, project_data[i], bottom=sum(project_data[i]), label=projects[i])
        plt.legend()
        plt.xlabel("Date")
        plt.ylabel("Hours")
        first_week_num, first_week_year = contemplated_dates[0].isocalendar()[1],  contemplated_dates[0].isocalendar()[0]
        last_week_num,  last_week_year  = contemplated_dates[-1].isocalendar()[1], contemplated_dates[-1].isocalendar()[0]
        plt.title(f"Worked Hours per project between week {first_week_num} of {first_week_year} and week {last_week_num} of {last_week_year}")
        plt.show()
        filename = f"TAW - worked hours per project from {contemplated_dates[0]} to {contemplated_dates[-1]}.png"
        plt.savefig(filename)
        print(f'Graph saved in the file: "{filename}"')
