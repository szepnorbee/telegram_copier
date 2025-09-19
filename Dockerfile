# Alap kép: Python 3.11 slim-bullseye
FROM python:3.11-slim-bullseye

# Munkakönyvtár beállítása a konténerben
WORKDIR /app

# Függőségek másolása és telepítése
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Az alkalmazás fájljainak másolása
COPY . .

# Port expozálása
EXPOSE 5000

# A Flask alkalmazás futtatása
CMD ["python3.11", "app.py"]
