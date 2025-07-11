# --- Stage 1: Build the Vue.js frontend ---
FROM node:20-alpine AS builder

WORKDIR /app

# --- THIS IS THE CORRECTED SECTION ---
# Use 'apk' (the Alpine package manager) to install build tools.
# 'build-base' is the Alpine equivalent of 'build-essential'.
RUN apk add --no-cache python3 build-base

# Copy package files and install dependencies
COPY ./taskmaster-app/package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY ./taskmaster-app/ ./
RUN npm run generate


# --- Stage 2: Create the final Nginx image ---
FROM nginx:stable-alpine

# Copy the built Vue app from the 'builder' stage
# COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/.output/public /usr/share/nginx/html

# Copy our custom Nginx configuration
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]