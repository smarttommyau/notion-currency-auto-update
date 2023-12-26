FROM alpine:3.18

WORKDIR /app
COPY notion/ ./notion/ 
COPY *.py .
COPY requirements_full.txt .
RUN echo "Install Python" && \
    apk add --no-cache \
            python3 \
            py3-pip && \
    python3 -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_full.txt

CMD ["python3", "-u", "main.py"]
