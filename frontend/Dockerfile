# Use a lightweight Nginx image
FROM nginx:alpine

# Copy frontend files into Nginx's web directory
COPY frontend/ /usr/share/nginx/html/

# Replace the default Nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80