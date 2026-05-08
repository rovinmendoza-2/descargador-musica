# Usamos una imagen oficial de Python ligera
FROM python:3.11-slim

# Instalamos ffmpeg, que es necesario para yt-dlp
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo en el contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos y los instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código del proyecto al contenedor
COPY . .

# Exponemos el puerto que usará Gunicorn
EXPOSE 10000

# Comando para ejecutar la aplicación con Gunicorn (servidor de producción)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "app:app"]
