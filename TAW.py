#!/usr/bin/env python3
#
# ┌== Recommended installation =============================┐
#
#  Dependencies 'matplotlib', 'pyyaml' and 'tabulate',
#  specified on Pipfile,
#  will be installed in a Python virtual environment:
#
#  $ python -m pip install pipenv
#  $ pipenv install
#
# └=========================================================┘
#
# ┌== Usage ================================================┐
#
#  Print hours per project worked in the current week:
#
#  $ pipenv run ./TAW.py
#
#  Print hours per project worked in the last 3 weeks:
#
#  $ pipenv run ./TAW.py -2,-1,0
#
#  Print hours per project worked this year:
#
#  $ pipenv run ./TAW.py $(seq -s, 1 $(date +%U))
#
# └=========================================================┘
#
# More info: https://github.com/jartigag/taw

author  = "@jartigag"
version = '1.1'
date    = '2023-05-12'

TAW_DIRS                      = ["taw/", "taw/_aparcados"]
COLORS_CONFIG_FILE            = ".obsidian/plugins/obsidian-full-calendar/data.json"
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
    if week_number<=0:
    # so week_number is relative to today:
        today               = datetime.today().date()
        ref_day             = today
    else:
    # so week_number is relative to the actual year:
        first_day_this_year = datetime.today().date().replace(month=1, day=1)
        ref_day             = first_day_this_year
    days_list = [ref_day + timedelta(days=i) for i in range(0-ref_day.weekday()+7*week_number, 5-ref_day.weekday()+7*week_number)]
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

def init_nested_dict(dirs):
    hours_per_project = {}
    for dir in dirs:
        if Path(dir+"/").is_dir():
            for subdir in Path(dir).iterdir():
                project = subdir.name
                if subdir.is_dir():
                    hours_per_project[project] = {}
        else:
            print(f'[!] Folder "{dir}" not found')
            sys.exit(-1)
    # Sort dict by code if project code between parenthesis, else sort by project name:
    hours_per_project = {k: hours_per_project[k] for k in sorted(
                            hours_per_project.keys(),
                            key=lambda x: x[x.find("(")+1:x.find(")")] if x.find('(')!=x.find(')')!=-1 else x
                        )}
    return hours_per_project

def load_colors_config(config_file):
    colors = {}
    if Path(config_file).is_file():
        colors_config = json.load(open(config_file))
    else:
        colors_config = {'calendarSources': ''}
    def replace_all(text, dic):
        for i, j in dic.items():
            text = text.replace(i, j)
        return text
    strings_to_remove = list(set([x for sublist in TAW_DIRS for x in sublist.split('/')])) + ["/"]
    for calendarSources in colors_config['calendarSources']:
        colors[replace_all(calendarSources['directory'], {k:"" for k in strings_to_remove})] = calendarSources['color']
    return colors

def sort_projects(projects, config_file):
    # Place 'VACACIONES' project at the end of the list and sort it:
    #TODO: configurable order
    projects = list(hours_per_project.keys())
    projects.remove('VACACIONES (23-0004)')
    projects = sorted(projects,
                key=lambda x: x[x.find("(")+1:x.find(")")] if x.find('(')!=x.find(')')!=-1 else x,
                reverse=True) + [('VACACIONES (23-0004)')]
    return projects


