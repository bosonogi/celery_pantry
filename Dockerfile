FROM python:3.6

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/opt/pantry"
WORKDIR /opt/pantry

COPY requirements-example.txt /opt/pantry/requirements.txt

RUN pip install -r requirements.txt --no-cache-dir

COPY example_tasks.py /opt/pantry/
COPY example_project /opt/pantry/example_project
COPY manage-example.py /opt/pantry/manage.py
COPY celery_pantry /opt/pantry/celery_pantry
