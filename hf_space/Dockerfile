# SAGE Hugging Face Space Multi-Stage Dockerfile
# Stage 1: Build Next.js Dashboard Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/sage/dashboard_frontend

COPY sage/dashboard_frontend/package*.json ./
RUN npm ci || npm install

COPY sage/dashboard_frontend ./
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# Stage 2: Unified Production Runner (Python 3.11 + Node 20 runtime)
FROM python:3.11-slim
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=7860
ENV NODE_ENV=production

# Install Node.js 20 and system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates netcat-traditional && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY hf_space/requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code and benchmark data
COPY pyproject.toml /app/
COPY sage /app/sage
COPY sage_live /app/sage_live
COPY tasks /app/tasks
COPY configs /app/configs
COPY experiments /app/experiments

# Copy built frontend application
COPY --from=frontend-builder /app/sage/dashboard_frontend /app/sage/dashboard_frontend

# Copy startup entrypoint script
COPY hf_space/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Hugging Face Spaces standard port
EXPOSE 7860

CMD ["/app/start.sh"]
