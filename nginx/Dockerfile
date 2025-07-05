# nginx/Dockerfile

# Start from the official lightweight Nginx image
FROM nginx:1.23-alpine

# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom production configuration into the image
COPY prod.conf /etc/nginx/conf.d/default.conf

# Copy our built Nuxt frontend files into the image's web root
COPY ../frontend_static /usr/share/nginx/html
