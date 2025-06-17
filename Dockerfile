FROM python:3.12

WORKDIR /app

COPY api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]