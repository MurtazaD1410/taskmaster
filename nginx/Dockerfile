FROM nginx:1.23-alpine

RUN rm /etc/nginx/conf.d/default.conf

# This path is now relative to the project root, which is the context.
COPY nginx/prod.conf /etc/nginx/conf.d/default.conf

# --- THIS IS THE FIX ---
# This path is also relative to the project root.
COPY frontend_static /usr/share/nginx/html