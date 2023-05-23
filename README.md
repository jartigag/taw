# T.A.W.

**T**ime **A**t **W**eek

## What does it do?

##### v1.0
> This Python script calculates the hours worked in a given period.
> 
> The user can choose how many weeks to review, and the program calculates the hours worked for each project during each week on workdays. The worked hours are stored in text files in YAML format located in subdirectories within a main folder called "taw". The text files store information about the hours worked on each day, separated by project.
> 
> The program uses the "tabulate" library to generate a table with summarized data. It also includes auxiliary functions to process the worked hours and create an ASCII bar chart to visually represent the worked hours.[^1]

##### v1.1
> After the table is printed, if you press "y" the script generates a graph showing the distribution of worked hours per project over the specified weeks period.[^1]

[^1]: Description generated with ChatGPT

## Installation

```python
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
```
```python
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
```

## Examples

```shell
$ pipenv run ./TAW.py $(seq -s, 1 19)
#                                        if executed at week #19 of the year, it is equivalent to
#                                        $ pipenv run ./TAW.py $(seq -s, -19 0)
#                                        and also to
#                                        $ pipenv run ./TAW.py $(seq -s, 1 $(date +%U))
Week nº1 (41 working hours):
Project                   2023-01-02    2023-01-03    2023-01-04    2023-01-05        2023-01-06
------------------------  ------------  ------------  ------------  ----------------  ------------
┌-HOLIDAYS   (23-0004)-┐  8.5           8.5           -             -                 7.0
||.███.███.██▋.   .   ||  holidays      holidays                                      p.holiday
└-24.0 h (58.5 %)     -┘
┌-CLI1                -┐  -             -             -             2.5               -
||.▏  .   .   .   .   ||                                            scrum
└-02.5 h (06.1 %)     -┘
┌-CLI6                -┐  -             -             8.5           -                 -
||.███.   .   .   .   ||                              review
                                                      report
└-08.5 h (20.7 %)     -┘
┌-OP2                 -┐  -             -             -             4.0               -
||.▉  .   .   .   .   ||                                            finish offer
└-04.0 h (09.8 %)     -┘
┌-PROJINT 1           -┐  -             -             -             2.0               -
||.   .   .   .   .   ||                                            internal tests
└-02.0 h (04.9 %)     -┘

[..]

Project                   2023-05-08    2023-05-09        2023-05-10    2023-05-11    2023-05-12
------------------------  ------------  ----------------  ------------  ------------  ------------
┌-CLI1                -┐  1.0           3.0               1.5           1.0           0.5
||.██▍.   .   .   .   ||  test          test. meet cust   test          test          test
└-07.0 h (17.1 %)     -┘

Generate graph? [y/N] y
Graph saved in file: "TAW - Worked hours per project from 2023-01-02 to 2023-05-12.png"
```

![](plots/TAW&#32;-&#32;2023&#32;-&#32;Worked&#32;hours&#32;per&#32;project&#32;from&#32;2023-01-02&#32;to&#32;2023-05-12.png)


```shell
$ yes | ./demo_scripts/gen_graphs_in_rows_of_13_bars.sh >/dev/null 2>&1
```

![](plots/TAW&#32;-&#32;Worked&#32;hours&#32;per&#32;project&#32;from&#32;2022-09-26&#32;to&#32;2022-12-23.png)
![](plots/TAW&#32;-&#32;Worked&#32;hours&#32;per&#32;project&#32;from&#32;2022-12-26&#32;to&#32;2023-03-24.png)
![](plots/TAW&#32;-&#32;Worked&#32;hours&#32;per&#32;project&#32;from&#32;2023-03-27&#32;to&#32;2023-06-23.png)
