FROM python:3.11-slim

WORKDIR /app
ARG SERVICE_NAME=ai_server
ENV SERVICE_NAME=${SERVICE_NAME}

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG http_proxy
ARG https_proxy
ARG NO_PROXY
ARG no_proxy

ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY
ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV NO_PROXY=$NO_PROXY
ENV no_proxy=$no_proxy

COPY requirements.txt .
RUN if [ "$SERVICE_NAME" = "ai_server" ]; then \
    apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*; \
    fi

COPY UpdateAgent.py ModelConnector.py RootcauseAnalyser.py DetailedAnalyser.py RecoveryPlanner.py ./
COPY prompts/ ./prompts/
COPY errorconfig.aidl .
COPY PackageGenerator.py .

EXPOSE 9000
EXPOSE 9001

ENV PYTHONUNBUFFERED=1

CMD if [ "$SERVICE_NAME" = "pkg_gen" ]; then \
        python3 -u PackageGenerator.py; \
    else \
        python3 -u UpdateAgent.py; \
    fi
