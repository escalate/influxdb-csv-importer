FROM python:3.6-alpine

LABEL maintainer="Felix Boerner <ich@felix-boerner.de>"

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt
COPY . /app/
WORKDIR /app

ENTRYPOINT ["/app/csvimporter.py"]
CMD ["--help"]
