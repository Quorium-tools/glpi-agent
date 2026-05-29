FROM python:3.12-slim

WORKDIR /app

COPY . /app/departments-support-agent

RUN pip install --no-cache-dir uv

ENV PYTHONUNBUFFERED=1
ENV GLPI_AGENT_HOST=0.0.0.0
ENV GLPI_AGENT_PORT=8005

EXPOSE 8005

CMD ["sh", "-c", "cd /app/departments-support-agent && uv run app.py"]
