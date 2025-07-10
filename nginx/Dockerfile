# --- Stage 1: Build the Vue.js frontend ---
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY ./taskmaster-app/package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY ./taskmaster-app/ ./
RUN npm run build


# --- Stage 2: Create the final Nginx image ---
FROM nginx:stable-alpine

# Copy the built Vue app from the 'builder' stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy our custom Nginx configuration
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]