# T.A.W.

**T**ime **A**t **W**eek

## ¿Qué hace?

> Este script de Python calcula las horas trabajadas en un periodo determinado.
> 
> El usuario puede elegir cuántas semanas se quieren revisar, y el programa calcula las horas trabajadas durante cada semana en días laborables, para cada proyecto registrado. Las horas trabajadas se encuentran registradas en archivos de texto en formato YAML, ubicados en subdirectorios dentro de una carpeta principal llamada "taw". En los archivos de texto se almacena información sobre las horas trabajadas en cada día, separadas por proyecto.
> 
> El programa utiliza la librería "tabulate" para generar una tabla con los datos resumidos. También se incluyen funciones auxiliares para procesar las horas trabajadas y crear una barra gráfica ASCII para representar visualmente las horas trabajadas.[^1]

[^1]: Descripción generada con ChatGPT

## Instalación

```
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
```
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
