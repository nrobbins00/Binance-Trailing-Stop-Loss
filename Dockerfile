#FROM python:3.9.6-alpine
FROM alpine:latest
WORKDIR /app
RUN apk add py-cryptography py3-pip gcc musl-dev libffi-dev openssl-dev python3-dev && \
pip3 install ccxt
ADD config.py /app
ADD . /app
ENTRYPOINT ["/app/main.py"]
