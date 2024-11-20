FROM python:3.10-slim

ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service-account.json"
ENV GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
ENV GOOGLE_CLOUD_REGION="your-region""
WORKDIR /app

COPY app.py /app/app.py
COPY setup.sh /app/setup.sh
COPY requirements.txt /app/requirements.txt
COPY service-account.json /app/service-account.json # Placeholder for the service account file

RUN apt-get update && \
    apt-get install -y curl bash && \
    bash setup.sh

EXPOSE 8080

CMD ["streamlit", "run", "app.py", "--server.enableCORS=false", "--server.enableXsrfProtection=false", "--server.port=8080"]
