FROM python:3.10-slim

WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y gcc libgl1-mesa-glx
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "Home.py", "--server.address=0.0.0.0", "--server.port=8501"]