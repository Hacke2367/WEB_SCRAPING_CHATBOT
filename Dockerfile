#FROM python:3.10-slim-buster
#WORKDIR /app
#
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
#COPY requirements.txt
#
#RUN pip install --no-cache-dir -r requirements.txt \
#    && playwright install --with-deps chromium \
#    && rm -rf /var/lib/apt/lists/*
#
#COPY scr/ /app/src
#
#EXPOSE 8000
#
#CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]


## IGNORE