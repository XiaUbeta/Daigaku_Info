# Stage 1: Build the React/Vite application
FROM node:22-alpine AS builder

WORKDIR /app

# Enable pnpm
RUN corepack enable

# Copy package management files first for caching
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy the rest of the application code
COPY . .

# Pass backend URL at build time if needed (Vite uses VITE_ prefix)
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Build the project
RUN pnpm build

# Stage 2: Serve the built app with Nginx
FROM nginx:alpine

# Add Nginx configuration for client-side routing (React Router fallback)
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Optional: proxy /api requests directly to the backend service \
    location /api/ { \
        proxy_pass http://api:8000/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
