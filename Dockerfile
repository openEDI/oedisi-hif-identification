FROM python:3.12.1-slim-bullseye
#USER root
RUN apt-get update && apt-get install -y git ssh

RUN mkdir -p /root/.ssh


WORKDIR /simulation

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ["High Impedance Fault Localization.py", "."]
COPY IEEE123_PV_L1C1B5HIF.csv .
COPY IEEE123_PV_L1C1B34HIF.csv .
COPY IEEE123_PV_L1C1B45HIF.csv .

ENTRYPOINT ["python", "High Impedance Fault Localization.py"]

