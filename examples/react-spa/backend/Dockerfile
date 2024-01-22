FROM python:3.12

WORKDIR /code/
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY manage.py .
COPY ./backend ./backend/
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
