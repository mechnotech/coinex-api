FROM python:3.10.0-slim-buster
LABEL name='CoinEx Pair Trader' version=1
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requierments.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
COPY ./ /code
ENTRYPOINT ["python3", "trades.py"]