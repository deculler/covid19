# Python runtime
FROM jupyter/scipy-notebook

RUN pip install --upgrade pip

RUN pip install datascience

ARG NB_USER="jovyan"
COPY World-covid19-JHU.ipynb /home/$NB_USER/work/
COPY US-covid19-JHU.ipynb /home/$NB_USER/work/
COPY US-County-covid19-JHU.ipynb /home/$NB_USER/work/
COPY timetable.py /home/$NB_USER/work/
