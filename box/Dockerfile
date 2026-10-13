FROM python:3.12-slim
WORKDIR /app
RUN useradd --system --no-create-home box
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
USER box
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:5000/')"
CMD ["python","app.py"]