if __name__ == "__main__":

    # Create nested dictionary to store worked hours:
    hours_per_project = init_nested_dict(TAW_DIRS)

    # Get command line arguments:
    args = sys.argv[1:]
    if not args:
        weeks = [0]
    else:
        try:
            weeks = sorted([int(x) for x in args[0].split(',')])
        except ValueError:
            print("[!] Provided week numbers must be integers separated by commas")
            sys.exit(-1)

    #TODO: simplify (2 `for week in weeks`? `contemplated_dates` and `contemplated_weeks?`)
    # Set the dates on which worked hours will be added:
    contemplated_dates = []
    contemplated_weeks = {}
    for week in weeks:
        contemplated_dates      +=  working_days_of_a_specific_week(week_number=week)
        contemplated_weeks[week] = [working_days_of_a_specific_week(week_number=week)]

    for week in weeks:

        n_week = contemplated_weeks[week][0][0].isocalendar()[1]

        # Iterate through the files of each project and add both the worked hours and the annotations to the dictionary:
        for project in hours_per_project:
            for date in contemplated_dates:
                hours_per_project[project][date] = {'hours': 0, 'notes': set()}
            for dir in TAW_DIRS:
                if Path(dir+"/"+project).is_dir():
                    for filename in Path(dir+"/"+project).iterdir():
                        if filename.is_file() and filename.suffix==".md":
                            try:
                                # date_in_file_name = datetime.strptime(filename.name.split()[0], "%Y-%m-%d").date()
                                data = yaml.safe_load(quote_hours_in_yaml_header(filename))
                                date = data['date']
                                if date in contemplated_dates:
                                    duration = convert_hhmm_to_decimal_hour(data['endTime']) - convert_hhmm_to_decimal_hour(data['startTime'])
                                    hours_per_project[project][date]['hours'] += duration
                                    hours_per_project[project][date]['notes'].add(data['title'])
                            except ValueError:
                                continue

        # Convert the dictionary into a table rows list:
        table_rows = []
        if len(hours_per_project)>0:
            max_num_chars_project_name = len(max(hours_per_project.keys(), key=len))
            num_chars_hours            = len("00.0 h (00.0 %)")
            for project in hours_per_project:
                hours_row = [f"┌-{project}{' '*(max(max_num_chars_project_name, num_chars_hours)-len(project))}-┐"]
                notes_row = [""]
                for days in contemplated_weeks[week]:
                    for day in days:
                        if hours_per_project[project][day]['hours']>0:
                            hours_row.append(hours_per_project[project][day]['hours'])
                            unified_notes = ". ".join(hours_per_project[project][day]['notes'])
                            if len(unified_notes) > 30:
                                notes_row.append("\n".join(hours_per_project[project][day]['notes']))
                            else:
                                notes_row.append(unified_notes)
                        else:
                            hours_row.append("-")
                            notes_row.append("")
                if any(h!='-' for h in hours_row[1:]):  # excluding the first element of the row, which is the project name
                    table_rows.append(hours_row)
                    total_hours_row     = sum(filter(lambda x: x != "-", hours_row[1:]))
                    total_hours_row_str = "{:04.1f}".format(total_hours_row)
                    # FIXME: set n_week correctly
                    percent_str         = "{:04.1f}".format(total_hours_row/TOTAL_WORKING_HOURS_EACH_WEEK[n_week]*100)
                    notes_row[0]        = "||"+"".join(ascii_bar(
                                                total_hours_row,
                                                TOTAL_WORKING_HOURS_EACH_WEEK[n_week],
                                                max(max_num_chars_project_name, num_chars_hours)
                                            ))+"||"
                    table_rows.append(notes_row)
                    table_rows.append([f"└-{total_hours_row_str} h ({percent_str} %)"+" "*(max_num_chars_project_name-num_chars_hours)+"-┘"])

            # Print the table:
            print(f"Week nº{n_week} ({TOTAL_WORKING_HOURS_EACH_WEEK[n_week]} working hours):")
            print(tabulate(table_rows, headers=['Project'] + [str(date) for date in contemplated_weeks[week][0]], numalign='right'),"\n")

    # Visualize the weeks graphically:
    if input("Generate graph? [y/N] ").lower().startswith("y"):
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mtick
        import json

        projects             = sort_projects(hours_per_project, COLORS_CONFIG_FILE)
        project_data         = [
            [hours_per_project[project][date]['hours'] for date in contemplated_dates] for project in projects
        ]

        project_data_percent = [
            [100*sum(project_hours[i:i+5])/TOTAL_WORKING_HOURS_EACH_WEEK[n_week] for i in range(0,len(project_hours),5)] for project_hours in project_data
        ]
        contemplated_mondays = [date for date in contemplated_dates if date.weekday() == 0]
        bottom               = [0] * len(contemplated_mondays)
        colors               = load_colors_config(COLORS_CONFIG_FILE)

        plt.figure(figsize=(25, 6))
        for p in range(len(projects)):
            plt.bar(contemplated_mondays, project_data_percent[p],
                    width=5, bottom=bottom, label=projects[p], color=colors.get(projects[p]),
                    edgecolor='black' if projects[p] == 'VACACIONES (23-0004)' else None, linewidth=0.2 if projects[p] == 'VACACIONES (23-0004)' else None
            )
            # Stack the bars so each week sums up to 100%:
            bottom = [bottom[s] + project_data_percent[p][s] for s in range(len(contemplated_mondays))]
        plt.legend(bbox_to_anchor=(-0.15, 1.0), loc='upper left')
        plt.xlabel("Date")
        plt.grid(axis='y', which='major')
        plt.minorticks_on()
        plt.grid(axis='y', which='minor', linewidth='0.8', linestyle=':')
        plt.ylim([0, 100])
        plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())
        plt.ylabel("% Hours")
        plt.tight_layout(pad=2.5)
        first_week_num, first_week_year = contemplated_dates[0].isocalendar()[1],  contemplated_dates[0].isocalendar()[0]
        last_week_num,  last_week_year  = contemplated_dates[-1].isocalendar()[1], contemplated_dates[-1].isocalendar()[0]
        plt.title(f"Worked hours per project between week #{first_week_num} of {first_week_year} and week #{last_week_num} of {last_week_year}")

        filename = f"TAW - Worked hours per project from {contemplated_dates[0]} to {contemplated_dates[-1]}.png"
        plt.savefig(filename)
        print(f'Graph saved in file: "{filename}"')
