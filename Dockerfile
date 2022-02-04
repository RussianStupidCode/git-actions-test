FROM python:3.8

COPY ./django-test ./app
RUN pip istanll -r /app/requirements-dev.txt

WORKDIR /app

CMD ["gunicron", "django-test:app"]