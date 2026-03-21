FROM python:3.12-slim

WORKDIR /opt/groundup-hub

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

ENV GROUNDUP_DATA_DIR=/data \
    GROUNDUP_MOCK_SERIAL=1 \
    GROUNDUP_HMAC_SECRET=dev-secret-change-me \
    GROUNDUP_GS1_BASE_URL=https://groundup.bio

VOLUME /data

EXPOSE 8420

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8420"]
