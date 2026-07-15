FROM python:3.11.9

# List packages here
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        file        \
        gcc         \
        libwww-perl && \
    apt-get autoremove -y && \
    apt-get clean

RUN apt-get install python3-dev -y

# Upgrade pip
RUN pip install --upgrade pip

WORKDIR /app/src/
ADD requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src .

ENV TZ=Asia/Tehran
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app/src/host
CMD ["python3", "app.py"]
