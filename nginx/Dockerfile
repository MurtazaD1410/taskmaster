# # --- Stage 1: Build the Vue.js frontend ---
# # FROM node:20-bookworm AS builder
# FROM --platform=linux/amd64 node:20-bookworm AS builder

# # It's still good practice to include build tools.
# RUN apt-get update && apt-get install -y build-essential python3 && rm -rf /var/lib/apt/lists/*
# WORKDIR /app

# # Copy package files and install dependencies
# COPY ./taskmaster-app/package*.json ./
# # RUN npm install
# RUN npm install --ignore-scripts
# # Copy the rest of the frontend source code
# COPY ./taskmaster-app/ ./
# RUN npm run build


# # --- Stage 2: Create the final Nginx image ---
# FROM nginx:stable-alpine

# # Copy the built Vue app from the 'builder' stage
# COPY --from=builder /app/dist /usr/share/nginx/html

# # Copy our custom Nginx configuration
# COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# # Expose port 80
# EXPOSE 80

# # Start Nginx
# CMD ["nginx", "-g", "daemon off;"]

FROM nginx:stable-alpine

# Remove the default Nginx welcome page.
RUN rm /usr/share/nginx/html/*

# Copy the PRE-BUILT assets from your local .output/public directory
# into the Nginx web root.
# The path is relative to the `context` defined in your docker-compose file.
COPY ./taskmaster-app/.output/public /usr/share/nginx/html

# Copy your custom Nginx configuration file.
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (standard for web servers).
EXPOSE 80
