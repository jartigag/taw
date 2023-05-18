#!/bin/sh
pipenv run ./TAW.py $(seq -s, -38 -26); xdg-open *$(sudo date -s '2023-06-23' 1>/dev/null; date -d 'friday 26 weeks ago' +%Y-%m-%d).png
pipenv run ./TAW.py $(seq -s, -25 -13); xdg-open *$(sudo date -s '2023-06-23' 1>/dev/null; date -d 'friday 13 weeks ago' +%Y-%m-%d).png
pipenv run ./TAW.py $(seq -s, -12   0); xdg-open *$(sudo date -s '2023-06-23' 1>/dev/null; date -d 'friday  0 weeks ago' +%Y-%m-%d).png
