FROM python:3.11 AS base

# Derived from (Apache License 2.0): 
# https://github.com/OpenCS-ontology/ci-worker/blob/496b15d734ac77ad51ec28fed831a4bb82c2bc90/Dockerfile

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy


FROM base AS runtime

# Install Eclipse Temurin
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget apt-transport-https && \
    mkdir -p /etc/apt/keyrings && \
    wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | tee /etc/apt/keyrings/adoptium.asc && \
    echo "deb [signed-by=/etc/apt/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends temurin-17-jdk

WORKDIR /app

# Download robot.jar
RUN wget https://github.com/ontodev/robot/releases/download/v1.9.7/robot.jar

# Install jelly-cli
RUN bash -c "$(curl -sSfL https://w3id.org/jelly/setup-cli.sh)"

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install application into container
COPY . .

ENTRYPOINT []
