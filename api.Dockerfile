FROM python:3.9

WORKDIR /code

COPY pyproject.toml /code

COPY ./src /code/app
COPY ./resources /code/resources

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]