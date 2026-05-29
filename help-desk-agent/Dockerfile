FROM python:3.12-slim

WORKDIR /app

COPY . /app/help-desk-agent

RUN pip install --no-cache-dir uv

ENV PYTHONUNBUFFERED=1
ENV GLPI_AGENT_HOST=0.0.0.0
ENV GLPI_AGENT_PORT=8004

EXPOSE 8004

CMD ["sh", "-c", "cd /app/help-desk-agent && uv run app.py"]
