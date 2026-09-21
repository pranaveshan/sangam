# SANGAM — single-service production image (API + built React UI)
FROM node:20-alpine AS frontend
WORKDIR /fe
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ .
ENV VITE_API_URL=
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=frontend /fe/dist ./static
ENV DATABASE_URL=sqlite:///./sangam.db
ENV UPLOAD_DIR=./uploads
ENV CORS_ORIGINS=*
ENV DATA_MODE=prototype
EXPOSE 8100
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
