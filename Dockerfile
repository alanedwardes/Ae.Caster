FROM python:3.9
WORKDIR /app
ADD . /app
RUN pip install -r requirements.py
ENTRYPOINT ["python3"]
CMD ["app.py"]
