FROM python:3.9
# FROM python:slim 
WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# CMD ["python3", "/app/new_main.py"]
CMD ["python3","-u", "/app/main.py"]



