# Python runtime
FROM jupyter/scipy-notebook

RUN pip install --upgrade pip

RUN pip install datascience

ARG NB_USER="jovyan"
COPY Covid19-Worldwide.ipynb /home/$NB_USER/work/
COPY timetable.py /home/$NB_USER/work/
