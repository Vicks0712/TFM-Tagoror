# Usa una imagen oficial de Python
FROM python:3.10

# Instala dependencias del sistema necesarias para OpenCV y FFmpeg
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    ffmpeg && \
    apt-get clean

# Define el directorio de trabajo
WORKDIR /ui

# Copia los archivos de la aplicación
COPY ui/ /ui/

# Copia el archivo de configuración de Streamlit
COPY ui/.streamlit /root/.streamlit

# Copia el archivo de requisitos desde la raíz del proyecto
COPY docker/ui/requirements.txt /requirements.txt

# Instala dependencias
RUN pip install -r /requirements.txt

# Expone el puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar la app con la configuración correcta
CMD ["streamlit", "run", "/ui/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
