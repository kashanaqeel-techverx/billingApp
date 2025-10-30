FROM python:3.10-slim

ENV GOOGLE_CLOUD_PROJECT="sacred-portal-452319-e2"
ENV GOOGLE_CLOUD_REGION="us-central1"
WORKDIR /app

COPY app.py /app/app.py
COPY setup.sh /app/setup.sh
COPY requirements.txt /app/requirements.txt

RUN apt-get update && \
    apt-get install -y curl bash && \
    bash setup.sh

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.port=8080"]
