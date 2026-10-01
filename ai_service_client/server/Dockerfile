FROM python:3.11-slim

WORKDIR /app

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG http_proxy
ARG https_proxy
ARG NO_PROXY
ARG no_proxy

COPY requirements.txt .
RUN HTTP_PROXY=${HTTP_PROXY} \
	HTTPS_PROXY=${HTTPS_PROXY} \
	http_proxy=${http_proxy} \
	https_proxy=${https_proxy} \
	NO_PROXY=${NO_PROXY} \
	no_proxy=${no_proxy} \
	pip install --no-cache-dir -r requirements.txt

COPY UpdateAgent.py ModelConnector.py RootcauseAnalyser.py DetailedAnalyser.py RecoveryPlanner.py ./
COPY prompts/ ./prompts/
COPY errorconfig.aidl .
COPY error_enum_next_steps.md .
COPY recovery_plan.md .

EXPOSE 9000

ENV PYTHONUNBUFFERED=1

CMD ["python3", "-u", "UpdateAgent.py"]
