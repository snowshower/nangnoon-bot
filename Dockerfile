FROM python:3.13.6

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install

COPY . .

CMD ["python", "nangnoon.py"]