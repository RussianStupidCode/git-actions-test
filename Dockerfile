FROM python:3.8

COPY ./django-test ./app
RUN pip install -r /app/requirements-dev.txt

WORKDIR /app

CMD ["gunicorn", "django-test:app"]