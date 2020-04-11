############# base stage ######################
FROM python:3.7-slim as base

COPY src/requirements/* /

RUN pip install -r /prod.txt

EXPOSE 8080

WORKDIR /app

############# dev stage ########################
FROM base as dev

ENV FLASK_ENV development

RUN pip install -r /dev.txt

VOLUME /app

############## testing stage ####################
FROM dev as testing

COPY src /app

CMD ./run_tests.sh

############## prod stage #######################
FROM base as prod

COPY src /app

ENV FLASK_ENV production

CMD ["python", "server.py"]


