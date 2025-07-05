# This is the final, bulletproof Dockerfile for your Nginx service.

# Start from the official lightweight Nginx image.
FROM nginx:1.23-alpine

# Copy our built Nuxt frontend files into the image's web root.
COPY frontend_static /usr/share/nginx/html

# Remove the default Nginx configuration files to prevent conflicts.
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom production configuration.
COPY nginx/prod.conf /etc/nginx/conf.d/default.conf

# --- THIS IS THE CRITICAL FIX ---
# Change the ownership of all web root files to the 'nginx' user.
# The Nginx process runs as this user, so this guarantees it has permission.
RUN chown -R nginx:nginx /usr/share/nginx/html

# For good measure, also ensure the files are world-readable.
RUN chmod -R 755 /usr/share/nginx/html