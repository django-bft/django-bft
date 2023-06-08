# Use a base Nginx image
FROM nginx:latest

# Install Certbot and other dependencies
RUN apt-get update && apt-get install -y certbot python3-certbot-nginx

# # Remove default Nginx configuration
# RUN rm /etc/nginx/conf.d/default.conf

# # Copy your Nginx configuration file
# COPY nginx.conf /etc/nginx/conf.d/nginx.conf

# # Expose ports 80 and 443
# EXPOSE 80 443

# # Start Nginx
# CMD ["nginx", "-g", "daemon off;"]