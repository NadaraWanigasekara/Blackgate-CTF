FROM python:3.12-slim
WORKDIR /app
RUN useradd --system --no-create-home app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER app
EXPOSE 8090
CMD ["python", "app.py"]
