# T.A.W.

**T**ime **A**t **W**eek

## What does it do?

> This Python script calculates the hours worked in a given period.
> 
> The user can choose how many weeks to review, and the program calculates the hours worked for each project during each week on workdays. The worked hours are stored in text files in YAML format located in subdirectories within a main folder called "taw". The text files store information about the hours worked on each day, separated by project.
> 
> The program uses the "tabulate" library to generate a table with summarized data. It also includes auxiliary functions to process the worked hours and create an ASCII bar chart to visually represent the worked hours.[^1]

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
# └=========================================================┘
```

## Example

```shell
$ pipenv run ./TAW.py $(seq -s, -18 0)
```