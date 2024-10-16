FROM python:3.13.0-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt

RUN python3.13 -m venv /python-docker/venv

RUN /python-docker/venv/bin/pip install -r requirements.txt

COPY . .

ENV GIT_PYTHON_REFRESH=quiet

CMD ["/python-docker/venv/bin/gunicorn", "-c", "conf/gunicorn_conf.py"]