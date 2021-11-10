FROM python:3.8-slim

ARG STORAGEACCOUNT
ENV AZURE_STORAGE_CONNECTION_ACCOUNT=$STORAGEACCOUNT

COPY . /app
WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

EXPOSE 80
RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
RUN cp credentials.toml ~/.streamlit/credentials.toml

WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["src/app.py"]