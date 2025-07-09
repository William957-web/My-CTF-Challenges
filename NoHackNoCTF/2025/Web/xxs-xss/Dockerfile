FROM python:3.11
RUN pip3 install --upgrade pip
RUN pip3 install flask
RUN apt-get update
RUN apt-get install chromium -y
WORKDIR /app
COPY . /app
RUN rm /app/Dockerfile
ENTRYPOINT [ "python3" ]
CMD ["app.py" ]
