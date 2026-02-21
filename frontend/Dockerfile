# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
# Clean install to ensure reproducible builds
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

RUN echo 'server { \
    listen 80; \
    location /api/ { \
    proxy_pass http://backend:8000; \
    proxy_set_header Host $host; \
    proxy_set_header X-Real-IP $remote_addr; \
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
    proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    location / { \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    try_files $uri $uri/ /index.html; \
    } \
    }' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
