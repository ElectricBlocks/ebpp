FROM python:3.8-slim-buster
WORKDIR /ebpp
COPY requirements.txt /ebpp
RUN pip install -r requirements.txt
COPY . /ebpp
ENTRYPOINT [ "python", "ebpp.py" ]
EXPOSE 1127