# Python runtime
FROM jupyter/scipy-notebook

RUN pip install --upgrade pip

RUN pip install datascience

# ARG NB_USER="jovyan"
# COPY RollingDice.ipynb /home/$NB_USER/work/

