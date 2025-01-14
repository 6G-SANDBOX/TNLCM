FROM python:3.13.1-slim

ENV GIT_PYTHON_REFRESH=quiet

ENV TNLCM_FOLDER="/python-docker"

ENV POETRY_FOLDER="/opt/poetry"

ENV POETRY_BIN="/opt/poetry/bin/poetry"

RUN apt update && apt install -y curl

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_FOLDER} python3 -

RUN ${POETRY_BIN} config virtualenvs.in-project true

WORKDIR ${TNLCM_FOLDER}

COPY . .

RUN ${POETRY_BIN} install --no-root

CMD ["/opt/poetry/bin/poetry", "run", "gunicorn", "-c", "conf/gunicorn_conf.py"]